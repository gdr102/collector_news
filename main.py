import os
import asyncio
import schedule
from datetime import datetime
from dotenv import load_dotenv

from app.core.system.parse import Parse
from app.core.system.client import Client
from app.core.system.handler import Handler
from app.core.system.disk import YandexDisk
from app.core.database.models import async_main, async_session

load_dotenv()

# Параметры для подключения
SESSION = os.getenv('SESSION')  # SESSION TG
API_ID = os.getenv('API_ID')  # API_ID TG
API_HASH = os.getenv('API_HASH')  # API_HASH TG
PHONE_NUMBER = os.getenv('PHONE_NUMBER')  # номер телефона

channel = os.getenv('CHANNEL')  # куда постить

FOLDER_ID = os.getenv('FOLDER_ID') # YA_ID
KEY_SECRET = os.getenv('KEY_SECRET') # KEY_SECRET

DISK_ID = os.getenv('DISK_ID') # DISK_ID
DISK_SECRET = os.getenv('DISK_SECRET') # DISK_SECRET
DISK_TOKEN = os.getenv('DISK_TOKEN') # DISK_TOKEN

FILE_SOURCE = os.getenv('FILE_SOURCE') # FILE_SOURCE
FILE_BAN_CATEGORIES = os.getenv('FILE_BAN_CATEGORIES') # BAN_CATEGORIES


async def main():
    print(f"Current server time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Создаем подключение к клиенту
    client = Client(SESSION, API_ID, API_HASH)

    # Подключение к яндекс диску
    disk = YandexDisk(DISK_ID, DISK_SECRET, DISK_TOKEN)
    await disk.init_client()  # Инициализируем клиента
    
    try:
        # Авторизация в тг по номеру
        await client.start(PHONE_NUMBER)

        # Получение списка источников
        rss_urls = await disk.get_sources(FILE_SOURCE)

        # Получаем последние 5 статей с каждого источника
        parser = Parse(rss_urls, disk, FILE_BAN_CATEGORIES)
        articles_data = await parser.get_articles()

        # Создаем таблицы в базе данных
        await async_main()

        handler = Handler(async_session)
        result = await handler.main(articles_data)

        await client.send_message(channel, result, FOLDER_ID, KEY_SECRET, handler)
    finally:
        await client.disconnect()

async def job_wrapper():
    try:
        await main()
    except Exception as e:
        print(f"Error occurred: {e}")

async def schedule_jobs():
    # Запускаем задачу каждые 3 минуты
    schedule.every(3).minutes.do(lambda: asyncio.create_task(job_wrapper()))

    while True:
        schedule.run_pending()
        print(f"Current server time in loop: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", end="\r")
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(schedule_jobs())
