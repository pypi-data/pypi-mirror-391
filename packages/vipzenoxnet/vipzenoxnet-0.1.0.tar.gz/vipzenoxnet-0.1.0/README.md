# vipzenoxnet

Simple Rubika bot framework using real bot API endpoints.

```python
from vipzenoxnet.bot import Bot

bot = Bot(token="YOUR_RUBIKA_TOKEN")

@bot.on_start
def start(bot, message):
    message.reply("سلام! من بوت vipzenoxnet هستم ✅")

bot.run_polling()
```
