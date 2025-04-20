# requests.py
import app.core.database.models as db
from sqlalchemy import select, update

class Query:
    def __init__(self, session) -> None:
        self.session = session

    async def check_post(self, post_link):
        async with self.session() as session:
            # Проверяем, существует ли ссылка в базе данных
            existing_post = await session.scalar(select(db.Posts).where(db.Posts.link == post_link))
            
            if existing_post is None:
                # Если ссылки нет, добавляем её в базу данных
                new_post = db.Posts(link=post_link)  # Предполагается, что у вас есть модель Posts с полем link
                session.add(new_post)
                await session.commit()  # Сохраняем изменения в базе данных
                print(f'\nДобавлен новый пост: {post_link}\n')

                return post_link
            else:
                if existing_post.status == 0:
                    print(f'\nПост существует, но не был отправлен: {post_link}\n')
                    
                    return post_link
        
    async def update_status(self, post_link):
        async with self.session() as session:
            # Обновляем статус существующего поста на 1
            await session.execute(update(db.Posts).where(db.Posts.link == post_link).values(status=1))
            await session.commit()