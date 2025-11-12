# Playgent

[![PyPI Version](https://img.shields.io/pypi/v/playgent.svg)](https://pypi.org/project/playgent/)
[![Python Versions](https://img.shields.io/pypi/pyversions/playgent.svg)](https://pypi.org/project/playgent/)

Record and test your OpenAI agent traces.

## Installation

```bash
pip install playgent
```

## Quick Start

### Step 1: Instrument your agent to record traces

```python
import json
from typing import List
import dotenv
import os

dotenv.load_dotenv()

from playgent.openai import OpenAI  # Drop-in replacement for OpenAI
from playgent import record, trace

client = OpenAI()  # Automatically tracks all OpenAI calls

# Your agent functions here
def add_to_todo_list(task: str) -> str:
    # ... your implementation
    pass

@record  # This decorator records the entire trace
def infer(input_text: str, model: str = "gpt-4", tools_list: List = None):
    messages = [{"role": "user", "content": input_text}]

    # Your agent logic with OpenAI calls
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools_list
    )

    # Process response and handle tool calls...
    return response

# Use trace context manager to auto-create traces
with trace() as sess:
    result = infer("Add 'buy milk' to my todo list")
```

### Step 2: Run tests via replay

After annotating traces with expected outcomes on the Playgent dashboard:

```python
from playgent import replay_test, evaluate
from example_agent import infer

# Test using a recorded trace ID
test_case_id = "6996b53a-1ebf-403a-8770-10ed001391c3"

with replay_test(test_case_id) as (trace_id, endpoint_events):
    for event in endpoint_events:
        infer(**event.arguments)
    result = evaluate(test_case_id, trace_id)
```

That's it! Two steps:
1. **Instrument** - Add `@record` decorator and use `playgent.openai.OpenAI`
2. **Test** - Replay annotated traces and evaluate results

## Environment Setup

Create a `.env` file:

```bash
PLAYGENT_API_KEY=your-playgent-api-key
OPENAI_API_KEY=your-openai-api-key
```

## Full Examples

See [example_agent.py](example_agent.py) and [example_agent_test.py](example_agent_test.py) for complete working examples.

## License

MIT