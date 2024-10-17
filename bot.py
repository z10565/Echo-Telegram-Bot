import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types.input_file import FSInputFile
from config_reader import config
from PIL import Image, ImageOps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

SAVE_DIR = "saved_photos"
os.makedirs(SAVE_DIR, exist_ok=True)

def apply_grayscale(image_path):
    img = Image.open(image_path)
    grayscale_img = img.convert("L") 
    grayscale_path = os.path.splitext(image_path)[0] + "_grayscale.jpg"
    grayscale_img.save(grayscale_path)
    return grayscale_path

def apply_negative(image_path):
    img = Image.open(image_path)
    negative_img = ImageOps.invert(img.convert("RGB"))  
    negative_path = os.path.splitext(image_path)[0] + "_negative.jpg"
    negative_img.save(negative_path)
    return negative_path

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user = message.from_user
    username = user.username if user.username else user.first_name
    await message.answer(f"👋 Привет {username}! Я бот, который сохраняет и пересылает отправленную информацию, также я могу применять фильтры к фото. \n"
        "Отправь мне фотографию, и я сделаю её черно-белой или негативной.")
    
@dp.message(F.text)
async def echo(message: Message):
    if not message.text.startswith('/'):
        await message.answer(message.text)
        
@dp.message(F.photo)
async def handle_photo(message: Message):
    try:
        photo = message.photo[-1]
        file_id = photo.file_id
        file = await bot.get_file(file_id)

        file_extension = os.path.splitext(file.file_path)[1] or ".jpg"
        file_path = os.path.abspath(os.path.join(SAVE_DIR, f"{file_id}{file_extension}"))

        await bot.download_file(file.file_path, destination=file_path)
        logger.info(f"Файл сохранён по пути: {file_path}")

        grayscale_path = apply_grayscale(file_path)
        input_file_grayscale = FSInputFile(grayscale_path)
        await bot.send_photo(chat_id=message.chat.id, photo=input_file_grayscale, caption="Вот ваше фото в черно-белом варианте!")

        negative_path = apply_negative(file_path)
        input_file_negative = FSInputFile(negative_path)
        await bot.send_photo(chat_id=message.chat.id, photo=input_file_negative, caption="А вот оно в негативном фильтре!")

    except Exception as e:
        logger.error(f"Error in handle_photo: {e}")
        await message.answer("Произошла ошибка при обработке фотографии.")

@dp.message(F.document)
async def echo_file(message: Message):
    try:
        document = message.document
        file_id = document.file_id
        await bot.send_document(chat_id=message.chat.id, document=file_id, caption="Вот ваш документ!")
    except Exception as e:
        logger.error(f"Error in echo_file: {e}")
        await message.answer("Произошла ошибка при обработке документа.")

async def main():
    logger.info("Start polling")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
