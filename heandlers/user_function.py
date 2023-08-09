import asyncio
from data.confige import *
from data.loader import *
from heandlers.admin_function import *
from services.api_sqlite import *
import logging
from os import path
from aiogram.dispatcher import FSMContext
from aiogram import executor, types
from key_boards.user_key_boards import *
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
import re

users_cafe = Users()
menu_cafe = Menu()


@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.answer(f"Вас приветствует кафе *HAPPY* !!!\nВыберите действие:",
                                                    reply_markup=menu_for_user, parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(text="🍽 Посетить кафе")
async def visit_cafe(message: types.Message):
    await message.answer(text='▪ Введите дату на когда хотите забронировать столик в формате ДД-ММ-ГГГГ '
                              '(например, 14-07-2023):',
                         reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("Назад"))
    await storage.set_state(chat=message.from_user.id, state='reservation')


@dp.message_handler(state='reservation')
async def reservation(message: types.Message, state: FSMContext):
    if message.text.lower() == 'назад':
        await message.answer('© Главное меню.', reply_markup=menu_for_user)
        await state.finish()
        return
    try:
        selected_date = datetime.strptime(message.text, '%d-%m-%Y')
    except ValueError:
        await message.answer('Некорректный формат даты. Введите дату в формате ДД-ММ-ГГГГ (например, 14-07-2023).')
        return
    await state.update_data(selected_date=message.text)
    await message.answer('Введите ваш номер телефона в формате +XXXXXXXXXXX (например, +380663839245): ')
    await state.set_state(state='numbers')


@dp.message_handler(state='numbers')
async def numbers(message: types.Message, state: FSMContext):
    if message.text.lower() == 'назад':
        await message.answer('© Главное меню.', reply_markup=menu_for_user)
        await state.finish()
        return
    phone_number = message.text.strip()
    phone_regex = r'^\+?[1-9]\d{1,14}$'
    if not re.match(phone_regex, phone_number):
        await message.answer('Некорректный номер телефона. Пожалуйста, введите номер в формате +XXXXXXXXXXX')
        return
    await state.update_data(selected_number=message.text)
    await message.answer('Введите ваше имя: ')
    await state.set_state(state='name')


@dp.message_handler(state='name')
async def name(message: types.Message, state: FSMContext):
    if message.text.lower() == 'назад':
        await message.answer('© Главное меню.', reply_markup=menu_for_user)
        await state.finish()
        return
    name_pattern = r'^[A-Za-zА-Яа-яЁё\s]+$'
    if not re.match(name_pattern, message.text):
        await message.answer('Некорректный формат имени. Пожалуйста, введите корректное имя.')

    await state.update_data(selected_name=message.text)
    data = await state.get_data()

    await message.answer(f'Ваш столик зарезервирован:\nПроверте корректность ваших данных\n'
                         f'Дата брони: {data["selected_date"]}\n'
                         f'Номер телефона: {data["selected_number"]}\n'
                         f'Ваше имя: {data["selected_name"]}')
    await asyncio.sleep(1.5)
    await message.answer('Подтверджаете ли вы свои данные?\n\n✍ Напишите ваш ответ:\n*Да* или *Нет*',
                                                                                   parse_mode=types.ParseMode.MARKDOWN)
    await state.set_state(state='result_1')


@dp.message_handler(state='result_1')
async def yes(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text.lower() == 'да':
        users_cafe.add_user(data['selected_name'], data['selected_number'], data["selected_date"])
        await message.answer('Данные подтверждены!!!\n\n© Главное меню.', reply_markup=menu_for_user)
        await state.finish()
    elif message.text.lower() == 'нет':
        await message.answer('Вы не подтвердили свои данные!\n\n© Главное меню!', reply_markup=menu_for_user,
                                                                                  parse_mode=types.ParseMode.MARKDOWN)
        await state.finish()
    else:
        await message.answer('Некорректный ответ!!!\n\n✍ Напишите ваш ответ:\n*Да* или *Нет*',
                                                                                   parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(text="📦 Заказать доставку")
async def order_delivery(message: types.Message):
    menu_text = (
        "Меню кафе *HAPPY*! Выберите блюда, которые хотите заказать:\n\n"
        "*🍕 Пицца*\n(Маргарита, Карбонара, Четыре сезона)\n\n"
        "*🍝 Паста*\n(Кампанелле, Каннеллони, Казаречче, Каватаппи)\n\n"
        "*🥗 Салат*\n(Цезарь, Греческий, Овощной)\n\n"
        "*🍰 Десерт*\n(Тирамису, Чизкейк, Наполеон, Медовик)\n\n"
        "*🍹 Напитки*\n(*Горячие напитки*: черный чай, зеленый чай, латте, капучино.\n*Холодные напитки:*"
        " молочный коктейль,"
        "апельсиновый сок, яблочный сок, кока-кола, спрайт)\n\n*✍️Напишите выбранные позиции:*"
    )
    await message.answer(text=menu_text, reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("Назад"),
                         parse_mode=types.ParseMode.MARKDOWN)
    await storage.set_state(chat=message.from_user.id, state='menu')


@dp.message_handler(state='menu')
async def menu(message: types.Message, state: FSMContext):
    if message.text.lower() == 'назад':
        await message.answer('© Главное меню.', reply_markup=menu_for_user)
        await state.finish()
        return
    await state.update_data(selected_menu=message.text)
    data = await state.get_data()
    print(data)
    await message.answer(f"Вы выбрали: {message.text}.")
    await message.answer('Введите ваш номер телефона в формате +XXXXXXXXXXX (например, +380663839245):')
    await state.set_state(state='numbers_two')


@dp.message_handler(state='numbers_two')
async def numbers(message: types.Message, state: FSMContext):
    if message.text.lower() == 'назад':
        await message.answer('© Главное меню.', reply_markup=menu_for_user)
        await state.finish()
        return
    phone_number = message.text.strip()
    phone_regex = r'^\+?[1-9]\d{1,14}$'
    if not re.match(phone_regex, phone_number):
        await message.answer('Некорректный номер телефона. Пожалуйста, введите номер в формате +XXXXXXXXXXX')
        return
    await state.update_data(selected_number2=message.text)
    await message.answer('Введите ваше имя: ')
    await state.set_state(state='name_two')


@dp.message_handler(state='name_two')
async def name(message: types.Message, state: FSMContext):
    if message.text.lower() == 'назад':
        await message.answer('© Главное меню.', reply_markup=menu_for_user)
        await state.finish()
        return
    name_pattern = r'^[A-Za-zА-Яа-яЁё\s]+$'
    if not re.match(name_pattern, message.text):
        await message.answer('Некорректный формат имени. Пожалуйста, введите корректное имя.')

    await state.update_data(selected_name2=message.text)
    data = await state.get_data()
    print(data)
    await message.answer('Введите ваш адрес(город, улица, номер дома, номер квартиры/комнаты): ')
    await state.set_state(state='address')


@dp.message_handler(state='address')
async def address(message: types.Message, state: FSMContext):
    if message.text.lower() == 'назад':
        await message.answer('© Главное меню.', reply_markup=menu_for_user)
        await state.finish()
        return
    user_address = message.text
    await message.answer(f"Вы ввели адрес: {user_address}. Ваш заказ обрабатывается...")
    await state.update_data(selected_address=message.text)
    data = await state.get_data()
    print(data)
    await message.answer(f'Ваш заказ обработан:\n{data["selected_menu"]}\n'
                         f'Ваш номер телефона: {data["selected_number2"]}\n'
                         f'Ваше имя: {data["selected_name2"]}\n'
                         f'Ваш адрес: {data["selected_address"]}')
    await asyncio.sleep(1.5)
    await message.answer('Подтверджаете ли вы свой заказ?\n\n✍ Напишите ваш ответ:\n*Да* или *Нет*',
                                                                                  parse_mode=types.ParseMode.MARKDOWN)
    await state.set_state(state='result')


@dp.message_handler(state='result')
async def yes_yes(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text.lower() == 'да':
        menu_cafe.add_info_menu(data['selected_menu'], data['selected_number2'], data['selected_name2'],
                                                                                              data['selected_address'])
        await message.answer('Спасибо что выбрали *"HAPPY"*\nВаш заказ будет доставлен на указанный адрес через'
                              '40 минут!\n' 'Ожидайте, с вами свяжется курьер\nХорошего дня!\n\n*© Главное меню!*',
                              reply_markup=menu_for_user,  parse_mode=types.ParseMode.MARKDOWN)
        await state.finish()
    elif message.text.lower() == 'нет':
        await message.answer('Вы не подтвердили заказ!\n\n*© Главное меню!*', reply_markup=menu_for_user,
                                                                                   parse_mode=types.ParseMode.MARKDOWN)
        await state.finish()
    else:
        await message.answer('Некорректный ответ!!!\n\n✍ Напишите ваш ответ:\n*Да* или *Нет*',
                                                                                   parse_mode=types.ParseMode.MARKDOWN)













