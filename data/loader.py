from aiogram import Bot, Dispatcher
# from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data.confige import confige_file


# storage = RedisStorage2('localhost', 6379, db=5, pull_size=10, prefix='cafebot')
storage = MemoryStorage()
bot = Bot(token=confige_file['token'])
dp = Dispatcher(bot, storage=storage)

