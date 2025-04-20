import asyncio
import json

from telethon import TelegramClient

from app.core.database.requests import Query
from app.core.system.translate import translate_yandex
from app.core.system.functions import clean_html


class Client:
    def __init__(self, session, api_id, api_hash) -> None:
        self.client = TelegramClient(session, api_id, api_hash) # anon

    async def start(self, phone_number):
        if self.client.is_connected():
            print('Клиент уже запущен')
            return
        
        await self.client.start(phone=phone_number)
        

    async def send_message(self, channel: str, articles_data: dict, FOLDER_ID, KEY_SECRET, handler):
        try:
            for url_rss, links in articles_data.items():
                if len(links) != 0:
                    for link, values in links.items():
                        source = f'Источник: {link}'

                        title = values['title']
                        date = values['published']
                        description = values['description']
                        categories = values['categories']

                        categories_list = [category.replace(' ', '') for category in categories]
                        categories_str = '\n\n' + ', '.join([f'#{category}' for category in categories_list]) if categories_list else ''

                        text_msg = clean_html(f'**{title}**\n\n{date}\n\n{description}\n\n{source}')

                        result = await translate_yandex(FOLDER_ID, KEY_SECRET, text_msg)
                        # Парсим JSON
                        data = json.loads(result)

                        # Извлекаем текст
                        text = data['translations'][0]['text'] + categories_str

                        send = await self.client.send_message(channel, text)

                        if send:
                            await handler.update_status(link)
                            print('Отправлено успешно!')
                        else:
                            print('Сообщение не было отправлено!')

                        await asyncio.sleep(3)

        except Exception as e:
            print(f'Ошибка при отправке сообщения: {e}')


    async def disconnect(self):
        if self.client.is_connected():
            self.client.disconnect()
        else:
            print('Клиент не подключен')

    