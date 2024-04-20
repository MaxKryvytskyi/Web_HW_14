import redis
import pickle
from typing import Any

class ClientRedis:
    """
    A client for interacting with a Redis database.

    Attributes:
        r (redis.Redis): The Redis client instance.
    """
    r = redis.Redis(host='localhost', port=6379, db=0)
    
    async def redis_get(self, read) -> Any | None:
        """
        Retrieves data from Redis based on the provided key.

        Args:
            read: The key used to retrieve data from Redis.

        Returns:
            Any: The deserialized data retrieved from Redis, or None if the key does not exist.
        """
        result = self.r.get(str(read))
        return pickle.loads(result) if result else result

    async def redis_set(self, read, write):
        """
        Stores data in Redis with the provided key.

        Args:
            read: The key used to store data in Redis.
            write: The data to be stored in Redis.
        """
        self.r.set(str(read), pickle.dumps(write))

    async def redis_expire(self, read, integer=3600):
        """
        Sets an expiration time for a key in Redis.

        Args:
            read: The key for which the expiration time will be set.
            integer (int): The expiration time in seconds. Defaults to 300 seconds (5 minutes).
        """
        self.r.expire(str(read), integer)

client_redis = ClientRedis()