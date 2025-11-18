### Hive JSON-RPC API package

### Installation

```bash
    pip install hiveio-reputation-api
```

### Usage

```python
    from wax import create_hive_chain
    from reputation_api.reputation_api_client import ReputationApi

    class MyApiCollection:
        def __init__(self):
            self.reputation_api = ReputationApi


    chain = create_hive_chain().extends(MyApiCollection)
```