from rq import Worker, Queue
from redis import Redis
from .config import settings

redis_conn = Redis.from_url(settings.redis_url)

if __name__ == "__main__":
    worker = Worker([Queue(connection=redis_conn)], connection=redis_conn)
    worker.work()
