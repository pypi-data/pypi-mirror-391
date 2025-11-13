"""Google GenAI span parser for OpenInference traces."""

import json
import logging
from typing import Optional, Union

from opentelemetry.trace import Span

from .base import BaseSpanParser
from .common import (
    OPENINFERENCE_SPAN_KIND,
    LLM_PROVIDER,
    GOOGLE_PROVIDER,
    LLM_SPAN_KIND,
    TEXT_MESSAGE_TYPE,
    TOOL_CALL_MESSAGE_TYPE,
    ASSISTANT_ROLE,
    USER_ROLE,
    SYSTEM_ROLE,
    UNKNOWN_DEFAULT,
    NULL_VALUES,
    ROLE_FIELD,
    CONTENT_FIELD,
    TYPE_FIELD,
    NAME_FIELD,
    ID_FIELD,
    DESCRIPTION_FIELD,
    PARAMETERS_FIELD,
)
from ...models.api_types import (
    LLMInput,
    LLMInteraction,
    LLMOutput,
    LLMToolDefinition,
    LLMToolCall,
    LLMToolResponse,
)
from ...models.openinference import OpenInferenceSpanData

logger = logging.getLogger(__name__)


class GoogleGenAISpanParser(BaseSpanParser):
    """Parser for Google GenAI spans captured by OpenInference."""

    def __init__(self):
        super().__init__(name="GoogleGenAI")

    def can_parse(self, span: Span) -> bool:
        """Check if this is a Google GenAI LLM span."""
        if not hasattr(span, "attributes") or span.attributes is None:
            return False

        attrs = span.attributes
        return (
            attrs.get(OPENINFERENCE_SPAN_KIND) == LLM_SPAN_KIND
            and attrs.get(LLM_PROVIDER) == GOOGLE_PROVIDER
        )

    def parse(self, span: Span) -> Optional[LLMInteraction]:
        """Parse Google GenAI span into LLMInteraction."""
        try:
            if not hasattr(span, "attributes") or span.attributes is None:
                return None

            attrs = span.attributes

            # Check if this is google-genai format (uses indexed attributes)
            # vs older format (uses input.value/output.value JSON)
            has_indexed_messages = any(
                key.startswith("llm.input_messages.")
                or key.startswith("llm.output_messages.")
                for key in attrs.keys()
            )

            if has_indexed_messages:
                return self._parse_indexed_format(attrs)
            else:
                return self._parse_json_format(attrs)

        except Exception as e:
            logger.error(f"Error parsing Google GenAI data: {e}", exc_info=True)
            return None

    def _parse_json_format(self, attrs: dict) -> Optional[LLMInteraction]:
        """Parse older format using input.value and output.value JSON."""
        try:
            span_data = OpenInferenceSpanData.from_span_attributes(attrs)
            input_messages, output_messages, tools = [], [], []

            # Parse input data
            if span_data.input_value and span_data.input_value not in NULL_VALUES:
                input_data = json.loads(span_data.input_value)

                # Process system instructions
                if (
                    "system_instruction" in input_data
                    and input_data["system_instruction"]
                ):
                    system_inst = input_data["system_instruction"]
                    if isinstance(system_inst, dict):
                        parts = system_inst.get("parts", [])
                        system_text = self._extract_text_from_parts(parts)
                        if system_text:
                            input_messages.append(
                                LLMInput(
                                    role=SYSTEM_ROLE,
                                    content=system_text,
                                    type=TEXT_MESSAGE_TYPE,
                                )
                            )

                # Process contents (conversation messages)
                for content_item in input_data.get("contents", []):
                    role = content_item.get(ROLE_FIELD, UNKNOWN_DEFAULT)
                    parts = content_item.get("parts", [])

                    # Process parts to extract text, function calls, or function responses
                    processed_content = self._process_parts(parts, role)

                    if processed_content:
                        input_messages.append(
                            LLMInput(
                                role=role,
                                content=processed_content,
                                type=TEXT_MESSAGE_TYPE,
                            )
                        )

                # Extract tools
                if "tools" in input_data:
                    for tool in input_data["tools"]:
                        if isinstance(tool, dict) and "function_declarations" in tool:
                            for func_decl in tool["function_declarations"]:
                                tools.append(
                                    LLMToolDefinition(
                                        name=func_decl.get(NAME_FIELD, UNKNOWN_DEFAULT),
                                        description=func_decl.get(
                                            DESCRIPTION_FIELD, ""
                                        ),
                                        parameters=json.dumps(
                                            func_decl.get(PARAMETERS_FIELD, {})
                                        ),
                                    )
                                )

            # Parse output data
            if span_data.output_value and span_data.output_value not in NULL_VALUES:
                output_data = json.loads(span_data.output_value)

                # Process candidates
                for candidate in output_data.get("candidates", []):
                    if "content" in candidate:
                        content = candidate["content"]
                        parts = content.get("parts", [])

                        for part in parts:
                            if isinstance(part, dict):
                                # Handle text content
                                if "text" in part:
                                    output_messages.append(
                                        LLMOutput(
                                            content=part["text"],
                                            type=TEXT_MESSAGE_TYPE,
                                        )
                                    )

                                # Handle function calls (tool calls)
                                elif "function_call" in part:
                                    function_call = part["function_call"]
                                    output_messages.append(
                                        LLMOutput(
                                            content=LLMToolCall(
                                                id=function_call.get(ID_FIELD, ""),
                                                name=function_call.get(
                                                    NAME_FIELD, UNKNOWN_DEFAULT
                                                ),
                                                parameters=json.dumps(
                                                    function_call.get("args", {})
                                                ),
                                            ),
                                            type=TOOL_CALL_MESSAGE_TYPE,
                                        )
                                    )

            return LLMInteraction(
                input_messages=input_messages,
                output_messages=output_messages,
                tools_available=tools or None,
            )

        except Exception as e:
            logger.error(f"Error parsing Google GenAI JSON format: {e}", exc_info=True)
            return None

    def _parse_indexed_format(self, attrs: dict) -> Optional[LLMInteraction]:
        """Parse indexed format using indexed message attributes."""
        try:
            input_messages, output_messages, tools = [], [], []

            # Extract input messages from indexed attributes
            input_msg_indices = set()
            for key in attrs.keys():
                if key.startswith("llm.input_messages."):
                    parts = key.split(".")
                    if len(parts) >= 3 and parts[2].isdigit():
                        input_msg_indices.add(int(parts[2]))

            for idx in sorted(input_msg_indices):
                role = attrs.get(
                    f"llm.input_messages.{idx}.message.role", UNKNOWN_DEFAULT
                )
                content = attrs.get(f"llm.input_messages.{idx}.message.content", "")

                # Map 'model' role to 'assistant' for consistency
                if role == "model":
                    role = ASSISTANT_ROLE

                # Check if this input message has tool calls (assistant messages with tool calls)
                tool_call_indices = set()
                for key in attrs.keys():
                    prefix = f"llm.input_messages.{idx}.message.tool_calls."
                    if key.startswith(prefix):
                        parts = key.split(".")
                        if len(parts) >= 6 and parts[5].isdigit():
                            tool_call_indices.add(int(parts[5]))

                # If tool calls exist in input (from conversation history), create tool call messages
                if tool_call_indices:
                    for tc_idx in sorted(tool_call_indices):
                        tool_name = attrs.get(
                            f"llm.input_messages.{idx}.message.tool_calls.{tc_idx}.tool_call.function.name",
                            UNKNOWN_DEFAULT,
                        )
                        tool_args = attrs.get(
                            f"llm.input_messages.{idx}.message.tool_calls.{tc_idx}.tool_call.function.arguments",
                            "{}",
                        )
                        tool_id = attrs.get(
                            f"llm.input_messages.{idx}.message.tool_calls.{tc_idx}.tool_call.id",
                            "",
                        )

                        input_messages.append(
                            LLMInput(
                                role=role,
                                content=LLMToolCall(
                                    id=tool_id,
                                    name=tool_name,
                                    parameters=tool_args,
                                ),
                                type=TEXT_MESSAGE_TYPE,
                            )
                        )
                else:
                    # Regular text message
                    input_messages.append(
                        LLMInput(
                            role=role,
                            content=content,
                            type=TEXT_MESSAGE_TYPE,
                        )
                    )

            # Extract output messages from indexed attributes
            output_msg_indices = set()
            for key in attrs.keys():
                if key.startswith("llm.output_messages."):
                    parts = key.split(".")
                    if len(parts) >= 3 and parts[2].isdigit():
                        output_msg_indices.add(int(parts[2]))

            for idx in sorted(output_msg_indices):
                role = attrs.get(
                    f"llm.output_messages.{idx}.message.role", UNKNOWN_DEFAULT
                )
                content = attrs.get(f"llm.output_messages.{idx}.message.content", "")

                # Map 'model' role to 'assistant' for consistency
                if role == "model":
                    role = ASSISTANT_ROLE

                # Check if this output message has tool calls
                tool_call_indices = set()
                for key in attrs.keys():
                    prefix = f"llm.output_messages.{idx}.message.tool_calls."
                    if key.startswith(prefix):
                        parts = key.split(".")
                        if len(parts) >= 6 and parts[5].isdigit():
                            tool_call_indices.add(int(parts[5]))

                # If tool calls exist, create output messages for each tool call
                if tool_call_indices:
                    for tc_idx in sorted(tool_call_indices):
                        tool_name = attrs.get(
                            f"llm.output_messages.{idx}.message.tool_calls.{tc_idx}.tool_call.function.name",
                            UNKNOWN_DEFAULT,
                        )
                        tool_args = attrs.get(
                            f"llm.output_messages.{idx}.message.tool_calls.{tc_idx}.tool_call.function.arguments",
                            "{}",
                        )
                        tool_id = attrs.get(
                            f"llm.output_messages.{idx}.message.tool_calls.{tc_idx}.tool_call.id",
                            "",
                        )

                        output_messages.append(
                            LLMOutput(
                                content=LLMToolCall(
                                    id=tool_id,
                                    name=tool_name,
                                    parameters=tool_args,
                                ),
                                type=TOOL_CALL_MESSAGE_TYPE,
                            )
                        )
                elif (
                    content
                ):  # Only add text output if there's content and no tool calls
                    output_messages.append(
                        LLMOutput(
                            content=content,
                            type=TEXT_MESSAGE_TYPE,
                        )
                    )

            # Extract tools from indexed attributes
            tool_indices = set()
            for key in attrs.keys():
                if key.startswith("llm.tools."):
                    parts = key.split(".")
                    if len(parts) >= 3 and parts[2].isdigit():
                        tool_indices.add(int(parts[2]))

            for idx in sorted(tool_indices):
                tool_json = attrs.get(f"llm.tools.{idx}.tool.json_schema")
                if tool_json:
                    try:
                        tool_data = json.loads(tool_json)
                        tools.append(
                            LLMToolDefinition(
                                name=tool_data.get(NAME_FIELD, UNKNOWN_DEFAULT),
                                description=tool_data.get(DESCRIPTION_FIELD, ""),
                                parameters=json.dumps(
                                    tool_data.get(PARAMETERS_FIELD, {})
                                ),
                            )
                        )
                    except:
                        pass

            return LLMInteraction(
                input_messages=input_messages,
                output_messages=output_messages,
                tools_available=tools or None,
            )

        except Exception as e:
            logger.error(
                f"Error parsing Google GenAI indexed format: {e}", exc_info=True
            )
            return None

    def _extract_text_from_parts(self, parts: list) -> str:
        """Extract text content from a list of parts."""
        text_parts = []
        for part in parts:
            if isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])
        return " ".join(text_parts)

    def _process_parts(
        self, parts: list, role: str
    ) -> Union[str, LLMToolCall, LLMToolResponse]:
        """Process Google GenAI parts to extract content.

        Google GenAI parts can contain:
        - text: Simple text content
        - function_call: Tool/function call from assistant
        - function_response: Tool/function response from user
        """
        text_parts = []
        function_calls = []
        function_responses = []

        for part in parts:
            if isinstance(part, dict):
                # Extract text
                if "text" in part:
                    text_parts.append(part["text"])

                # Extract function calls (assistant making tool calls)
                elif "function_call" in part:
                    function_call = part["function_call"]
                    function_calls.append(
                        LLMToolCall(
                            id=function_call.get(ID_FIELD, ""),
                            name=function_call.get(NAME_FIELD, UNKNOWN_DEFAULT),
                            parameters=json.dumps(function_call.get("args", {})),
                        )
                    )

                # Extract function responses (user providing tool results)
                elif "function_response" in part:
                    function_response = part["function_response"]
                    response_data = function_response.get("response", {})
                    function_responses.append(
                        LLMToolResponse(
                            id="",  # Google GenAI doesn't provide ID for function responses
                            name=function_response.get(NAME_FIELD, ""),
                            response=json.dumps(response_data),
                        )
                    )

        # Return the appropriate content type based on what we found
        if function_calls:
            return function_calls[0]  # Return first tool call
        elif function_responses:
            return function_responses[0]  # Return first tool response
        else:
            return " ".join(text_parts)  # Return joined text
