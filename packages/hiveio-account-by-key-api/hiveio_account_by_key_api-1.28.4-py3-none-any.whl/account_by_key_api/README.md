### Hive JSON-RPC API package

### Installation

```bash
    pip install hiveio-account-by-key-api
```

### Usage

```python
    from wax import create_hive_chain
    from account_by_key_api.account_by_key_api_client import AccountByKeyApi

    class MyApiCollection:
        def __init__(self):
            self.account_by_key_api = AccountByKeyApi


    chain = create_hive_chain().extends(MyApiCollection)
```