import asyncio
from app.core.config import get_settings
from sqlalchemy.ext.asyncio import create_async_engine

async def test():
    engine = create_async_engine(get_settings().DATABASE_URL)
    async with engine.connect() as conn:
        print('Connected successfully!')

asyncio.run(test())
