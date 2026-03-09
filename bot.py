import telebot
import requests
import random
import time

# ТВОИ ДАННЫЕ (уже вставлены)
BOT_TOKEN = "8765744270:AAFC9OrhzRAcctmNVZhk8588OKAalWvcNzQ"
ALLOWED_USER_ID = 6223685380  # ID жены

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != ALLOWED_USER_ID:
        bot.reply_to(message, "🚫 Этот бот только для одного человека")
        return
    bot.reply_to(message, "👋 Привет, любимая! Я работаю 24/7\n/weather - погода\n/joke - анекдот")

@bot.message_handler(commands=['weather'])
def weather(message):
    if message.from_user.id != ALLOWED_USER_ID:
        return
    bot.reply_to(message, "🌤 Сейчас покажу погоду... (тут будет код позже)")

@bot.message_handler(commands=['joke'])
def joke(message):
    if message.from_user.id != ALLOWED_USER_ID:
        return
    jokes = ["Шутка 1", "Шутка 2", "Шутка 3"]
    bot.reply_to(message, random.choice(jokes))

print("Бот запущен!")
bot.polling()