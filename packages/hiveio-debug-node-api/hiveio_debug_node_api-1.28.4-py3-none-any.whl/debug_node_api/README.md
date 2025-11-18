### Hive JSON-RPC API package

### Installation

```bash
    pip install hiveio-debug-node-api
```

### Usage

```python
    from wax import create_hive_chain
    from debug_node_api.debug_node_api_client import DebugNodeApi

    class MyApiCollection:
        def __init__(self):
            self.debug_node_api = DebugNodeApi


    chain = create_hive_chain().extends(MyApiCollection)
```