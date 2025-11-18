### Hive JSON-RPC API package

### Installation

```bash
    pip install hiveio-bridge
```

### Usage

```python
    from wax import create_hive_chain
    from bridge.bridge_client import Bridge

    class MyApiCollection:
        def __init__(self):
            self.bridge = Bridge


    chain = create_hive_chain().extends(MyApiCollection)
```