import asyncio
import datetime
from api import async_get


if __name__ == '__main__':
    start = datetime.datetime.now()
    asyncio.run(async_get())
    print(datetime.datetime.now() - start)
