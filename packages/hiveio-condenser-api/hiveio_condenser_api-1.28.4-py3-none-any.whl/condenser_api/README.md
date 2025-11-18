### Hive JSON-RPC API package

### Installation

```bash
    pip install hiveio-condenser-api
```

### Usage

```python
    from wax import create_hive_chain
    from condenser_api.condenser_api_client import CondenserApi

    class MyApiCollection:
        def __init__(self):
            self.condenser_api = CondenserApi


    chain = create_hive_chain().extends(MyApiCollection)
```