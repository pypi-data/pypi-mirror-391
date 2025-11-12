# Megaflow SDK

Megaflow function SDK for writing Megaflow functions.

## Installation

```bash
pip install -e .
```

Or for development:
```bash
pip install -e packages/megaflow-sdk
```

## Usage

```python
from megaflow import FunctionContext, Items
from megaflow.types import Item

async def run(context: FunctionContext) -> Items:
    items = context.get_input_data()
    # ... your function logic
    return items
```

## API Reference

See the [Megaflow Function Programmability documentation](../../megaflow-dev-doc/domains/function/extensibility/function_programmability.md) for complete API reference.

