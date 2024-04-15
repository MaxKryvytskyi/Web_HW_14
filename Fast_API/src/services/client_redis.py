import redis
import pickle


r = redis.Redis(host='localhost', port=6379, db=0)

def redis_get(read):
    print("1")
    result = r.get(str(read))
    print("2")
    print(result)
    print("3")
    return pickle.loads(result) if result else result

def redis_set(read, write):
    print("4")
    result = r.set(str(read), pickle.dumps(write))
    print("5")
    print(result)
    print("6")

def redis_expire(read, integer=10):
    print("7")
    result = r.expire(str(read), integer)
    print("8")
    print(result)
    print("9")