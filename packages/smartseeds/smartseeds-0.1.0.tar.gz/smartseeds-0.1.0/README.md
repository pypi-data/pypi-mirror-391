# SmartSeeds 🌱

**Essential utilities that grow smart solutions**

SmartSeeds is a lightweight, zero-dependency Python library providing core utilities for the smart* ecosystem (smartswitch, smartasync, etc.). Think of it as the seeds from which smart solutions grow.

[![Part of Genro-Libs](https://img.shields.io/badge/Part%20of-Genro--Libs-blue.svg)](https://github.com/softwell/genro-libs)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/smartseeds.svg)](https://badge.fury.io/py/smartseeds)
[![Documentation Status](https://readthedocs.org/projects/smartseeds/badge/?version=latest)](https://smartseeds.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/genropy/smartseeds/branch/main/graph/badge.svg)](https://codecov.io/gh/genropy/smartseeds)

## Features

- **`extract_kwargs`**: Decorator for extracting and grouping keyword arguments by prefix
- **Three flexible styles**: Prefix style, dict style, and boolean activation
- **Zero dependencies**: Pure Python standard library
- **Full type hints**: Complete typing support

## Installation

```bash
pip install smartseeds
```

## Quick Start

### extract_kwargs Decorator

Extract kwargs by prefix into separate parameter groups - supports three convenient styles:

```python
from smartseeds import extract_kwargs

@extract_kwargs(logging=True, cache=True)
def setup_service(name, logging_kwargs=None, cache_kwargs=None, **kwargs):
    print(f"Logging config: {logging_kwargs}")
    print(f"Cache config: {cache_kwargs}")
    print(f"Other: {kwargs}")

# Style 1: Prefix style (most explicit)
setup_service(
    name="api",
    logging_level="INFO",      # → logging_kwargs={'level': 'INFO'}
    logging_format="json",     # → logging_kwargs={'format': 'json'}
    cache_ttl=300,             # → cache_kwargs={'ttl': 300}
    timeout=30                 # → kwargs={'timeout': 30}
)

# Style 2: Dict style (compact)
setup_service(
    name="api",
    logging={'level': 'INFO', 'format': 'json'},
    cache={'ttl': 300}
)

# Style 3: Boolean activation (use defaults)
setup_service(
    name="api",
    logging=True,  # → logging_kwargs={} (empty dict for defaults)
    cache=True
)
```

### Use in smart* Ecosystem

SmartSeeds is designed to be used by other smart* tools:

```python
# In smartswitch, smartasync, etc.
from smartseeds import extract_kwargs

class Switcher:
    @extract_kwargs(logging=True, async_mode=True)
    def __init__(self, name=None, logging_kwargs=None, async_kwargs=None, **kwargs):
        # Plugin configuration extracted automatically
        if logging_kwargs:
            self.plug('logging', **logging_kwargs)
        if async_kwargs:
            self.plug('async', **async_kwargs)
```

## Why extract_kwargs?

Traditional approaches to nested configuration have problems:

**❌ Explicit parameters (verbose)**
```python
def connect(host, port, logging_level=None, logging_format=None, logging_file=None):
    logger = Logger(level=logging_level, format=logging_format, file=logging_file)
```

**❌ Catch-all kwargs (unclear)**
```python
def connect(host, port, **kwargs):
    # What kwargs are valid? Users don't know!
    logger = Logger(**kwargs)
```

**✅ extract_kwargs (clear + flexible)**
```python
@extract_kwargs(logging=True)
def connect(host, port, logging_kwargs=None):
    if logging_kwargs:
        logger = Logger(**logging_kwargs)

# All these work and are clear:
connect('localhost', 8000, logging_level='INFO')
connect('localhost', 8000, logging={'level': 'INFO'})
connect('localhost', 8000, logging=True)
```

## Documentation

Full documentation available at: https://smartseeds.readthedocs.io

## Part of the Smart* Family

SmartSeeds is part of the Genropy smart* toolkit:

- [smartswitch](https://github.com/genropy/smartswitch) - Rule-based function dispatch
- [smartasync](https://github.com/genropy/smartasync) - Async utilities
- [smartpub](https://github.com/genropy/smartpub) - Pub/sub messaging

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) first.
