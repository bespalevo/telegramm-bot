from loader import bot
from states.contact_info import UserInfoRequest
from telebot.types import Message
import json
import requests
from telebot.types import InputMediaPhoto


@bot.message_handler(commands=['history'])
def start(message: Message) -> None:
    # bot.set_state(message.from_user.id, UserInfoRequest.city, message.chat.id)
    bot.send_message(message.from_user.id, f'Привет, {message.from_user.username} тут будет отображаться история')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        bot.send_message(message.from_user.id, f'Ваша история: {data["history"]}')
