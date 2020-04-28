import telebot

print(telebot.__file__)

with open("telegram-bot-token.txt") as bot_key_file:
    BOT_TOKEN = bot_key_file.read().strip()

bot = telebot.TeleBot(BOT_TOKEN)

from telebot import types
    
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Привет, я телегамм бот Виталик!")

@bot.message_handler(commands=["help"])
def send_help(message):
    bot.send_message(message.chat.id, "Вот мои команды: \n /help \n /start")

@bot.message_handler(content_types=["sticker"])
def echo_sticker(message):
    bot.reply_to(message, "Прикольный стикер!")

@bot.message_handler(content_types=["voice"])
def echo_sticker(message):
    bot.reply_to(message, "Не умею распознавать голосовые сообщения!")

@bot.message_handler()
def echo(message):
    print(message)
    if message.text.lower() == "привет":
        bot.reply_to(message, f"Привет, {message.from_user.first_name}")
    elif message.text.lower() == "здравствуй":
        bot.reply_to(message, f"Здравствуй, {message.from_user.first_name}")
    elif message.text.lower() == "как дела?" or message.text.lower() == "как дела":
        bot.send_message(message.chat.id, "У меня все отлично")
    elif message.text.lower() == "как тебя зовут?" or message.text.lower() == "как тебя зовут":
        bot.send_message(message.chat.id, f"Я телеграм бот Виталик, приятно познакомиться, {message.from_user.first_name}")
    elif message.text.lower() == "пока" or message.text.lower() == "до свидания":
        bot.send_message(message.chat.id, f"Пока, {message.from_user.first_name}")
    else:
        bot.reply_to(message, 'Я Вас не совсем понял!')


bot.polling()