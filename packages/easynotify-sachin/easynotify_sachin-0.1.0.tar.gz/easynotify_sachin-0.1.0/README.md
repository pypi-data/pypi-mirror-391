# easynotify

A lightweight notification library that wraps AWS SNS or email for sending alerts.

## Usage
```python
from easynotify.notifier import EasyNotify

notify = EasyNotify(mode='email')
notify.send("Test", "Hello farmer!", "farmer@example.com")

