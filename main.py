import asyncio
import logging
import sys
from datetime import datetime

import aiohttp

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message


# =========================================================
# ⚙️ НАЛАШТУВАННЯ
# =========================================================

BOT_TOKEN = "8965988024:AAHF0SHiAKCA0Z9k_4XGnoNc188pYYHun8U"

# Username каналу:
# наприклад "@my_channel"
CHANNEL_ID = "@ProRobloxUA"

# Місто для погоди
CITY = "Запоріжжя"

# Координати Запоріжжя
LATITUDE = 47.8388
LONGITUDE = 35.1396

# Як часто перевіряти погоду
WEATHER_INTERVAL = 60 * 60

# =========================================================
# 🤖 TELEGRAM
# =========================================================

dp = Dispatcher()

# Запам'ятовуємо останній стан тривоги,
# щоб бот не надсилав одне повідомлення багато разів.
last_alert_state = None

# Час останньої публікації погоди
last_weather_hour = None


# =========================================================
# 🌤️ ПОГОДА — OPEN-METEO
# =========================================================

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


async def get_weather():
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "precipitation,"
            "weather_code,"
            "wind_speed_10m"
        ),
        "timezone": "Europe/Kyiv",
    }

    try:
        timeout = aiohttp.ClientTimeout(total=10)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                WEATHER_URL,
                params=params
            ) as response:

                if response.status != 200:
                    print(
                        "Помилка погоди:",
                        response.status
                    )
                    return None

                return await response.json()

    except Exception as e:
        print("Помилка підключення до погоди:", e)
        return None


def weather_description(code):
    descriptions = {
        0: "☀️ Ясно",
        1: "🌤️ Переважно ясно",
        2: "⛅ Мінлива хмарність",
        3: "☁️ Хмарно",
        45: "🌫️ Туман",
        48: "🌫️ Іній/туман",
        51: "🌦️ Легка мряка",
        53: "🌦️ Мряка",
        55: "🌧️ Сильна мряка",
        61: "🌧️ Невеликий дощ",
        63: "🌧️ Дощ",
        65: "🌧️ Сильний дощ",
        71: "🌨️ Невеликий сніг",
        73: "🌨️ Сніг",
        75: "❄️ Сильний сніг",
        80: "🌦️ Зливи",
        81: "🌦️ Сильні зливи",
        82: "⛈️ Дуже сильні зливи",
        95: "⛈️ Гроза",
        96: "⛈️ Гроза з градом",
        99: "⛈️ Сильна гроза з градом",
    }

    return descriptions.get(
        code,
        "🌡️ Невідомі погодні умови"
    )


async def send_weather(bot: Bot):
    data = await get_weather()

    if not data:
        return

    current = data.get("current", {})

    temperature = current.get(
        "temperature_2m",
        "?"
    )

    humidity = current.get(
        "relative_humidity_2m",
        "?"
    )

    feels_like = current.get(
        "apparent_temperature",
        "?"
    )

    precipitation = current.get(
        "precipitation",
        "?"
    )

    wind = current.get(
        "wind_speed_10m",
        "?"
    )

    code = current.get(
        "weather_code",
        -1
    )

    description = weather_description(code)

    text = (
        f"🌤️ <b>ПОГОДА — {CITY.upper()}</b>\n\n"
        f"{description}\n\n"
        f"🌡️ Температура: <b>{temperature}°C</b>\n"
        f"🤔 Відчувається: <b>{feels_like}°C</b>\n"
        f"💧 Вологість: <b>{humidity}%</b>\n"
        f"🌧️ Опади: <b>{precipitation} мм</b>\n"
        f"💨 Вітер: <b>{wind} км/год</b>"
    )

    try:
        await bot.send_message(
            CHANNEL_ID,
            text
        )

        print("🌤️ Погоду опубліковано")

    except Exception as e:
        print(
            "Помилка відправлення погоди:",
            e
        )


# =========================================================
# 🚨 МІСЦЕ ДЛЯ API ТРИВОГ
# =========================================================
#
# Тут НЕ визначаємо координати або маршрути БпЛА.
#
# Функція повертає:
# True  = тривога
# False = відбій
# None  = не вдалося отримати дані
#
# Після підключення конкретного офіційного API
# вставимо його запит сюди.
# =========================================================


async def get_alert_state():
    """
    Повертає стан повітряної тривоги.

    True  -> тривога
    False -> відбій
    None  -> помилка / немає даних

    Зараз повертаємо None, щоб бот випадково
    не публікував неправдиві тривоги.
    """

    return None


# =========================================================
# 🚨 ВІДПРАВЛЕННЯ ТРИВОГИ
# =========================================================

async def send_air_alert(bot: Bot):

    text = (
        "🚨 <b>ПОВІТРЯНА ТРИВОГА</b>\n\n"
        "📍 Запорізька область\n\n"
        "⚠️ Перебувайте в безпечному місці "
        "та стежте за офіційними повідомленнями."
    )

    try:

        await bot.send_message(
            CHANNEL_ID,
            text
        )

        print("🚨 Надіслано повідомлення про тривогу")

    except Exception as e:

        print(
            "Помилка відправлення тривоги:",
            e
        )


# =========================================================
# 🟢 ВІДБІЙ
# =========================================================

async def send_air_clear(bot: Bot):

    text = (
        "🟢 <b>ВІДБІЙ ПОВІТРЯНОЇ ТРИВОГИ</b>\n\n"
        "📍 Запорізька область"
    )

    try:

        await bot.send_message(
            CHANNEL_ID,
            text
        )

        print("🟢 Надіслано відбій")

    except Exception as e:

        print(
            "Помилка відправлення відбою:",
            e
        )


# =========================================================
# 🔄 МОНІТОРИНГ ТРИВОГ
# =========================================================

async def alert_monitor(bot: Bot):

    global last_alert_state

    print("🚨 Моніторинг тривог запущений")

    while True:

        try:

            state = await get_alert_state()

            if state is not None:

                # Перше отримання
                if last_alert_state is None:

                    last_alert_state = state

                # Почалася тривога
                elif (
                    state is True
                    and last_alert_state is False
                ):

                    await send_air_alert(bot)

                    last_alert_state = True

                # Відбій
                elif (
                    state is False
                    and last_alert_state is True
                ):

                    await send_air_clear(bot)

                    last_alert_state = False

        except Exception as e:

            print(
                "Помилка моніторингу:",
                e
            )

        # Перевірка кожні 30 секунд
        await asyncio.sleep(30)


# =========================================================
# 🌤️ МОНІТОРИНГ ПОГОДИ
# =========================================================

async def weather_monitor(bot: Bot):

    global last_weather_hour

    print("🌤️ Моніторинг погоди запущений")

    while True:

        try:

            now = datetime.now()

            # Публікуємо один раз на початку кожної години
            current_hour = (
                now.year,
                now.month,
                now.day,
                now.hour
            )

            if current_hour != last_weather_hour:

                await send_weather(bot)

                last_weather_hour = current_hour

        except Exception as e:

            print(
                "Помилка моніторингу погоди:",
                e
            )

        await asyncio.sleep(60)


# =========================================================
# /START
# =========================================================

@dp.message(CommandStart())
async def start_command(message: Message):

    await message.answer(
        "🤖 <b>Бот працює!</b>\n\n"
        "🚨 Повітряні тривоги\n"
        "🟢 Відбої\n"
        "🌤️ Погода\n\n"
        "Повідомлення надходять у канал."
    )


# =========================================================
# 🚀 MAIN
# =========================================================

async def main():

    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout
    )

    if BOT_TOKEN == "ВСТАВ_ТОКЕН_БОТА_СЮДИ":

        print(
            "❌ Ти ще не вставив токен бота!"
        )

        return

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    print("================================")
    print("🤖 БОТ ЗАПУЩЕНИЙ")
    print("📢 Канал:", CHANNEL_ID)
    print("🌤️ Погода:", CITY)
    print("================================")

    try:

        await asyncio.gather(

            dp.start_polling(bot),

            alert_monitor(bot),

            weather_monitor(bot)

        )

    finally:

        await bot.session.close()


# =========================================================
# ▶️ ЗАПУСК
# =========================================================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print(
            "\n🛑 Бот зупинений."
)
