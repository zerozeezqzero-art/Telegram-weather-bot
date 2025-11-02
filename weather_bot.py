import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

# Токены из переменных окружения (безопасно!)
TELEGRAM_TOKEN = os.environ.get('8504670923:AAEdJJ6jZNMf3v_qoOIGIuQqC5VvdQAyrG4')
WEATHERAPI_KEY = os.environ.get('aad96c1c789441b79c1204403250211')

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_text = """
    🌤️ Привет! Я погодный бот!
    
    Просто напиши название города и я покажу погоду!
    
    Команды:
    /start - показать это сообщение
    /weather [город] - погода в указанном городе
    """
    await update.message.reply_text(welcome_text)

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /weather"""
    city = ' '.join(context.args) if context.args else "Moscow"
    weather_info = get_weather(city)
    await update.message.reply_text(weather_info)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка обычных сообщений с названием города"""
    city = update.message.text
    weather_info = get_weather(city)
    await update.message.reply_text(weather_info)

def get_weather(city_name):
    """Получение данных о погоде с WeatherAPI"""
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={WEATHERAPI_KEY}&q={city_name}&lang=ru"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            location = data['location']
            current = data['current']
            
            # Формируем красивое сообщение
            weather_text = f"""
🌍 **{location['name']}, {location['country']}**
🌤️ **{current['condition']['text']}**

📊 **Температура:** {current['temp_c']}°C
💁 **Ощущается как:** {current['feelslike_c']}°C
💧 **Влажность:** {current['humidity']}%
📏 **Давление:** {current['pressure_mb']} гПа
💨 **Ветер:** {current['wind_kph']} км/ч
👁️ **Видимость:** {current['vis_km']} км
            """
            return weather_text
        else:
            return f"❌ Город '{city_name}' не найден. Попробуй другое название."
            
    except Exception as e:
        return f"❌ Ошибка при получении погоды: {str(e)}"

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logging.error(f"Ошибка: {context.error}")
    if update and update.message:
        await update.message.reply_text("❌ Произошла ошибка при обработке запроса")

def main():
    """Основная функция"""
    # Проверяем что токены загружены
    if not TELEGRAM_TOKEN or not WEATHERAPI_KEY:
        logging.error("❌ Токены не найдены! Проверь переменные окружения.")
        return
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("weather", weather_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    print("🤖 Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()
