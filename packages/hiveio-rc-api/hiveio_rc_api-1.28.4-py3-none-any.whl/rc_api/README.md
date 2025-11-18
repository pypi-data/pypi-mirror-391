### Hive JSON-RPC API package

### Installation

```bash
    pip install hiveio-rc-api
```

### Usage

```python
    from wax import create_hive_chain
    from rc_api.rc_api_client import RcApi

    class MyApiCollection:
        def __init__(self):
            self.rc_api = RcApi


    chain = create_hive_chain().extends(MyApiCollection)
```