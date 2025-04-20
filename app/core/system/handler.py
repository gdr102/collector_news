import asyncio

from app.core.database.requests import Query

class Handler:
    def __init__(self, async_session):
        self.db_session = Query(async_session)
        self.event = asyncio.Event()

    async def check_post(self, links):
        return await self.db_session.check_post(links)
    
    async def update_status(self, link):
        return await self.db_session.update_status(link)
    
    async def main(self, articles_data: dict):
        # Предположим, что check_post возвращает True, если пост существует, и False в противном случае
        valid_links = []  # Список для хранения валидных ссылок

        # Проверяем каждую ссылку
        for rss_url, posts in articles_data.items():
            for post_link in posts.keys():
                if await self.check_post(post_link):  # Проверяем, существует ли пост
                    valid_links.append(post_link)

        # Фильтруем articles_data, оставляя только валидные ссылки
        for rss_url in articles_data.keys():
            articles_data[rss_url] = {link: articles_data[rss_url][link] for link in articles_data[rss_url] if link in valid_links}

        return articles_data  # Возвращаем обновленный словарь

            