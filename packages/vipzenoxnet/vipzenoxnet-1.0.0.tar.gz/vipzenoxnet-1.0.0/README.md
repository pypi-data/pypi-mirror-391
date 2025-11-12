# vipzenoxnet

A lightweight, fast, and simple Rubika bot library using Bot Token.

## Installation

```bash
pip install requests
# then copy vipzenoxnet.py to your project
```

## Usage

```python
from vipzenoxnet import Bot

bot = Bot("YOUR_BOT_TOKEN")

@bot.on_message
def handle_message(message):
    if message.text == "/start":
        message.reply("Hello!")
    else:
        message.reply(f"You said: {message.text}")

bot.start_polling(interval=1)

while True:
    pass
```
