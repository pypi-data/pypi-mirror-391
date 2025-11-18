### Hive JSON-RPC API package

### Installation

```bash
    pip install hiveio-hive
```

### Usage

```python
    from wax import create_hive_chain
    from hive.hive_client import Hive

    class MyApiCollection:
        def __init__(self):
            self.hive = Hive


    chain = create_hive_chain().extends(MyApiCollection)
```