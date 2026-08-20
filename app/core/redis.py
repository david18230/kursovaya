import os
import redis.asyncio as aioredis

redis_client = aioredis.from_url(os.getenv("REDIS_URL"))
async def get_cache(key):
    return await redis_client.get(key)

async def set_cache(key, value, ttl = 300):
    await redis_client.set(key, value, ex=ttl)

async def delete_pattern(pattern = "rooms:filter"):
    keys = await redis_client.keys(pattern)
    if keys:
        await redis_client.delete(*keys)
async def increment(key):
    return await redis_client.incr(key)

async def is_rate_limited(key, max_attempts, ttl):
    current = await redis_client.get(key)

    if current is None:
        await redis_client.set(key, 1, ex = ttl)
        return False
    current = int(current)
    if current >= max_attempts:
        return True
    await redis_client.incr(key)
    return False

async def incr_online():
    await redis_client.incr("online_users")

async def decr_online():
    await redis_client.decr("online_users")

async def exists_key(key: str) -> bool:
    return await redis_client.exists(key)

async def add_booking_to_rating(room_id):
    return await redis_client.zincrby("rating:rooms", 1, f"room: {room_id}")

async def reset_online():
    await redis_client.set("online_users", 0)
