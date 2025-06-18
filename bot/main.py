import os
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID"))
TOPIC_ID = int(os.getenv("TOPIC_ID"))
STATE_FILE = "state/message_id.txt"

bot = Bot(token=TOKEN)

message_text = (
    "<b>🔷 Что должно быть в посте:</b>\n"
    "<b>1. Название —</b> кратко отражает суть, например: «Набор чертежей для ситиблоков»\n"
    "<b>2. Описание —</b> что делает чертёж, какие задачи решает, можно указать эффективность (например, производство ресурсов в секунду).\n"
    "<b>3. Изображения —</b> от 1 до 5 скриншотов. Видео можно, но нежелательно.\n"
    "<b>4. Ссылка или файл —</b> <i>txt</i> чертежа для использования другими игроками.\n"
    "По желанию: <i>теги.</i>\n\n"
)

keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("📋 Инструкция", url="https://telegra.ph/CHertezhi-06-11"),
            InlineKeyboardButton("ℹ️ Подробнее", url="https://t.me/FCTostin/414/447")
        ]
    ]
)


def read_last_message_id() -> int:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return int(f.read().strip())
    return 0


def save_last_message_id(message_id: int):
    os.makedirs("state", exist_ok=True)
    with open(STATE_FILE, "w") as f:
        f.write(str(message_id))


async def send_test_message() -> int:
    msg = await bot.send_message(
        chat_id=GROUP_CHAT_ID,
        message_thread_id=TOPIC_ID,
        text="проверка, без звука",
        disable_notification=True,
    )
    return msg.message_id


async def delete_message(message_id: int):
    try:
        await bot.delete_message(chat_id=GROUP_CHAT_ID, message_id=message_id)
    except Exception as e:
        print(f"[WARN] Не удалось удалить сообщение {message_id}: {e}")


async def send_main_message() -> int:
    msg = await bot.send_message(
        chat_id=GROUP_CHAT_ID,
        message_thread_id=TOPIC_ID,
        text=message_text,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_notification=True
    )
    return msg.message_id


async def main():
    last_main_id = read_last_message_id()

    print(f"[INFO] Предыдущее сообщение ID: {last_main_id}")
    test_id = await send_test_message()
    print(f"[INFO] Тестовое сообщение ID: {test_id}")

    await delete_message(test_id)

    if test_id > last_main_id + 1:
        print("[INFO] Обнаружены другие сообщения — обновляем...")
        await delete_message(last_main_id)
        new_main_id = await send_main_message()
        save_last_message_id(new_main_id)
        print(f"[INFO] Отправлено новое сообщение ID: {new_main_id}")
    else:
        print("[INFO] Других сообщений не было — пропускаем.")

if __name__ == "__main__":
    asyncio.run(main())
