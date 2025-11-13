import math
from typing import List, Optional, Union
from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .common_types import ModelClass, ModelCore, EvaluationTarget, criteria_starts


class LLMToolResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the tool call.")
    response: str = Field(..., description="Tool response")

    name: Optional[str] = Field(default=None, description="Tool name")

    model_config = ConfigDict(
        extra="allow",
    )


class LLMToolCall(BaseModel):
    id: str = Field(..., description="Unique identifier for the tool call.")
    name: str = Field(..., description="Tool name")
    parameters: str = Field(..., description="Tool parameters.")

    model_config = ConfigDict(
        extra="allow",
    )


class LLMToolDefinition(BaseModel):
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: str = Field(..., description="Tool parameters.")

    model_config = ConfigDict(
        extra="allow",
    )


class LLMInput(BaseModel):
    role: str = Field(
        ...,
        description="Role of the message sender (e.g., user, system, assistant, tool)",
    )
    type: Optional[str] = Field(
        default=None,
        description="Type of message (e.g., text, thinking_tokens, tool_call). This can be arbitrary but should be consistent within a trace.",
    )
    content: Union[str, LLMToolCall, LLMToolResponse] = Field(
        ..., description="Content of the LLM Input."
    )


class LLMOutput(BaseModel):
    type: Optional[str] = Field(
        default=None,
        description="Type of message (e.g., text, thinking_tokens, tool_call). This can be arbitrary but should be consistent within a trace.",
    )
    content: Union[str, LLMToolCall] = Field(..., description="Content of the message")


class LLMInteraction(BaseModel):
    input_messages: List[LLMInput] = Field(
        ...,
        description="List of input messages to the LLM invocation.",
    )
    output_messages: List[LLMOutput] = Field(
        ...,
        description="List of output messages from the LLM invocation.",
    )
    tools_available: Optional[List[LLMToolDefinition]] = Field(
        default=None,
        description="List of tools available to the agent in this interaction.",
    )


class AgentInstance(BaseModel):
    id: str = Field(..., description="Unique identifier for the agent instance.")
    name: str = Field(..., description="User defined name of the agent invoked.")
    interactions: List[Union[str, LLMInteraction]] = Field(
        ...,
        description="List of ordered LLM interactions or agent instance ids for this agent instance.",
    )


class MultiAgentTrace(BaseModel):
    root_agent_instance_id: str = Field(
        ...,
        description="User invoked Agent Instance ID. This is the root of the trace.",
    )
    agent_instance_by_id: dict[str, AgentInstance] = Field(
        ..., description="Mapping of ID to Agent Instance objects."
    )


class RequestBase(BaseModel):
    evaluation_criteria: str = Field(
        ...,
        description="Criteria used for evaluation. Begins with one of the following: "
        + ", ".join(criteria_starts["reward"] + criteria_starts["binary"]),
    )
    model_core: ModelCore = Field(
        default=ModelCore.ALIGN_20250529,
        description="The model core for reward evaluation. Defaults to align-20250503 if not specified.",
    )

    @field_validator("evaluation_criteria")
    @classmethod
    def check_evaluation_criteria_length(cls, evaluation_criteria):
        if len(evaluation_criteria) > 4096:
            raise ValueError("Evaluation criteria length cannot exceed 4k characters")
        return evaluation_criteria

    @field_validator("evaluation_criteria")
    @classmethod
    def evaluation_criteria_must_start_with_correct_prefix(cls, value):
        if not any(
            value.startswith(start)
            for start in criteria_starts["reward"] + criteria_starts["binary"]
        ):
            raise ValueError(
                "Evaluation criteria must start with one of the following: "
                + ", ".join(criteria_starts["reward"] + criteria_starts["binary"])
            )
        return value

    def is_binary_evaluation(self) -> bool:
        return any(
            self.evaluation_criteria.startswith(cs) for cs in criteria_starts["binary"]
        )


class RewardRequest(RequestBase):
    """
    Request model for reward score evaluation of LLM responses against specified criteria.
    """

    messages: List[dict] = Field(
        ..., description="A list of chat messages", min_length=2
    )
    system: Optional[str] = Field(
        None,
        description="System message is separate for Anthropic-style LLM calls. Optional.",
    )
    tools: Optional[List[dict]] = Field(
        None,
        description="List of tools available for the assistant to call. Optional.",
    )
    evaluate_latest: bool = Field(
        default=True,
        description="Whether to evaluate only the latest response or all responses.",
    )

    @model_validator(mode="after")
    def lightning_not_allowed_for_all_responses_evaluation(self):
        if (
            not self.evaluate_latest
            and self.model_core.model_class() == ModelClass.ALIGN_LIGHTNING
        ):
            raise ValueError(
                "Align Lightning model core not supported when evaluating all responses."
            )
        return self


class TraceRewardRequest(RequestBase):
    """
    Request model for a trace based evaluation of LLM responses against specified criteria.
    """

    trace: MultiAgentTrace = Field(
        ...,
        description="A Multi Agent Trace object representing the full trace of agent interactions.",
    )
    evaluate_latest: bool = Field(
        default=False,
        description="Whether to evaluate only the latest response or all responses.",
    )

    @field_validator("model_core")
    @classmethod
    def lightning_not_allowed_for_trace_evaluation(cls, value):
        if value.model_class() == ModelClass.ALIGN_LIGHTNING:
            raise ValueError(
                "Align Lightning model core not supported for trace evaluations."
            )
        return value

    @field_validator("evaluate_latest")
    @classmethod
    def evaluate_latest_must_be_false_for_trace_evaluation(cls, value):
        if value:
            raise ValueError("evaluate_latest must be false for trace evaluations.")
        return value

    @field_validator("trace")
    @classmethod
    def trace_must_have_llm_interactions(cls, body):
        ### Check if trace has any LLM interactions
        has_llm_interaction = False
        for agent_instance in body.agent_instance_by_id.values():
            for interaction in agent_instance.interactions:
                if isinstance(interaction, LLMInteraction):
                    has_llm_interaction = True
                    break
            if has_llm_interaction:
                break

        if not has_llm_interaction:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trace contains no LLM interactions. At least one agent instance must have an LLM interaction.",
            )
        return body


class RewardGPURequest(RewardRequest):
    """
    Request model for reward score evaluation of LLM responses against specified criteria,
    specifically for GPU-based evaluation.
    """

    explanation: str = Field(
        description="Explanation of the evaluation criteria. Optional.",
    )


class ScoreResponse(BaseModel):
    """
    Response model for evaluation scores.
    """

    score: Optional[float] = Field(
        None,
        description="Evaluation score between 0 and 1. If null, the criteria was deemed not applicable.",
    )
    explanation: str = Field(description="Explanation of the evaluation score")

    @field_validator("score")
    def validate_score(cls, value):
        if value is None:
            return value
        if math.isnan(value):
            return None
        if not 0 <= value <= 1:
            raise ValueError("Score must be between 0 and 1.")
        return value

    def get_rounded(self) -> "ScoreResponse":
        """
        Round the score to either 0 or 1 based on a threshold of 0.5.
        """
        if self.score is not None:
            self.score = 1.0 if self.score >= 0.5 else 0.0
        return self


class SummaryStatistics(BaseModel):
    median: Optional[float] = Field(default=None, description="Median score.")
    min: Optional[float] = Field(default=None, description="Minimum score.")
    max: Optional[float] = Field(default=None, description="Maximum score.")
    std: Optional[float] = Field(
        default=None, description="Standard deviation of scores."
    )


class AgentTraceResult(BaseModel):
    agent_name: str = Field(..., description="Name of the agent evaluated.")
    results_by_agent_instance_id: dict[str, Union[ScoreResponse, None]] = Field(
        ...,
        description="Mapping of Agent Instance ID to their respective Score Response, or None depending on criteria.",
    )
    summary_statistics: Optional[SummaryStatistics] = Field(
        default=None,
        description="Summary statistics for the agent's evaluations. Only applicable for reward evaluations.",
    )


class MultiAgentTraceResponse(BaseModel):
    """
    Response model for multi-agent trace evaluations.
    """

    request_id: str = Field(
        ..., description="Unique identifier for the evaluation request."
    )
    results_by_agent_name: dict[str, AgentTraceResult] = Field(
        ..., description="Mapping of Agent Name to their respective trace results."
    )

    def __str__(self) -> str:
        return self.model_dump_json(indent=2)

    def get_rounded(self) -> "MultiAgentTraceResponse":
        """
        Round all scores in the response to either 0 or 1 based on a threshold of 0.5.
        """
        for agent_trace_result in self.results_by_agent_name.values():
            for (
                agent_instance_id,
                score_response,
            ) in agent_trace_result.results_by_agent_instance_id.items():
                if score_response is not None and score_response.score is not None:
                    score_response.score = 1.0 if score_response.score >= 0.5 else 0.0

        return self
