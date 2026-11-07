import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
async def make_pool():
    return await asyncpg.create_pool(DATABASE_URL)
    