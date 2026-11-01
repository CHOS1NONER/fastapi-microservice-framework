import asyncio

import bcrypt


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


async def hash_password(password: str) -> str:
    # bcrypt 是 CPU 密集计算，放进线程池，避免堵住事件循环
    return await asyncio.to_thread(_hash_password, password)


async def verify_password(password: str, hashed_password: str) -> bool:
    return await asyncio.to_thread(_verify_password, password, hashed_password)
