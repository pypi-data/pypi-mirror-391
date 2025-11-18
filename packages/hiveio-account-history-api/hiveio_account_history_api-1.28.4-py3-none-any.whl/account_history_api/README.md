### Hive JSON-RPC API package

### Installation

```bash
    pip install hiveio-account-history-api
```

### Usage

```python
    from wax import create_hive_chain
    from account_history_api.account_history_api_client import AccountHistoryApi

    class MyApiCollection:
        def __init__(self):
            self.account_history_api = AccountHistoryApi


    chain = create_hive_chain().extends(MyApiCollection)
```