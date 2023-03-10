from loader import bot
from states.contact_info import UserInfoRequest
from telebot.types import Message
import json
import requests
from telebot.types import InputMediaPhoto
import re
import datetime


@bot.message_handler(commands=['history'])
def start(message: Message) -> None:
    id_user = message.from_user.id

    with open('history.json', 'r') as file:
        result = json.load(file)
        history = result[0][str(id_user)][0]
        commands = result[0][str(id_user)][0]['commands']
        date_time = result[0][str(id_user)][0]['date_time']
        flag_for_foto = result[0][str(id_user)][0]['foto']

        bot.send_message(message.chat.id, f'Ваша история поиска: \n'
                                          f'Команда: {commands}\n'
                                          f'Дата и время запроса: {date_time}')

        if flag_for_foto:

            for i_num in range(len(result) + 1):
                foto_his = re.findall(r'(https?:\/\/.+)', history[f"hotel{i_num}"])
                text = re.findall(r'.+', history[f"hotel{i_num}"])
                text2 = text[:8]
                medias = []

                text_for_user = ''
                for i in text2:
                    text_for_user += i + '\n'
                num = str(text2[7]).split()
                quantity_foto = int(num[3])

                for num in range(quantity_foto):
                    medias.append(InputMediaPhoto(foto_his[num], caption=text_for_user if num == 0 else ''))

                bot.send_media_group(chat_id=message.from_user.id, media=medias)

        else:

            for i_num in range(len(result) + 1):
                text = re.findall(r'.+', history[f"hotel{i_num}"])
                text2 = text[:8]

                text_for_user = ''
                for i in text2:
                    text_for_user += i + '\n'

                bot.send_message(message.chat.id, text_for_user)


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def start(message: Message) -> None:
    bot.set_state(message.from_user.id, UserInfoRequest.city, message.chat.id)
    bot.send_message(message.from_user.id, f'Привет, {message.from_user.username} в каком городе будем искать?')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["commands"] = message.text
        date_time = str(datetime.datetime.utcnow())
        data["date_time"] = date_time


@bot.message_handler(state=UserInfoRequest.city)
def get_city(message: Message) -> None:
    if message.text:
        bot.send_message(message.from_user.id, 'Спасибо, записал. Введите дату заезда в формате "YYYY-MM-DD"')
        bot.set_state(message.from_user.id, UserInfoRequest.check_in, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["city"] = message.text
    else:
        bot.send_message(message.from_user.id, 'Город может содержать только буквы')


@bot.message_handler(state=UserInfoRequest.check_in)
def get_data_in(message: Message) -> None:
    if message.text:
        bot.send_message(message.from_user.id, 'Спасибо, записал. Введите дату выезда в формате "YYYY-MM-DD"')
        bot.set_state(message.from_user.id, UserInfoRequest.check_out, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["check_in"] = message.text
    else:
        bot.send_message(message.from_user.id, 'Дата выезда может содержать только числа')


@bot.message_handler(state=UserInfoRequest.check_out)
def get_data_out(message: Message) -> None:
    if message.text:
        bot.send_message(message.from_user.id, 'Спасибо, записал. Сколько отелей показать?')
        bot.set_state(message.from_user.id, UserInfoRequest.quantity_hotels, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["check_out"] = message.text
    else:
        bot.send_message(message.from_user.id, 'Дата выезда может содержать только числа')


@bot.message_handler(state=UserInfoRequest.quantity_hotels)
def get_quantity_hotels(message: Message) -> None:
    if message.text:
        bot.send_message(message.from_user.id, 'Спасибо, записал. Показать фото?')
        bot.set_state(message.from_user.id, UserInfoRequest.show_foto, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['quantity_hotels'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Ответ может быть только числом')


@bot.message_handler(state=UserInfoRequest.show_foto)
def get_answer_user(message: Message) -> None:
    answer_yes = ["yes", "Yes", "да", "Да", "lf", "Lf", "da", "Da"]
    answer_no = ["no", "No", "нет", "Нет", "Ytn", "ytn", "net", "Net"]

    if message.text in answer_yes:
        bot.send_message(message.from_user.id, 'Спасибо, записал. Сколько фото показать?')
        bot.set_state(message.from_user.id, UserInfoRequest.quantity_foto, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['show_foto'] = True

    elif message.text in answer_no:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['show_foto'] = False
            data['quantity_foto'] = '0'

            if data['commands'] == "/bestdeal":
                bot.send_message(message.from_user.id, 'Укажите минимальную цену.')
                bot.set_state(message.from_user.id, UserInfoRequest.min_price, message.chat.id)

            else:
                text = f'Ищем по этим критериям:\n' \
                       f'Город - {data["city"]}\n' \
                       f'Дата заезда - {data["check_in"]}\n' \
                       f'Дата выезда - {data["check_out"]}\n' \
                       f'Количество отелей - {data["quantity_hotels"]}\n' \
                       f'Показать фото - {data["show_foto"]}\n' \
                       f'Количество фотографий - {data["quantity_foto"]}\n' \
                       f'Команда - {data["commands"]}'

                bot.send_message(message.from_user.id, text)
                bot.send_message(message.from_user.id, 'Загружаю...')
                qwerty(data, message)


@bot.message_handler(state=UserInfoRequest.quantity_foto)
def get_quantity_foto(message: Message) -> None:
    if message.text:
        bot.send_message(message.from_user.id, 'Спасибо, записал')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['quantity_foto'] = message.text

            if data['commands'] == "/bestdeal":
                bot.send_message(message.from_user.id, 'Укажите минимальную цену.')
                bot.set_state(message.from_user.id, UserInfoRequest.min_price, message.chat.id)
            else:
                text = f'Ищем по этим критериям:\n' \
                       f'Город - {data["city"]}\n' \
                       f'Дата заезда - {data["check_in"]}\n' \
                       f'Дата выезда - {data["check_out"]}\n' \
                       f'Количество отелей - {data["quantity_hotels"]}\n' \
                       f'Показать фото - {data["show_foto"]}\n' \
                       f'Количество фотографий - {data["quantity_foto"]}\n' \
                       f'Команда - {data["commands"]}'

                bot.send_message(message.from_user.id, text)
                bot.send_message(message.from_user.id, 'Загружаю...')
                qwerty(data, message)


@bot.message_handler(state=UserInfoRequest.min_price)
def min_price(message: Message) -> None:
    bot.send_message(message.from_user.id, 'Укажите максимальную цену.')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["min_price"] = message.text
        bot.set_state(message.from_user.id, UserInfoRequest.max_price, message.chat.id)


@bot.message_handler(state=UserInfoRequest.max_price)
def max_price(message: Message) -> None:
    bot.send_message(message.from_user.id, 'Укажите диапазон дистанции через дефис "-"')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["max_price"] = message.text
        bot.set_state(message.from_user.id, UserInfoRequest.distance, message.chat.id)


@bot.message_handler(state=UserInfoRequest.distance)
def distance(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["distance"] = message.text

        text = f'Ищем по этим критериям:\n' \
               f'Город - {data["city"]}\n' \
               f'Дата заезда - {data["check_in"]}\n' \
               f'Дата выезда - {data["check_out"]}\n' \
               f'Количество отелей - {data["quantity_hotels"]}\n' \
               f'Показать фото - {data["show_foto"]}\n' \
               f'Количество фотографий - {data["quantity_foto"]}\n' \
               f'Команда - {data["commands"]}\n' \
               f'Мин цена - {data["min_price"]}\n'\
               f'Макс цена - {data["max_price"]}\n' \
               f'Дистанция - {data["distance"]} миль'

        bot.send_message(message.from_user.id, text)
        bot.send_message(message.from_user.id, 'Загружаю...')
        qwerty(data, message)


def qwerty(data, message):
    url = "https://hotels4.p.rapidapi.com/locations/v3/search"

    querystring = {"q": data["city"], "locale": "en_US", "langid": "1033", "siteid": "300000001"}

    headers = {
        "X-RapidAPI-Key": "81f573b7a2msh157b866b65b5604p17a326jsn7593d54af000",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    print('response:', response.text)
    # Проверяем полученный ответ с сайта
    if response.status_code == requests.codes.ok:
        print('статус запроса = ok')

        result = json.loads(response.text)
        id_city = str(result["sr"][0]["gaiaId"])
        print('id city:', id_city)

        items = request(data, id_city, message)

        id_list = []
        for add_id in items:
            if data["commands"] == "/bestdeal":
                numbers = data["distance"].split('-')
                start_number = int(numbers[0])
                end_number = int(numbers[1])
                if (add_id["destinationInfo"]["distanceFromDestination"]["value"] < start_number)\
                        or (add_id["destinationInfo"]["distanceFromDestination"]["value"] > end_number):
                    break
                else:
                    id_list.append(add_id["id"])
            else:
                id_list.append(add_id["id"])
            if len(id_list) == int(data["quantity_hotels"]):
                break

        print(id_list)
        count = 0
        for i_requests in items:
            if i_requests["id"] in id_list:
                url = "https://hotels4.p.rapidapi.com/properties/v2/detail"

                payload = {
                    "currency": "USD",
                    "eapid": 1,
                    "locale": "en_US",
                    "siteId": 300000001,
                    "propertyId": i_requests["id"]
                }
                headers = {
                    "content-type": "application/json",
                    "X-RapidAPI-Key": "81f573b7a2msh157b866b65b5604p17a326jsn7593d54af000",
                    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
                }

                response2 = requests.request("POST", url, json=payload, headers=headers)
                result3 = json.loads(response2.text)

                if data["show_foto"]:
                    foto = []
                    for num in range(int(data["quantity_foto"])):
                        foto.append(result3["data"]["propertyInfo"]["propertyGallery"]["images"][num]["image"]["url"])

                    medias = []
                    if i_requests["id"] in id_list:
                        text = f'City: {data["city"]}\n' \
                               f'Hotel: {i_requests["name"]}\n' \
                               f'Address: ' \
                               f'{result3["data"]["propertyInfo"]["summary"]["location"]["address"]["addressLine"]}\n' \
                               f'Distance from the center: ' \
                               f'{i_requests["destinationInfo"]["distanceFromDestination"]["value"]} miles\n' \
                               f'Arrival date: {data["check_in"]}\n' \
                               f'Departure date:  {data["check_out"]}\n' \
                               f'Price: {i_requests["price"]["lead"]["formatted"]}\n' \
                               f'Number of photos: {data["quantity_foto"]}'

                        for num in range(int(data["quantity_foto"])):
                            medias.append(InputMediaPhoto(foto[num], caption=text if num == 0 else ''))

                        bot.send_media_group(chat_id=message.from_user.id, media=medias)
                        count += 1
                        record(data, message, text, count, foto)

                    if len(id_list) < int(data["quantity_hotels"]):
                        bot.send_message(message.from_user.id, 'Это все, что удалось найди по заданным критериям.')

                else:
                    if i_requests["id"] in id_list:
                        text = f'City: {data["city"]}\n' \
                               f'Hotel: {i_requests["name"]}\n' \
                               f'Address: ' \
                               f'{result3["data"]["propertyInfo"]["summary"]["location"]["address"]["addressLine"]}\n' \
                               f'Distance from the center: ' \
                               f'{i_requests["destinationInfo"]["distanceFromDestination"]["value"]} miles\n' \
                               f'Arrival date: {data["check_in"]}\n' \
                               f'Departure date:  {data["check_out"]}\n' \
                               f'Price: {i_requests["price"]["lead"]["formatted"]}\n' \
                               f'Number of photos: {data["quantity_foto"]}'

                        bot.send_message(message.from_user.id, text)
                        count += 1
                        record(data, message, text, count)

                    if len(id_list) < int(data["quantity_hotels"]):
                        bot.send_message(message.from_user.id, 'Это все, что удалось найди по заданным критериям.')


def record(data, message, text, count, *args, **kwargs):
    if count == 1:
        if data["show_foto"]:
            new_media = [
                {message.from_user.id: [{"foto": True, "commands": data["commands"], "date_time": data["date_time"],
                                         f"hotel{count - 1}": text + '\n' + "\n".join(*args)}]}]
        else:
            new_media = [
                {message.from_user.id: [{"foto": False, "commands": data["commands"], "date_time": data["date_time"],
                                         f"hotel{count - 1}": text + '\n' + "\n"}]}]

        with open('history.json', 'w', encoding='utf-8') as file:
            json.dump(new_media, file, indent=4)
    else:
        with open('history.json', 'r', encoding='utf-8') as file:
            result_json = json.load(file)
            if data["show_foto"]:
                result_json[0][str(message.from_user.id)][0][
                    f"hotel{count - 1}"] = text + '\n' + "\n".join(*args)
            else:
                result_json[0][str(message.from_user.id)][0][f"hotel{count - 1}"] = text + '\n' + "\n"

            with open('history.json', 'w', encoding='utf-8') as file:
                json.dump(result_json, file, indent=4)


def request(data, id_city, message):

    date_time_str_in = data["check_in"]
    date_for_in = date_time_str_in.split('-')
    check_in_day = int(date_for_in[2])
    check_in_month = int(date_for_in[1])
    check_in_year = int(date_for_in[0])

    date_time_str_out = data["check_out"]
    date_for_out = date_time_str_out.split('-')
    check_out_day = int(date_for_out[2])
    check_out_month = int(date_for_out[1])
    check_out_year = int(date_for_out[0])

    if data["commands"] == "/lowprice":
        sort_price = "PRICE_LOW_TO_HIGH"
        max_price_for_best = 200
        min_price_for_best = 1

    elif data["commands"] == "/highprice":
        sort_price = "RECOMMENDED"
        max_price_for_best = 200
        min_price_for_best = 1

    elif data["commands"] == "/bestdeal":
        sort_price = "DISTANCE"
        max_price_for_best = int(data["max_price"])
        min_price_for_best = int(data["min_price"])
    else:
        sort_price = "PRICE_LOW_TO_HIGH"
        max_price_for_best = 200
        min_price_for_best = 1

    try:
        url = "https://hotels4.p.rapidapi.com/properties/v2/list"
        payload = {
            "currency": "USD",
            "eapid": 1,
            "locale": "en_US",
            "siteId": 300000001,
            "destination": {"regionId": id_city},
            "checkInDate": {
                "day": check_in_day,
                "month": check_in_month,
                "year": check_in_year
            },
            "checkOutDate": {
                "day": check_out_day,
                "month": check_out_month,
                "year": check_out_year
            },
            "rooms": [
                {
                    "adults": 2,
                    "children": [{"age": 5}, {"age": 7}]
                }
            ],
            "resultsStartingIndex": 0,
            "resultsSize": 200,
            "sort": sort_price,
            "filters": {"price": {
                "max": max_price_for_best,
                "min": min_price_for_best
            }}
        }
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": "81f573b7a2msh157b866b65b5604p17a326jsn7593d54af000",
            "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
        }

        response = requests.request("POST", url, json=payload, headers=headers)
        result2 = json.loads(response.text)
        items = result2["data"]["propertySearch"]["properties"]
        return items

    except:
        bot.send_message(message.from_user.id,
                         'По данным критериям ничего не найдено, попробуйте увеличить сумма или дистанцию')
