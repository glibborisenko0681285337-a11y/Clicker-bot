import asyncio
import random
from telethon import TelegramClient, events

# =========================
# НАЛАШТУВАННЯ
# =========================

API_ID = 38356152
API_HASH = "983051aa071e4b2f9df1378fe87c28fc"

# ID Володі
VOLODYА_ID = 5987681144

SESSION_NAME = "my_account"

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# =========================
# СТАН
# =========================

troll_active = False
mute_active = False
troll_task = None

# =========================
# ДОПОМІЖНІ ФУНКЦІЇ
# =========================

async def delete_command(event):
    try:
        await event.delete()
    except Exception:
        pass


async def send_to_volodya(text):
    try:
        await client.send_message(VOLODYА_ID, text)
    except Exception as e:
        print("Помилка надсилання:", e)


async def troll_scenario():
    global troll_active

    messages = [
        "🤖 Система активована...",
        "🔎 Сканування користувача...",
        "⏳ Аналіз повідомлень...",
        "📡 З'єднання встановлено...",
        "🚨 ВОЛОДЮ ЗНАЙДЕНО 😂",
        "🤣 АХАХА, це просто тролінг!",
        "🤝 Все-все, мир 😎"
    ]

    for msg in messages:
        if not troll_active:
            break

        await send_to_volodya(msg)
        await asyncio.sleep(2)

    troll_active = False


async def chaos_scenario():
    global troll_active

    messages = [
        "🚨 УВАГА!",
        "🤖 Запускається режим ХАОС...",
        "1%...",
        "25%...",
        "67%...",
        "99%...",
        "100%!",
        "💥 ХАОС ЗАВЕРШЕНО 😂",
        "🤝 Мир?"
    ]

    for msg in messages:
        if not troll_active:
            break

        await send_to_volodya(msg)
        await asyncio.sleep(1.5)

    troll_active = False


async def matrix_scenario():
    global troll_active

    messages = [
        "🟩 Підключення до Матриці...",
        "🟩 Завантаження...",
        "🟩 Перевірка системи...",
        "🟩 Користувача знайдено.",
        "😂 ВОЛОДЯ, ТИ В МАТРИЦІ!",
        "🤝 Жарт 😎"
    ]

    for msg in messages:
        if not troll_active:
            break

        await send_to_volodya(msg)
        await asyncio.sleep(2)

    troll_active = False


async def scanner_scenario():
    global troll_active

    messages = [
        "🔎 Сканер запущено...",
        "🔎 Сканування...",
        "🔎 10%...",
        "🔎 50%...",
        "🔎 100%...",
        "🚨 Результат: ВОЛОДЯ 😂"
    ]

    for msg in messages:
        if not troll_active:
            break

        await send_to_volodya(msg)
        await asyncio.sleep(1.5)

    troll_active = False


async def error_scenario():
    global troll_active

    messages = [
        "💻 Запуск системи...",
        "🔄 Перевірка...",
        "⚠️ Помилка...",
        "⚠️ Повторна перевірка...",
        "🚨 КРИТИЧНА ПОМИЛКА",
        "Причина: знайдено Володю 😂",
        "🤝 Система жартує 😎"
    ]

    for msg in messages:
        if not troll_active:
            break

        await send_to_volodya(msg)
        await asyncio.sleep(1.7)

    troll_active = False


async def countdown_scenario():
    global troll_active

    for number in range(5, 0, -1):
        if not troll_active:
            break

        await send_to_volodya(f"⏳ {number}...")
        await asyncio.sleep(1)

    if troll_active:
        await send_to_volodya("💥 БУМ! 😂 Жарт!")
        await asyncio.sleep(1)
        await send_to_volodya("🤝 Мир!")

    troll_active = False


async def surprise_scenario():
    global troll_active

    jokes = [
        "🎁 У мене для тебе сюрприз...",
        "⏳ Зачекай...",
        "⏳ Ще секунду...",
        "🎉 СЮРПРИЗ!",
        "😂 Ти просто потрапив на тролінг!",
        "🤝 Мир 😎"
    ]

    for msg in jokes:
        if not troll_active:
            break

        await send_to_volodya(msg)
        await asyncio.sleep(2)

    troll_active = False


# =========================
# КОМАНДИ ВІД ТЕБЕ
# =========================

@client.on(events.NewMessage(outgoing=True))
async def my_commands(event):
    global troll_active, mute_active, troll_task

    text = event.raw_text.strip().lower()

    # Працюємо тільки з командами
    commands = [
        "тролл",
        "стоп",
        "мир",
        "хаос",
        "матриця",
        "сканер",
        "помилка",
        "відлік",
        "сюрприз",
        "мут",
        "стоп мут"
    ]

    if text not in commands:
        return

    await delete_command(event)

    # =====================
    # МУТ
    # =====================

    if text == "мут":
        mute_active = True
        await send_to_volodya(
            "🔇 Автовідповідач тимчасово не приймає повідомлення."
        )
        print("🔇 Мут увімкнено")
        return

    if text == "стоп мут":
        mute_active = False
        await send_to_volodya(
            "🔊 Режим тиші завершено 😎"
        )
        print("🔊 Мут вимкнено")
        return

    # =====================
    # СТОП
    # =====================

    if text == "стоп":
        troll_active = False

        if troll_task:
            troll_task.cancel()
            troll_task = None

        await send_to_volodya("🛑 Тролінг зупинено.")
        return

    # =====================
    # МИР
    # =====================

    if text == "мир":
        troll_active = False

        if troll_task:
            troll_task.cancel()
            troll_task = None

        await send_to_volodya("🤝 МИР! Тролінг завершено 😂")
        return

    # =====================
    # НОВИЙ СЦЕНАРІЙ
    # =====================

    troll_active = True

    if troll_task:
        troll_task.cancel()

    if text == "тролл":
        troll_task = asyncio.create_task(troll_scenario())

    elif text == "хаос":
        troll_task = asyncio.create_task(chaos_scenario())

    elif text == "матриця":
        troll_task = asyncio.create_task(matrix_scenario())

    elif text == "сканер":
        troll_task = asyncio.create_task(scanner_scenario())

    elif text == "помилка":
        troll_task = asyncio.create_task(error_scenario())

    elif text == "відлік":
        troll_task = asyncio.create_task(countdown_scenario())

    elif text == "сюрприз":
        troll_task = asyncio.create_task(surprise_scenario())


# =========================
# АВТОМАТИЧНИЙ МУТ
# =========================

@client.on(events.NewMessage(incoming=True))
async def incoming_messages(event):
    global mute_active

    if not mute_active:
        return

    # Реагуємо тільки на Володю
    if event.sender_id != VOLODYА_ID:
        return

    try:
        await event.delete()
        print("🗑️ Повідомлення Володі видалено")
    except Exception as e:
        print("Не вдалося видалити:", e)


# =========================
# ЗАПУСК
# =========================

async def main():
    print("🤖 Telethon-автовідповідач запускається...")

    await client.start()

    me = await client.get_me()

    print("--------------------------------")
    print("✅ ПРОГРАМА ЗАПУЩЕНА")
    print(f"👤 Акаунт: {me.first_name}")
    print(f"🎯 ID Володі: {VOLODYА_ID}")
    print("--------------------------------")
    print("Команди:")
    print("тролл")
    print("стоп")
    print("мир")
    print("хаос")
    print("матриця")
    print("сканер")
    print("помилка")
    print("відлік")
    print("сюрприз")
    print("мут")
    print("стоп мут")
    print("--------------------------------")

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
