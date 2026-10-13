import asyncio
import logging
import os
import time

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

# --- Настройки (задай через переменные окружения или впиши сюда) ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "8911863999:AAHaMSqRlJi6dlPphbWCSAkYSFeuhruXPxA")
# Либо @username публичного канала, либо числовой id вида -1001234567890
CHANNEL_ID = os.getenv("CHANNEL_ID", "-1004308451530")
# Антиспам: минимум секунд между сообщениями от одного пользователя
COOLDOWN_SECONDS = 300  # 5 минут

logging.basicConfig(level=logging.INFO)
dp = Dispatcher()
last_message_time: dict[int, float] = {}


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет! Напиши мне любое сообщение (текст, фото, видео, голосовое, "
        "стикер), и я анонимно опубликую его в канале https://t.me/podslushanoMKDK."
    )


@dp.message(F.chat.type == "private")
async def anonymous_post(message: Message, bot: Bot):
    user_id = message.from_user.id
    now = time.time()

    # Простой антиспам
    wait = COOLDOWN_SECONDS - (now - last_message_time.get(user_id, 0))
    if wait > 0:
        wait = int(wait) + 1
        minutes, seconds = divmod(wait, 60)
        await message.answer(
            f"⏳ Слишком часто! Следующее сообщение можно отправить "
            f"через {minutes} мин {seconds} сек."
        )
        return

    try:
        # copy_message отправляет контент без пометки "Переслано от..."
        await bot.copy_message(
            chat_id=CHANNEL_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
        )
        last_message_time[user_id] = now
        await message.answer("✅ Отправлено анонимно!")
    except Exception as e:
        logging.exception("Не удалось отправить в канал: %s", e)
        await message.answer("❌ Не получилось отправить. Попробуй позже.")


async def main():
    bot = Bot(token=BOT_TOKEN)
    me = await bot.get_me()
    print(f"✅ Бот запущен: @{me.username}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())