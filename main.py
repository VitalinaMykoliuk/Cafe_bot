from data.confige import *
from data.loader import *
from heandlers.admin_function import *
from heandlers.user_function import *
from services.api_sqlite import *
import logging
from os import path
from aiogram import executor


logging.basicConfig(filename=path.join('data', 'log.txt'), level=logging.INFO, format="%(asctime)s %(message)s",
                    filemode="w")


if __name__ == '__main__':
    executor.start_polling(dp)
