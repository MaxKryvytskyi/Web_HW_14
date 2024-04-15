import redis
import pickle


r = redis.Redis(host='localhost', port=6379, db=0)

def redis_get(read):
    result = r.get(str(read))
    return pickle.loads(result) if result else result

def redis_set(read, write):
    r.set(str(read), pickle.dumps(write))

def redis_expire(read, integer=10):
    r.expire(str(read), integer)
