### Hive JSON-RPC API package

### Installation

```bash
    pip install hiveio-block-api
```

### Usage

```python
    from wax import create_hive_chain
    from block_api.block_api_client import BlockApi

    class MyApiCollection:
        def __init__(self):
            self.block_api = BlockApi


    chain = create_hive_chain().extends(MyApiCollection)
```