import asyncio
import json
import os
import time
from collections import defaultdict, deque

from telethon import TelegramClient, events

# =========================================================
# НАЛАШТУВАННЯ
# =========================================================

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")

SESSION_NAME = "my_account"
SETTINGS_FILE = "settings.json"

if not API_ID or not API_HASH:
    raise RuntimeError("Не задано API_ID або API_HASH у змінних середовища.")

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# =========================================================
# ГЛОБАЛЬНІ НАЛАШТУВАННЯ
# Команди +... / -... можна надсилати у «Збережене»
# =========================================================

settings = {
    "antispam": False,
    "autogreeting": False,
    "autoreply": False,
    "sleep": False,
    "autoreply_text": "Привіт! 👋 Зараз я не можу відповісти. Напишу пізніше 😊",
    "autoreply_entities": [],
}

# Сценарії працюють окремо в кожному чаті.
troll_active = defaultdict(bool)
troll_tasks = {}

mute_active = defaultdict(bool)

# Антиспам
spam_messages = defaultdict(lambda: defaultdict(deque))
spam_warnings = defaultdict(lambda: defaultdict(int))
last_warning = defaultdict(lambda: defaultdict(float))

MAX_MESSAGES = 6
TIME_WINDOW = 5
MAX_WARNINGS = 2
WARNING_COOLDOWN = 10

# Щоб не вітати одного й того самого користувача багато разів
greeted_users = set()

# Щоб не відповідати на власні повідомлення
my_id = None


# =========================================================
# ЗБЕРЕЖЕННЯ НАЛАШТУВАНЬ
# =========================================================

def load_settings():
    global settings

    if not os.path.exists(SETTINGS_FILE):
        return

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)

        for key in settings:
            if key in saved:
                settings[key] = saved[key]

    except Exception as e:
        print("Не вдалося завантажити settings.json:", e)


def save_settings():
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print("Не вдалося зберегти settings.json:", e)


# =========================================================
# ДОПОМІЖНІ ФУНКЦІЇ
# =========================================================

async def delete_message(event):
    try:
        await event.delete()
        return True
    except Exception as e:
        print("Не вдалося видалити повідомлення:", e)
        return False


async def send_to_chat(chat_id, text, formatting_entities=None):
    try:
        await client.send_message(
            chat_id,
            text,
            formatting_entities=formatting_entities
        )
    except Exception as e:
        print("Помилка надсилання:", e)


def stop_troll(chat_id):
    troll_active[chat_id] = False

    task = troll_tasks.get(chat_id)

    if task and not task.done():
        task.cancel()

    troll_tasks[chat_id] = None


def start_troll(chat_id, scenario):
    stop_troll(chat_id)

    troll_active[chat_id] = True
    troll_tasks[chat_id] = asyncio.create_task(scenario(chat_id))


# =========================================================
# ТРОЛЛ
# =========================================================

async def troll_scenario(chat_id):
    messages = [
        "🤖 Система активована...",
        "🔎 Сканування користувачів...",
        "⏳ Аналіз повідомлень...",
        "📡 З'єднання встановлено...",
        "🚨 КОРИСТУВАЧІ ЗНАЙДЕНІ 😂",
        "🤣 АХАХА, це просто тролінг!",
        "🤝 Все-все, мир 😎"
    ]

    try:
        for msg in messages:
            if not troll_active[chat_id]:
                break

            await send_to_chat(chat_id, msg)
            await asyncio.sleep(2)

    except asyncio.CancelledError:
        pass

    finally:
        troll_active[chat_id] = False


# =========================================================
# ХАОС
# =========================================================

async def chaos_scenario(chat_id):
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

    try:
        for msg in messages:
            if not troll_active[chat_id]:
                break

            await send_to_chat(chat_id, msg)
            await asyncio.sleep(1.5)

    except asyncio.CancelledError:
        pass

    finally:
        troll_active[chat_id] = False


# =========================================================
# КОМАНДИ У ЗБЕРЕЖЕНОМУ
# Глобальні перемикачі: +... / -...
# =========================================================

@client.on(events.NewMessage(outgoing=True))
async def global_commands(event):
    text = event.raw_text.strip()
    command = text.lower()

    # Глобальні перемикачі дозволяємо тільки із «Збереженого»
    is_saved_messages = event.chat_id == my_id

    if not is_saved_messages:
        return

    if command == "+антиспам":
        settings["antispam"] = True
        save_settings()
        await send_to_chat(my_id, "🛡️ Антиспам: 🟢 УВІМКНЕНО")
        return

    if command == "-антиспам":
        settings["antispam"] = False
        save_settings()
        await send_to_chat(my_id, "🛡️ Антиспам: 🔴 ВИМКНЕНО")
        return

    if command == "+автопривітання":
        settings["autogreeting"] = True
        save_settings()
        await send_to_chat(my_id, "👋 Автопривітання: 🟢 УВІМКНЕНО")
        return

    if command == "-автопривітання":
        settings["autogreeting"] = False
        save_settings()
        await send_to_chat(my_id, "👋 Автопривітання: 🔴 ВИМКНЕНО")
        return

    if command == "+автовідповідач":
        settings["autoreply"] = True
        save_settings()
        await send_to_chat(my_id, "🤖 Автовідповідач: 🟢 УВІМКНЕНО")
        return

    if command == "-автовідповідач":
        settings["autoreply"] = False
        save_settings()
        await send_to_chat(my_id, "🤖 Автовідповідач: 🔴 ВИМКНЕНО")
        return

    if command == "+сон":
        settings["sleep"] = True
        save_settings()
        await send_to_chat(
            my_id,
            "😴 Режим сну: 🟢 УВІМКНЕНО\n"
            "Вхідні повідомлення позначатимуться прочитаними, "
            "а відповідь буде: «Власник акаунта спить 😴»."
        )
        return

    if command == "-сон":
        settings["sleep"] = False
        save_settings()
        await send_to_chat(my_id, "😴 Режим сну: 🔴 ВИМКНЕНО")
        return

    if command == "+перевірка":
        await send_to_chat(
            my_id,
            "🛡️ Перевірка поки не підключена до цієї версії."
        )
        return

    if command == "-перевірка":
        await send_to_chat(
            my_id,
            "🛡️ Перевірка поки не підключена до цієї версії."
        )
        return

    # Встановлення автовідповіді через відповідь на повідомлення.
    if command == "встановити автовідповідь":
        if not event.is_reply:
            await send_to_chat(
                my_id,
                "❗ Спочатку надішли потрібне повідомлення, "
                "потім відповідай на нього командою:\n"
                "встановити автовідповідь"
            )
            return

        try:
            replied = await event.get_reply_message()

            settings["autoreply_text"] = replied.raw_text or ""

            entities = []
            if replied.entities:
                entities = [
                    entity.to_dict()
                    for entity in replied.entities
                ]

            settings["autoreply_entities"] = entities
            save_settings()

            await send_to_chat(
                my_id,
                "✅ Автовідповідь збережено разом із доступним "
                "форматуванням Telegram."
            )

        except Exception as e:
            await send_to_chat(
                my_id,
                f"❌ Не вдалося зберегти відповідь: {e}"
            )

        return

    if command == "статус":
        await send_to_chat(
            my_id,
            "⚙️ СТАТУС:\n\n"
            f"🛡️ Антиспам: {'🟢' if settings['antispam'] else '🔴'}\n"
            f"👋 Автопривітання: {'🟢' if settings['autogreeting'] else '🔴'}\n"
            f"🤖 Автовідповідач: {'🟢' if settings['autoreply'] else '🔴'}\n"
            f"😴 Сон: {'🟢' if settings['sleep'] else '🔴'}"
        )
        return


# =========================================================
# ЛОКАЛЬНІ КОМАНДИ В ЧАТІ
# Тільки твої вихідні повідомлення.
# =========================================================

@client.on(events.NewMessage(outgoing=True))
async def chat_commands(event):
    global mute_active

    text = event.raw_text.strip().lower()
    chat_id = event.chat_id

    # Глобальні команди вже обробляються вище.
    if chat_id == my_id:
        return

    if text == "тролл":
        await delete_message(event)
        start_troll(chat_id, troll_scenario)
        return

    if text == "хаос":
        await delete_message(event)
        start_troll(chat_id, chaos_scenario)
        return

    if text == "стоп":
        await delete_message(event)
        stop_troll(chat_id)
        await send_to_chat(chat_id, "🛑 Троллінг зупинено.")
        return

    if text == "мир":
        await delete_message(event)
        stop_troll(chat_id)
        await send_to_chat(chat_id, "🤝 МИР! Троллінг завершено 😂")
        return

    if text == "мут":
        await delete_message(event)
        mute_active[chat_id] = True
        await send_to_chat(chat_id, "🔇 Режим тиші увімкнено.")
        return

    if text == "стоп мут":
        await delete_message(event)
        mute_active[chat_id] = False
        await send_to_chat(chat_id, "🔊 Режим тиші вимкнено 😎")
        return


# =========================================================
# ВХІДНІ ПОВІДОМЛЕННЯ
# =========================================================

@client.on(events.NewMessage(incoming=True))
async def incoming_handler(event):
    chat_id = event.chat_id
    user_id = event.sender_id

    if user_id is None:
        return

    # -----------------------------------------------------
    # РЕЖИМ СНУ
    # -----------------------------------------------------

    if settings["sleep"]:
        try:
            await event.mark_read()
        except Exception:
            pass

        await send_to_chat(
            chat_id,
            "Власник акаунта спить 😴"
        )
        return

    # -----------------------------------------------------
    # МУТ У КОНКРЕТНОМУ ЧАТІ
    # -----------------------------------------------------

    if mute_active[chat_id]:
        await delete_message(event)
        return

    # -----------------------------------------------------
    # АВТОПРИВІТАННЯ
    # -----------------------------------------------------

    if settings["autogreeting"] and user_id not in greeted_users:
        greeted_users.add(user_id)

        await send_to_chat(
            chat_id,
            "Привіт! 👋 Радий тебе бачити 😊"
        )

    # -----------------------------------------------------
    # АВТОВІДПОВІДАЧ
    # -----------------------------------------------------

    if settings["autoreply"]:
        text = settings["autoreply_text"]
        entities = settings["autoreply_entities"]

        # Telethon приймає entity-словники назад через TLObject,
        # тому для простоти при помилці надсилаємо звичайний текст.
        try:
            await send_to_chat(
                chat_id,
                text,
                formatting_entities=entities or None
            )
        except Exception:
            await send_to_chat(chat_id, text)

    # -----------------------------------------------------
    # АНТИСПАМ
    # -----------------------------------------------------

    if not settings["antispam"]:
        return

    now = time.monotonic()
    queue = spam_messages[chat_id][user_id]

    queue.append(now)

    while queue and now - queue[0] > TIME_WINDOW:
        queue.popleft()

    if len(queue) <= MAX_MESSAGES:
        return

    warnings = spam_warnings[chat_id][user_id]

    if warnings < MAX_WARNINGS:
        spam_warnings[chat_id][user_id] += 1

        previous = last_warning[chat_id][user_id]

        if now - previous >= WARNING_COOLDOWN:
            last_warning[chat_id][user_id] = now

            await send_to_chat(
                chat_id,
                "⚠️ Будь ласка, не надсилай так багато "
                "повідомлень поспіль."
            )

        return

    await delete_message(event)


# =========================================================
# ЗАПУСК
# =========================================================

async def main():
    global my_id

    print("🤖 Telegram Helper запускається...")

    load_settings()

    await client.start()

    me = await client.get_me()
    my_id = me.id

    print("--------------------------------")
    print("✅ ПРОГРАМА ЗАПУЩЕНА")
    print(f"👤 Акаунт: {me.first_name}")
    print(f"🆔 ID: {me.id}")
    print("--------------------------------")
    print("Глобальні команди — у «Збереженому»:")
    print("+антиспам / -антиспам")
    print("+автопривітання / -автопривітання")
    print("+автовідповідач / -автовідповідач")
    print("+сон / -сон")
    print("встановити автовідповідь")
    print("статус")
    print("--------------------------------")
    print("Команди в чатах:")
    print("тролл | хаос | мир | стоп")
    print("мут | стоп мут")
    print("--------------------------------")

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
