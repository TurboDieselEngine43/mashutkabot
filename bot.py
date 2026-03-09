import telebot
import requests
import random
import time
from datetime import datetime, timedelta

# ТВОИ ДАННЫЕ (уже вставлены)
BOT_TOKEN = "8765744270:AAFC9OrhzRAcctmNVZhk8588OKAalWvcNzQ"
WEATHER_API_KEY = "19db7301b7b8516736173b0218b23499"
ALLOWED_USER_ID = 6223685380 # ID твоей жены

bot = telebot.TeleBot(BOT_TOKEN)
DEFAULT_CITY = "Kirov"

# База анекдотов (нормальные, не тестовые)
JOKES = [
    "— Дорогой, я кастрюлю сожгла! \n— А что там было? \n— Борщ. \n— А борщ где был? \n— В кастрюле...",
    "Встречаются два программиста: \n— Слышал, твоя программа зависла? \n— Нет, она просто задумалась о смысле жизни.",
    "— Почему программисты путают Хэллоуин и Рождество? \n— Потому что 31 Oct = 25 Dec.",
    "Учитель спрашивает Вовочку: \n— Сколько будет 2×2? \n— А мы сейчас продаем или покупаем?",
    "— Доктор, у меня галлюцинации! \n— А вы кому об этом рассказываете? Я же галлюцинация!",
    "Оптимист учит английский, пессимист - китайский. А реалист - автомат Калашникова.",
    "— Ты почему опоздал на работу? \n— Я вышел пораньше, но навигатор сказал, что я приеду вовремя, и я расслабился.",
    "— Ваш сын на экзамене вытянул билет и упал в обморок. Что делать? \n— Переверните на другой бок.",
]

# Функция проверки доступа
def is_allowed_user(user_id):
    return user_id == ALLOWED_USER_ID

# Функция получения погоды
def get_weather_forecast(city=DEFAULT_CITY):
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if str(data.get('cod')) != '200':
            print(f"Ошибка API: {data.get('cod')}")
            return None
        
        # Собираем прогноз по дням
        forecast = {}
        for item in data['list']:
            date = datetime.fromtimestamp(item['dt']).strftime('%d.%m')
            if date not in forecast:
                forecast[date] = {
                    'temp_max': item['main']['temp_max'],
                    'temp_min': item['main']['temp_min'],
                    'description': item['weather'][0]['description'],
                    'humidity': item['main']['humidity'],
                    'wind_speed': item['wind']['speed'],
                    'feels_like': item['main']['feels_like'],
                }
            else:
                forecast[date]['temp_max'] = max(forecast[date]['temp_max'], item['main']['temp_max'])
                forecast[date]['temp_min'] = min(forecast[date]['temp_min'], item['main']['temp_min'])
        
        return forecast
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

# Функция рекомендаций по одежде
def get_clothing_recommendation(temp):
    if temp < -20:
        return "❄️ Очень холодно! Пуховик, шапка, шарф, варежки!"
    elif temp < -10:
        return "🧥 Холодно! Зимний пуховик, теплая шапка и перчатки."
    elif temp < 0:
        return "🧣 Прохладно. Куртка, шапка и шарф."
    elif temp < 10:
        return "🧥 Свежо. Легкая куртка или пальто."
    elif temp < 18:
        return "👕 Прохладно. Свитер или кофта."
    elif temp < 25:
        return "👚 Тепло. Футболка и джинсы."
    else:
        return "🩳 Жарко! Шорты, майка, панама."

# Функция эмодзи для погоды
def get_weather_emoji(desc):
    desc = desc.lower()
    if 'ясно' in desc: return '☀️'
    if 'облачно' in desc: return '⛅'
    if 'пасмурно' in desc: return '☁️'
    if 'дождь' in desc: return '🌧️'
    if 'снег' in desc: return '❄️'
    return '🌡️'

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_allowed_user(message.from_user.id):
        bot.reply_to(message, "🚫 Этот бот только для одного человека.")
        return
    
    welcome_text = (
        "👋 *Привет, любимая!* 🌸\n\n"
        "Я твой личный помощник:\n"
        "🌤 /weather - погода в Кирове\n"
        "😄 /joke - анекдот\n"
        "🆘 /help - помощь"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

# Команда /help
@bot.message_handler(commands=['help'])
def send_help(message):
    if not is_allowed_user(message.from_user.id):
        return
    bot.reply_to(message, "Просто жми /weather или /joke", parse_mode='Markdown')

# Команда /weather (ПОЛНАЯ РАБОЧАЯ ВЕРСИЯ)
@bot.message_handler(commands=['weather'])
def send_weather(message):
    if not is_allowed_user(message.from_user.id):
        return
    
    msg = bot.reply_to(message, "🔍 Смотрю погоду в Кирове... Подожди секунду...")
    
    forecast = get_weather_forecast()
    
    if not forecast:
        bot.edit_message_text("😕 Не могу получить погоду. Попробуй позже.", 
                            message.chat.id, msg.message_id)
        return
    
    # Формируем сообщение с прогнозом
    weather_text = "🌤 *Погода в Кирове:*\n\n"
    
    # Берем первые 3 дня
    for i, (date, day) in enumerate(list(forecast.items())[:3]):
        temp_avg = (day['temp_min'] + day['temp_max']) / 2
        emoji = get_weather_emoji(day['description'])
        
        weather_text += f"*{date}*\n"
        weather_text += f"{emoji} {day['description'].capitalize()}\n"
        weather_text += f"🌡️ {day['temp_min']:.0f}..{day['temp_max']:.0f}°C (ощущается {day['feels_like']:.0f}°C)\n"
        weather_text += f"💧 Влажность: {day['humidity']}%\n"
        weather_text += f"💨 Ветер: {day['wind_speed']:.1f} м/с\n"
        weather_text += f"👔 *Совет:* {get_clothing_recommendation(temp_avg)}\n\n"
    
    bot.edit_message_text(weather_text, message.chat.id, msg.message_id, parse_mode='Markdown')

# Команда /joke (НОРМАЛЬНЫЕ АНЕКДОТЫ)
@bot.message_handler(commands=['joke'])
def send_joke(message):
    if not is_allowed_user(message.from_user.id):
        return
    
    joke = random.choice(JOKES)
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(1)
    bot.reply_to(message, f"*Анекдот:*\n\n{joke}", parse_mode='Markdown')

# Обработка обычных сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not is_allowed_user(message.from_user.id):
        return
    
    text = message.text.lower()
    
    if 'погод' in text:
        bot.reply_to(message, "🌤 Жми /weather")
    elif 'анекдот' in text or 'шутк' in text:
        bot.reply_to(message, "😄 Жми /joke")
    elif 'привет' in text:
        bot.reply_to(message, "👋 Приветик!")
    elif 'спасиб' in text:
        bot.reply_to(message, "😊 Всегда пожалуйста")
    elif 'пока' in text:
        bot.reply_to(message, "👋 Пока-пока!")
    else:
        bot.reply_to(message, random.choice([
            "🌤 Как погода?", 
            "😄 Анекдот хочешь?", 
            "👂 Я слушаю"
        ]))

if __name__ == '__main__':
    print("🤖 Бот запущен! Жду сообщения...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)
