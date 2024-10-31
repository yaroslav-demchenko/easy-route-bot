import os
from dotenv import load_dotenv
import telebot
from telebot import types
import json
from datetime import datetime

load_dotenv()
ACCESS_TOKEN = os.getenv("TELEGRAM_ACCESS_TOKEN")

bot = telebot.TeleBot(ACCESS_TOKEN, parse_mode=None)

data = {}

with open("route_mapping.json", "r") as file:
    route_map = json.load(file)


def validate_date_format(date_text):
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True
    except ValueError:
        return False


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    if message.from_user.id not in data.keys():
        data[user_id] = {
            "name": user_name,
            "routes": []
        }
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Створити маршрут", callback_data=f'create_route')
    btn2 = types.InlineKeyboardButton(text="Мої маршрути", callback_data=f'view_routes')

    markup.add(btn1, btn2)
    bot.send_message(
        message.chat.id,
        f"Вітаємо в Easy-Route Bot!",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('view_routes'))
def view_routes(call):
    user_id = call.from_user.id
    routes = data[user_id]["routes"]
    markup = types.InlineKeyboardMarkup()
    for route in routes:
        dest = route["destination"]
        dep = route["departure"]
        btn = types.InlineKeyboardButton(text=f"{dep}-{dest}", callback_data=f'tickets_info-{dep}-{dest}')
        markup.add(btn)
    bot.send_message(
        call.message.chat.id,
        f"Оберіть необхідний маршрут:",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('tickets_info'))
def set_route(call):
    dep_dest = call.data.split("-")
    departure = dep_dest[1]
    destination = dep_dest[2]
    msg = bot.send_message(call.message.chat.id, 'Введіть дату відправлення в форматі: 2024-10-31')
    bot.register_next_step_handler(msg, get_date, departure, destination)


def get_date(message, departure, destination):
    date = message.text
    if validate_date_format(date):
        bot.send_message(message.from_user.id, "Опрацьовуємо ваш запит...")
        # TODO realise parsing functionality
    else:
        bot.send_message(message.from_user.id, "Не вірний формат дати. Спробуйте ще раз...")

@bot.callback_query_handler(func=lambda call: call.data.startswith('create_route'))
def ask_departure(call):
    msg = bot.send_message(call.message.chat.id, 'Введіть місце відправлення:')
    bot.register_next_step_handler(msg, ask_destination)


def ask_destination(message):
    departure = message.text
    msg = bot.send_message(message.chat.id, 'Введіть місце призначення:')
    bot.register_next_step_handler(msg, write_route, departure)


def write_route(message, departure):
    user_id_data = message.from_user.id
    destination = message.text
    if destination.lower() in route_map.keys() and departure.lower() in route_map.keys():
        data[user_id_data]["routes"].append(
            {
                "departure": departure,
                "destination": destination
            }
        )
        bot.send_message(message.chat.id, f'Ви зареєстрували маршрут: {departure.upper()}-{destination.upper()}')
    else:
        bot.send_message(message.chat.id, f'Не вдалося зареєструвати такий маршрут: {departure.upper()}-{destination.upper()}')


if __name__ == '__main__':
    bot.infinity_polling()
