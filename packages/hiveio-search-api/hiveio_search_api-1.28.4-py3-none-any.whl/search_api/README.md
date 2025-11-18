### Hive JSON-RPC API package

### Installation

```bash
    pip install hiveio-search-api
```

### Usage

```python
    from wax import create_hive_chain
    from search_api.search_api_client import SearchApi

    class MyApiCollection:
        def __init__(self):
            self.search_api = SearchApi


    chain = create_hive_chain().extends(MyApiCollection)
```