### Hive JSON-RPC API package

### Installation

```bash
    pip install hiveio-follow-api
```

### Usage

```python
    from wax import create_hive_chain
    from follow_api.follow_api_client import FollowApi

    class MyApiCollection:
        def __init__(self):
            self.follow_api = FollowApi


    chain = create_hive_chain().extends(MyApiCollection)
```