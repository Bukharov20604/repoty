from aiogram.dispatcher.filters import Command
from aiogram.types import Message
from main import dp
from states import question
from aiogram.dispatcher import FSMContext
import requests
from data import write, read
from config import WEATHER_TOKEN


@dp.message_handler(Command("start"))
async def show_hello(message: Message):
   await message.answer("Здраствуйте для работы ознакомьтесь с меню.")


@dp.message_handler(Command("get_weather"), state=None)
async def get_country(message:Message):
    await message.answer("Хотите узнать какая погода за окном? \n" 
                         "Отлично! Напишите название города, где хотите узнать погоду.")
    await question.Q.set()
@dp.message_handler(state=question.Q)
async def get_weather(message: Message, state: FSMContext):
    weather_var = {
        "Clear": "Ясно",
        "Clouds": "Облачно",
        "Rain": "Дождь",
        "Drizzle": "Дождь",
        "Thunderstorm": "Гроза",
        "Snow": "Снег",
        "Mist": "Туман"
    }

    answer = message.text
    async with state.proxy() as data:
        data["city"] = answer
    data = await state.get_data()
    city = data.get("city")
    try:
        city_data = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={WEATHER_TOKEN}").json()
        lat = city_data[0]["lat"]
        lon = city_data[0]["lon"]
        weather_data = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_TOKEN}&units=metric").json()
        await message.answer(
        f"Текущая погода в городе {city_data[0]['local_names']['ru']} - {weather_var[weather_data['weather'][0]['main']]} \n"
        f"Температура на улице: {weather_data['main']['temp']}°C \n"
        f"Ощущается как: {weather_data['main']['feels_like']}°C \n"
        f"Влажность: {weather_data['main']['humidity']}% \n"
        f"Давление: {weather_data['main']['pressure']}00 Паскалей. \n"
        f"Скорость ветра: {weather_data['wind']['speed']} м/с"
        )
        if weather_var[weather_data['weather'][0]['main']] == "Ясно":
            await message.answer(
                "На улице хорошая погода. \n" 
                "Советую вам выйти погулять"
            )
        elif weather_var[weather_data['weather'][0]['main']] == "Дождь":
            await message.answer(
                "На улице дождь! \n"
                "Не забудь зонтик или дождевик"
            )
        elif weather_var[weather_data['weather'][0]['main']] == "Снег":
            await message.answer(
                "На улице холодно! \n"
                "Не забудьте надеть шапку!"
            )
    except Exception as ex:
        await message.answer(
            "Данный город не найден :( \n"
            "Возможно вы некорректно его указали."
        )
        print(ex)

    s = read("data.json")
    with open("data.json", "w") as f:
        pass
    if f"{answer}" in s.keys():
        s.update({answer: s.get(answer) + 1})
    else:
        s[answer] = 1
    write(s, "data.json")
    await state.finish()


@dp.message_handler(Command("bot_stat"))
async def get_info(message: Message):
    s = read("data.json")
    str = ""
    sorted_dict = {}
    sorted_keys = sorted(s, key=s.get, reverse=True)
    for k in sorted_keys:
        sorted_dict[k] = s[k]

    if len(sorted_dict) < 20:
        for i in sorted_dict:
            str += f"{i} : {sorted_dict[i]} запросов \n"
    else:
        i = 0
        v = list(sorted_dict.keys())
        while i < 20:
            str += f"{v[i]} : {sorted_dict[v[i]]} запросов \n"
            i += 1

    await message.answer("Список наиболее запрашиваемых городов \n"
                         f"{str}"
                         )