import os
import whisper
import ffmpeg
import easyocr
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.storage.memory import MemoryStorage

# Инициализация моделей
whisper_model = whisper.load_model("small")
reader = easyocr.Reader(['ru'])

# Конфигурация бота
BOT_TOKEN = "7051450602:AAFltVCU1XL1AyCvpWD5XeEoHV1ROfuts4Y"

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# ========== Обработчики команд ==========
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Добро пожаловать в бот-конвертер!\n\n"
        "<b>Я умею:</b>\n"
        "• 🔊 Аудио → текст\n"
        "• 🎥 Видео → текст\n"
        "• 📸 Фото → текст\n\n"
        "Просто отправьте мне файл нужного типа!",
        parse_mode="HTML"
    )


# ========== Обработчики файлов ==========
@dp.message(lambda m: m.content_type == ContentType.AUDIO)
async def handle_audio(message: Message):
    try:
        file = await bot.get_file(message.audio.file_id)
        file_path = f"temp_{message.audio.file_id}.mp3"

        await bot.download_file(file.file_path, destination=file_path)
        text = await asyncio.to_thread(audio_to_text, file_path)

        os.remove(file_path)
        await message.reply(f"🔊 Текст:\n{text}")
    except Exception as e:
        await message.reply(f"⚠️ Ошибка обработки аудио: {str(e)}")


@dp.message(lambda m: m.content_type == ContentType.VIDEO)
async def handle_video(message: Message):
    try:
        file = await bot.get_file(message.video.file_id)
        file_path = f"temp_{message.video.file_id}.mp4"

        await bot.download_file(file.file_path, destination=file_path)
        text = await asyncio.to_thread(video_to_text, file_path)

        os.remove(file_path)
        await message.reply(f"🎥 Текст из видео:\n{text}")
    except Exception as e:
        await message.reply(f"⚠️ Ошибка обработки видео: {str(e)}")


@dp.message(lambda m: m.content_type == ContentType.PHOTO)
async def handle_photo(message: Message):
    try:
        file = await bot.get_file(message.photo[-1].file_id)
        file_path = f"temp_{message.photo[-1].file_id}.jpg"

        await bot.download_file(file.file_path, destination=file_path)
        text = await asyncio.to_thread(image_to_text, file_path)

        os.remove(file_path)
        await message.reply(f"📸 Текст на фото:\n{text}")
    except Exception as e:
        await message.reply(f"⚠️ Ошибка обработки фото: {str(e)}")


# ========== Вспомогательные функции ==========
def audio_to_text(audio_path: str) -> str:
    result = whisper_model.transcribe(audio_path, language="ru")
    return result["text"]


def video_to_text(video_path: str) -> str:
    audio_path = "temp_audio.mp3"
    ffmpeg.input(video_path).output(audio_path, ac=1, ar=16000).run(quiet=True)
    text = audio_to_text(audio_path)
    os.remove(audio_path)
    return text


def image_to_text(image_path: str) -> str:
    result = reader.readtext(image_path, detail=0, paragraph=True)
    return "\n".join(result)


# ========== Запуск бота ==========
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
