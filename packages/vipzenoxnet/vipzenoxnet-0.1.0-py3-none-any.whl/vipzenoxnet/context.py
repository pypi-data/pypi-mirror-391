class Message:
    def __init__(self, bot, chat_id, message_id, sender_id, text):
        self.bot = bot
        self.chat_id = chat_id
        self.message_id = message_id
        self.sender_id = sender_id
        self.text = text

    def reply(self, text):
        return self.bot.send_message(self.chat_id, text)
