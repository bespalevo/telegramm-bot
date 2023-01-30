from telebot.handler_backends import State, StatesGroup


class UserInfoRequest(StatesGroup):
    city = State()
    check_in = State()
    check_out = State()
    quantity_hotels = State()
    quantity_foto = State()
    show_foto = State()
    commands = State()
    min_price = State()
    max_price = State()
    distance = State()
    address = State()
    date_time = State()

