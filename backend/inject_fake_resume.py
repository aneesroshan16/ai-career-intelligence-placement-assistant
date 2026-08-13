import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.modules.resumes.models import Resume
from app.modules.users.models import User

async def run():
    async with AsyncSessionLocal() as session:
        u = (await session.execute(select(User).limit(1))).scalar_one_or_none()
        if not u:
            u = User(email='test@example.com', full_name='Test User')
            session.add(u)
            await session.flush()
            
        r = (await session.execute(select(Resume).limit(1))).scalar_one_or_none()
        if not r:
            r = Resume(user_id=u.id, storage_url='http://fake.url', original_filename='fake.pdf', parsed_text='Python SQL AWS Docker Fastapi React Javascript Typescript')
            session.add(r)
            
        await session.commit()

asyncio.run(run())
