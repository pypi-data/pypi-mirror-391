### Hive JSON-RPC API package

### Installation

```bash
    pip install hiveio-transaction-status-api
```

### Usage

```python
    from wax import create_hive_chain
    from transaction_status_api.transaction_status_api_client import TransactionStatusApi

    class MyApiCollection:
        def __init__(self):
            self.transaction_status_api = TransactionStatusApi


    chain = create_hive_chain().extends(MyApiCollection)
```