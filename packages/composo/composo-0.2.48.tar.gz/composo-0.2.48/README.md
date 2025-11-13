# Composo Python SDK

Composo provides a Python SDK for evaluating LLM applications.

## Installation

```bash
pip install composo
```

## Quick Start

```python
from composo import Composo

composo_client = Composo()

result = composo_client.evaluate(
    messages=[
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hello! How can I help you today?"}
    ],
    criteria="Reward responses that are friendly"
)

print(f"Score: {result.score}")
print(f"Explanation: {result.explanation}")
```

## Documentation

For detailed documentation, API reference, examples, and guides, please visit [docs.composo.ai](https://docs.composo.ai).
