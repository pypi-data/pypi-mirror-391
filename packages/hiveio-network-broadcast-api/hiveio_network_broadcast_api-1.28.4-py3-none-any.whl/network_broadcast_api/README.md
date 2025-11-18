### Hive JSON-RPC API package

### Installation

```bash
    pip install hiveio-network-broadcast-api
```

### Usage

```python
    from wax import create_hive_chain
    from network_broadcast_api.network_broadcast_api_client import NetworkBroadcastApi

    class MyApiCollection:
        def __init__(self):
            self.network_broadcast_api = NetworkBroadcastApi


    chain = create_hive_chain().extends(MyApiCollection)
```