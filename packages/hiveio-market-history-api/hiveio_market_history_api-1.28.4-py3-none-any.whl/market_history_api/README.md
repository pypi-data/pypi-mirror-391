### Hive JSON-RPC API package

### Installation

```bash
    pip install hiveio-market-history-api
```

### Usage

```python
    from wax import create_hive_chain
    from market_history_api.market_history_api_client import MarketHistoryApi

    class MyApiCollection:
        def __init__(self):
            self.market_history_api = MarketHistoryApi


    chain = create_hive_chain().extends(MyApiCollection)
```