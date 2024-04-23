from fastapi import FastAPI
import redis.asyncio as redis
from contextlib import asynccontextmanager
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler


r = None
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(server: FastAPI):
    global r
    global limiter
    
    server.state.limiter = limiter
    server.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    r = await redis.Redis(host='localhost', port=6379, db=0, encoding="utf-8", decode_responses=True)
    yield
    r.close()

server = FastAPI(lifespan=lifespan)