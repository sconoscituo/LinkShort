import random
import string
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.link import Link


def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


async def create_unique_code(db: AsyncSession, length: int = 6) -> str:
    for _ in range(10):
        code = generate_short_code(length)
        result = await db.execute(select(Link).where(Link.short_code == code))
        if not result.scalar_one_or_none():
            return code
    return generate_short_code(length + 2)
