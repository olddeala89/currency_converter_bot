import telebot
from telebot import types
import yahoo_fin.stock_info as si
from datetime import datetime, timedelta


# Ваш токен от BotFather
TOKEN = 'token'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    currencies = ['RUB', 'USD', 'EUR', 'BYN', 'GRN', 'AED', 'AMD', 'GBP']
    buttons = [types.KeyboardButton(currency) for currency in currencies]
    markup.add(*buttons)
    bot.reply_to(message, "Добро пожаловать в бот конвертер валют! Выберите из какой валюты конвертировать:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def get_source_currency(message):
    chat_id = message.chat.id
    source_currency = message.text.upper()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    currencies = ['RUB', 'USD', 'EUR', 'BYN', 'GRN', 'AED', 'AMD', 'GBP']
    buttons = [types.KeyboardButton(currency) for currency in currencies]
    markup.add(*buttons)
    bot.send_message(chat_id, f"Выбрана валюта для конвертации: {source_currency}. Теперь выберите валюту, в которую конвертировать:", reply_markup=markup)
    bot.register_next_step_handler(message, get_target_currency, source_currency)

def get_target_currency(message, source_currency):
    chat_id = message.chat.id
    target_currency = message.text.upper()
    bot.send_message(chat_id, f"Выбрана валюта, в которую конвертировать: {target_currency}. Теперь введите сумму для конвертации:")
    bot.register_next_step_handler(message, get_amount, source_currency, target_currency)

def get_amount(message, source_currency, target_currency):
    chat_id = message.chat.id
    try:
        amount = float(message.text)
        result = convert_function(source_currency, target_currency, amount)
        bot.send_message(chat_id, f"Результат конвертации: {result} {target_currency}")

        # Добавляем кнопку "Начать заново"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("Начать заново")
        markup.add(item)
        bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)

        # Регистрируем следующий шаг после нажатия кнопки "Начать заново"
        bot.register_next_step_handler(message, restart)
    except ValueError:
        bot.send_message(chat_id, "Пожалуйста, введите корректное число для суммы.")

def restart(message):
    # Функция для перезапуска бота, если пользователь нажимает "Начать заново"
    if message.text == "Начать заново":
        send_welcome(message)
    else:
        bot.send_message(message.chat.id, "Используйте кнопку 'Начать заново'.")

# Здесь должна быть ваша функция конвертации валют
def convert_function(source_currency, target_currency, amount):
    # Ваш алгоритм конвертации
    # Замените этот блок на свою функцию
    # construct the currency pair symbol
    symbol = f"{source_currency}{target_currency}=X"
    # extract minute data of the recent 2 days
    latest_data = si.get_data(symbol, interval="1m", start_date=datetime.now() - timedelta(days=2))
    # get the latest datetime
    last_updated_datetime = latest_data.index[-1].to_pydatetime()
    # get the latest price
    latest_price = latest_data.iloc[-1].close
    # return the latest datetime with the converted amount
    return latest_price * amount

if __name__ == "__main__":
    bot.polling(none_stop=True)