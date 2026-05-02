# Code with Line Numbers

```python:example.py
1 | def main():
2 |     """Main entry point."""
3 |     config = load_config()
4 |     process(config)
5 |
6 |
7 | def load_config():
8 |     """Load configuration from file."""
9 |     return {"debug": True}
10|
11|
12| def process(config):
13|     """Process with config."""
14|     if config.get("debug"):
15|         print("Debug mode enabled")
```
