### Hive JSON-RPC API package

### Installation

```bash
    pip install hiveio-database-api
```

### Usage

```python
    from wax import create_hive_chain
    from database_api.database_api_client import DatabaseApi

    class MyApiCollection:
        def __init__(self):
            self.database_api = DatabaseApi


    chain = create_hive_chain().extends(MyApiCollection)
```