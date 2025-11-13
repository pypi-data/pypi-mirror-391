# sumo-logger

A lightweight and production-ready Python package for sending application logs to **Sumo Logic HTTP Sources** using the built-in `logging` module.

---

## 📘 Overview

`sumo-logger` makes it easy to stream your Python logs directly to [Sumo Logic](https://www.sumologic.com/) with minimal setup.  
It extends Python’s native `logging` system, allowing you to:

- Centralize logs across microservices or distributed apps.
- Automatically retry failed requests with exponential backoff.
- Send structured JSON logs containing rich metadata (timestamp, level, file, function, etc.).
- Use it as a drop-in replacement for your existing logging setup.

---

## 📦 Installation

You can install **sumo-logger** directly from [PyPI](https://pypi.org/project/sumo-logger/):

```bash
pip install sumo-logger
```
