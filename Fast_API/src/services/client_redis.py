import redis
import pickle


class ClientRedis:

    r = redis.Redis(host='localhost', port=6379, db=0)
    async def redis_get(self, read):
        result = self.r.get(str(read))
        return pickle.loads(result) if result else result

    async def redis_set(self, read, write):
        self.r.set(str(read), pickle.dumps(write))

    async def redis_expire(self, read, integer=30):
        self.r.expire(str(read), integer)

client_redis = ClientRedis()