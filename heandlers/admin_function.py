from data.loader import *
from data.confige import *
from services.api_sqlite import *
from aiogram import types

users_cafe = Users()


@dp.message_handler(text='🗒 Статистика')
async def static(message: types.Message):
    await message.answer(f'Количество юзеров: {len([user for user in users_cafe])}')