import asyncio
import aiohttp
import feedparser

class Parse:
    def __init__(self, rss_urls, disk, file_ban_categories):
        self.rss_urls = rss_urls
        self.articles = {url: [] for url in rss_urls}
        self.article_details = {}
        self.disk = disk
        self.file_ban_categories = file_ban_categories

    async def fetch_rss(self, session, url):
        headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                'Accept': 'application/rss+xml, application/xml;q=0.9, */*;q=0.8',
            }
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f'Failed to fetch {url}: {response.status}')
                    return None
        except aiohttp.ClientError as e:
            print(f'Client error occurred while fetching {url}: {e}')
        except asyncio.TimeoutError:
            print(f'Timeout error occurred while fetching {url}')
        except Exception as e:
            print(f'An unexpected error occurred while fetching {url}: {e}')
        return None

    async def parse_rss(self, url):
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            rss_content = await self.fetch_rss(session, url)
            if rss_content:
                feed = feedparser.parse(rss_content)
                self.articles[url] = []  # Инициализация списка для статей
                exclude_categories = await self.disk.get_ban_categories(self.file_ban_categories)  # Используем полученные запрещенные категории
                for entry in feed.entries[:5]:
                    if 'category' in entry and entry.category in exclude_categories:
                        continue
                    self.articles[url].append(entry.link)

            else:
                print(f'No content fetched for {url}')

    async def fetch_article_details(self, rss_url, links):
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            rss_content = await self.fetch_rss(session, rss_url)
            if rss_content:
                feed = feedparser.parse(rss_content)
                for entry in feed.entries:
                    if entry.link in links:
                        title = entry.title if 'title' in entry else 'Нет заголовка'
                        published = entry.published if 'published' in entry else 'Нет даты'
                        description = entry.summary if 'summary' in entry else 'Нет описания'
                        categories = entry.tags if 'tags' in entry else []
                        categories = [category.term for category in categories] if categories else []
                        self.article_details[entry.link] = {
                            'title': title,
                            'published': published,
                            'description': description,
                            'categories': categories
                        }
            else:
                print(f'No content fetched for {rss_url}')

    async def get_articles(self):
        tasks = [self.parse_rss(url) for url in self.rss_urls]
        await asyncio.gather(*tasks)

        result = {}
        for rss_url, links in self.articles.items():
            result[rss_url] = {}
            await self.fetch_article_details(rss_url, links)
            for link in links:
                if link in self.article_details:
                    result[rss_url][link] = self.article_details[link]

        return result