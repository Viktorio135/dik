import os
import json
import string
import random
import threading
import requests
import dill as pickle


from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.deep_linking import get_start_link, decode_payload
from aiogram.types import ContentType

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from functools import wraps
from dotenv import load_dotenv


from states import user_states, admin_states
from keyboards.user_keyboards import *
from keyboards.admin_keyboard import *
from database.db_commands import *



load_dotenv()
user_token = os.getenv('token')
PAYMENTS_PROVIDER_TOKEN = os.getenv('PAYMENT_TOKEN')
CHANNEL_ID=os.getenv('CHANNEL_ID')

bot = Bot(token=user_token, parse_mode='HTML', disable_web_page_preview=True)
dp = Dispatcher(bot, storage=MemoryStorage())

carts = {}
promo_in_carts ={}


def admin_access(func):
    @wraps(func)
    async def wrapped(message: types.Message, *args, **kwargs):
        admin_sp = await get_admin_list()
        if str(message.from_user.id) not in admin_sp:
            return
        return await func(message, *args, **kwargs)
    return wrapped







@dp.message_handler(commands='start', state='*')
async def cmd_start(msg: types.Message, state=None):
    if state is not None:  # Проверяем, находится ли пользователь в каком-либо состоянии
        await state.finish()  # Завершаем текущее состояние
    if not(await has_register(msg.from_user.id)):
        await bot.send_message(
            msg.from_user.id,
            'Здравствуйте, вы попали в Фабрика Мебели ДИК\nВведите свое имя:'
        )
        await user_states.Registration.name.set()
    else:
        await main_menu(msg)


@dp.message_handler(state=user_states.Registration.name)
async def registration_state_name(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = msg.text
    await bot.send_message(
        msg.from_user.id,
        'Отлично, теперь введите свой номер телефона:',
        reply_markup=get_contact_kb()
    )
    await user_states.Registration.phone_number.set()


@dp.message_handler(content_types=[types.ContentType.CONTACT, types.ContentType.TEXT], state=user_states.Registration.phone_number)
async def registration_state_phone(msg: types.Message, state: FSMContext):
    if msg.contact is not None:
        async with state.proxy() as data:
            data["phone_number"] = msg.contact.phone_number
    else:
        async with state.proxy() as data:
            data["phone_number"] = msg.text
    await state.finish()
    if await create_user(user_id=str(msg.from_user.id) , name=data["name"], phone=data["phone_number"], user_name=msg.from_user.username):
        carts[msg.from_user.id] = {}
        # webhook_url = 'https://b24-j63d76.bitrix24.ru/rest/1/zmz3l3ypfo3o79qp/'

        # # Метод API, который вы хотите вызвать
        # method = 'crm.contact.add'

        # # Параметры запроса (если есть)
 

        # # Формируем полный URL для запроса
        # url = f'{webhook_url}{method}'

        # # Выполняем GET-запрос
        # contact_data = {
        #     'fields': {
        #         'NAME': data['name'],
        #         'SECOND_NAME': str(msg.from_user.id),
        #         'LAST_NAME': str(msg.from_user.username),
        #         'TYPE_ID': 'CLIENT',
        #         'SOURCE_ID': 'CALL',
        #         'HAS_PHONE': 'Y',
        #         'HAS_EMAIL': 'N',
        #         'ASSIGNED_BY_ID': '1',
        #         'OPENED': 'Y',
        #         'PHONE': [
        #             {
        #                 'VALUE': data['phone_number'],
        #                 'VALUE_TYPE': 'WORK'
        #             }
        #         ]
        #     },
        #     'params': {
        #         'REGISTER_SONET_EVENT': 'Y'
        #     }
        # }

        # # Выполняем POST-запрос
        # response = requests.post(url, json=contact_data)

        # # Проверяем статус ответа
        # if response.status_code == 200:
        #     data = response.json()
        #     if 'result' in data:
        #         contact_id = data['result']
        #         print(f'Contact created with ID: {contact_id}')
        #     else:
        #         print('Error:', data)
        # else:
        #     print(f'Error: {response.status_code}')
        #     print(response.text)
        await main_menu(msg)
    else:
                await bot.send_message(
                    msg.from_user.id,
                    'Что-то  пошло не так'
                )


async def main_menu(msg: types.Message):
    await bot.send_message(
        msg.from_user.id,
        'Выберите',
        reply_markup=main_menu_kb()
    )


@dp.message_handler(lambda message: message.text == '📝 Каталог', state='*')
async def menu(msg: types.Message, state=None):
    if state is not None:  # Проверяем, находится ли пользователь в каком-либо состоянии
        await state.finish()  # Завершаем текущее состояние
    await bot.send_message(
        msg.from_user.id,
        'Выберите категорию',
        reply_markup=await get_category_kb(),
    )

@dp.callback_query_handler(lambda c: 'menu_in_category' in c.data)
async def subcat_in_cat(callbcak_query: types.CallbackQuery):
    cat_name = callbcak_query.data.split(':')[1]
    await callbcak_query.message.edit_text(
        'Выберите подкатегорию',
        reply_markup=await get_subcategory_kb(cat=cat_name)
    )

@dp.callback_query_handler(lambda c: 'menu_in_subcat' in c.data)
async def menu_in_cat(callback_query: types.CallbackQuery, place=0, cat_name=None, subcat_name=None):
    if not cat_name and not subcat_name:
        cat_name = callback_query.data.split(':')[1]
        subcat_name = callback_query.data.split(':')[2]
    furniturees = await get_furniturees_in_category(cat_name, subcat_name)
    if furniturees:
        furniture_data = await get_furniture_data(furniturees[place])
        if furniturees[place] not in carts[callback_query.from_user.id]:
            if callback_query.message.photo:
                await callback_query.message.edit_media(
                    media=types.InputMediaPhoto(
                        open(f'static/{furniture_data["photo"]}', 'rb'),
                        f'{furniture_data["name"]}\n\nЦена: {"<s>" + str(furniture_data["price"]) + "</s>" + "  " + str(furniture_data["price"]-furniture_data["price"]*(furniture_data["discount"]/100)) if furniture_data["discount"] != 0 else furniture_data["price"]}₽\n\n{furniture_data["description"]}\n\nХарактеристики: {furniture_data["composition"]}',
                    ),
                    reply_markup=get_furniturees_in_category_kb(cat_name, place, is_first=True, subcat=subcat_name)
                )
            else:
                await callback_query.message.delete()
                await bot.send_photo(
                    callback_query.from_user.id,
                    photo=types.InputFile(
                        open(f'static/{furniture_data["photo"]}', 'rb'),
                    ),
                    caption=f'{furniture_data["name"]}\n\nЦена: {"<s>" + str(furniture_data["price"]) + "</s>" + "  " + str(furniture_data["price"]-furniture_data["price"]*(furniture_data["discount"]/100)) if furniture_data["discount"] != 0 else furniture_data["price"]}₽\n\n{furniture_data["description"]}\n\nХарактеристики: {furniture_data["composition"]}',
                    reply_markup=get_furniturees_in_category_kb(cat_name, place, is_first=True, subcat=subcat_name)
                )
        else:
            if callback_query.message.photo:
                await callback_query.message.edit_media(
                    media=types.InputMediaPhoto(
                        open(f'static/{furniture_data["photo"]}', 'rb'),
                        caption=f'{furniture_data["name"]}\n\nЦена: {"<s>" + str(furniture_data["price"]) + "</s>" + "  " + str(furniture_data["price"]-furniture_data["price"]*(furniture_data["discount"]/100)) if furniture_data["discount"] != 0 else furniture_data["price"]}₽\n\n{furniture_data["description"]}\n\nХарактеристики: {furniture_data["composition"]}\n\nКоличество в корзине: {carts[callback_query.from_user.id][furniturees[place]]}.',
                    ),
                    reply_markup=get_furniturees_in_category_kb(cat_name, place, is_first=False, subcat=subcat_name),
                )
            else:
                await callback_query.message.delete()
                await bot.send_photo(
                    callback_query.from_user.id,
                    photo=types.InputFile(
                        open(f'static/{furniture_data["photo"]}', 'rb'),
                    ),
                    caption=f'{furniture_data["name"]}\n\nЦена: {"<s>" + str(furniture_data["price"]) + "</s>" + "  " + str(furniture_data["price"]-furniture_data["price"]*(furniture_data["discount"]/100)) if furniture_data["discount"] != 0 else furniture_data["price"]}₽\n\n{furniture_data["description"]}\n\nХарактеристики: {furniture_data["composition"]}\n\nКоличество в корзине: {carts[callback_query.from_user.id][furniturees[place]]}.',
                    reply_markup=get_furniturees_in_category_kb(cat_name, place, is_first=False, subcat=subcat_name),
                )

    else:
        await callback_query.message.edit_text(
            text='Тут пока ничего нет'
        )

@dp.callback_query_handler(lambda c: 'menu_l' in c.data)
async def menu_in_cat_last(callback_query: types.CallbackQuery):
    cat_name = callback_query.data.split(':')[1]
    place = int(callback_query.data.split(':')[2])
    subcat_name =callback_query.data.split(':')[3]
    furniturees = await get_furniturees_in_category(cat_name, subcat_name)
    if place == 0:
        place = len(furniturees) - 1
    else:
        place -= 1
    await menu_in_cat(callback_query, place=place, cat_name=cat_name, subcat_name=subcat_name)

@dp.callback_query_handler(lambda c: 'menu_n' in c.data)
async def menu_in_cat_next(callback_query: types.CallbackQuery):
    cat_name = callback_query.data.split(':')[1]
    subcat_name =callback_query.data.split(':')[3]
    place = int(callback_query.data.split(':')[2])
    furniturees = await get_furniturees_in_category(cat_name, subcat_name)
    if place >= len(furniturees) - 1:
        place = 0
    else:
        place += 1
    await menu_in_cat(callback_query, place=place, cat_name=cat_name, subcat_name=subcat_name)


@dp.callback_query_handler(lambda c:'add_in_c' in c.data)
async def add_in_cart(callback_query: types.CallbackQuery, change=False, furniture=None):
    if not change:
        cat_name = callback_query.data.split(':')[1]
        place = int(callback_query.data.split(':')[2])
        subcat_name =callback_query.data.split(':')[3]
        furniturees = await get_furniturees_in_category(cat_name, subcat_name)
        if furniturees[place] in carts[callback_query.from_user.id]:
            carts[callback_query.from_user.id][furniturees[place]] += 1
        else:
            carts[callback_query.from_user.id][furniturees[place]] = 1
        await menu_in_cat(callback_query, place=place, cat_name=cat_name, subcat_name=subcat_name) 
    else:
        carts[callback_query.from_user.id][furniture] += 1
        await change_furniture(callback_query, furniture=furniture)
        

@dp.callback_query_handler(lambda c:'del_in_c' in c.data)
async def del_in_cart(callback_query: types.CallbackQuery, change=False, furniture=None):
    if not change:
        cat_name = callback_query.data.split(':')[1]
        place = int(callback_query.data.split(':')[2])
        subcat_name =callback_query.data.split(':')[3]
        furniturees = await get_furniturees_in_category(cat_name, subcat_name)
        if furniturees[place] in carts[callback_query.from_user.id]:
            carts[callback_query.from_user.id][furniturees[place]] -= 1
            if carts[callback_query.from_user.id][furniturees[place]] == 0:
                del carts[callback_query.from_user.id][furniturees[place]] 
        else:
            del carts[callback_query.from_user.id][furniturees[place]]
        await menu_in_cat(callback_query, place=place, cat_name=cat_name, subcat_name=subcat_name) 
    else:
        carts[callback_query.from_user.id][furniture] -= 1
        await change_furniture(callback_query, furniture=furniture)

@dp.callback_query_handler(lambda c: c.data == 'from_furniture_to_cart')
async def from_furniture_to_cart(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    await my_cart(callback_query)

@dp.callback_query_handler(lambda c: c.data == 'from_furniture_to_back')
async def from_furniture_to_back(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    await menu(callback_query)


@dp.message_handler(lambda message: message.text == '🛒 Корзина', state='*')
async def my_cart(msg: types.Message, state=None):
    if state is not None:  # Проверяем, находится ли пользователь в каком-либо состоянии
        await state.finish()  # Завершаем текущее состояние
    for furniture in dict(carts[msg.from_user.id]):
            furniture_datas = await get_furniture_data(furniture)
            if furniture_datas['is_active'] == False:
                del carts[msg.from_user.id][furniture]
    if len(carts[msg.from_user.id]) != 0:
        message = ''
        all_price = 0
        for furniture in dict(carts[msg.from_user.id]):
            furniture_datas = await get_furniture_data(furniture)
            all_price += (furniture_datas["price"]-furniture_datas["price"]*(furniture_datas["discount"]/100))*carts[msg.from_user.id][furniture]
            message += f'{furniture}\t x \t{carts[msg.from_user.id][furniture]}\t = \t{(furniture_datas["price"]-furniture_datas["price"]*(furniture_datas["discount"]/100))*carts[msg.from_user.id][furniture]:.2f}₽\n'
        if msg.from_user.id in promo_in_carts:
            discount = await check_promocode(promo_in_carts[msg.from_user.id])
            if discount:
                message += f'\nИтоговая цена: <s>{all_price}</s>₽'    
                all_price = all_price - (all_price * (discount/100))
                message += f'  {all_price}'
            else:
                del promo_in_carts[msg.from_user.id]
        else:
            message += f'\nИтоговая цена: {all_price}₽'    
        await bot.send_message(
            msg.from_user.id,
            message, 
            reply_markup=carts_kb()
        )
    else:
        await bot.send_message(
            msg.from_user.id,
            'Ваша корзина пуста, скорее добавьте сюда что-ниубдь!'
        )


@dp.callback_query_handler(lambda c: c.data == 'use_promocode')
async def use_promocode_in_cart(callback_query: types.CallbackQuery):
    await user_states.UsePromocode.code.set()
    await callback_query.message.edit_text(
        'Введите промокод:'
    )

@dp.message_handler(state=user_states.UsePromocode.code)
async def use_promocode_in_cart_state(msg:  types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["code"] = msg.text
    await state.finish()
    if await check_promocode(data["code"]):
        promo_in_carts[msg.from_user.id] = data["code"]
        await my_cart(msg)
    else:
        await bot.send_message(
            msg.from_user.id,
            'К сожалению такого промокода не существует('
        )
        await my_cart(msg)




@dp.callback_query_handler(lambda c: c.data == 'clear_cart')
async def clear_cart(callback_query: types.CallbackQuery):
    carts[callback_query.from_user.id] = {}
    await callback_query.message.edit_text(
        'Корзина очищена!'
    )

@dp.callback_query_handler(lambda c: c.data == 'change_cart')
async def change_cart(callback_query: types.CallbackQuery):
    try:
        await callback_query.message.edit_text(
            'Выберите:',
            reply_markup=change_cart_kb(carts[callback_query.from_user.id])
        )
    except:
        await bot.send_message(
            callback_query.from_user.id,
            'Выберите:',
            reply_markup=change_cart_kb(carts[callback_query.from_user.id])
        )

@dp.callback_query_handler(lambda c: 'change_furniture' in c.data)
async def change_furniture(callback_query: types.CallbackQuery, furniture=None):
    if not furniture:
        furniture = callback_query.data.split(':')[1]
        furniture_data = await get_furniture_data(furniture)
        if carts[callback_query.from_user.id][furniture] == 1:
            await callback_query.message.delete()
            await bot.send_photo(
                callback_query.from_user.id,
                photo=types.InputFile(
                    open(f'static/{furniture_data["photo"]}', 'rb'),
                ),
                caption=f'{furniture_data["name"]}\n\nЦена: {"<s>" + str(furniture_data["price"]) + "</s>" + "  " + str(furniture_data["price"]-furniture_data["price"]*(furniture_data["discount"]/100)) if furniture_data["discount"] != 0 else furniture_data["price"]}₽\n\n{furniture_data["description"]}\n\nХарактеристики: {furniture_data["composition"]}\n\nКоличество в корзине: {carts[callback_query.from_user.id][furniture]}.',
                reply_markup=change_furniture_kb(furniture, is_first=True)
            )
        else:
            await callback_query.message.delete()
            await bot.send_photo(
                callback_query.from_user.id,
                photo=types.InputFile(
                    open(f'static/{furniture_data["photo"]}', 'rb'),
                ),
                caption=f'{furniture_data["name"]}\n\nЦена: {"<s>" + str(furniture_data["price"]) + "</s>" + "  " + str(furniture_data["price"]-furniture_data["price"]*(furniture_data["discount"]/100)) if furniture_data["discount"] != 0 else furniture_data["price"]}₽\n\n{furniture_data["description"]}\n\nХарактеристики: {furniture_data["composition"]}\n\nКоличество в корзине: {carts[callback_query.from_user.id][furniture]}.',
                reply_markup=change_furniture_kb(furniture, is_first=False)
            )
    else:
        furniture = callback_query.data.split(':')[1]
        furniture_data = await get_furniture_data(furniture)
        if carts[callback_query.from_user.id][furniture] == 1:
            await callback_query.message.edit_media(
                media=types.InputMediaPhoto(
                    open(f'static/{furniture_data["photo"]}', 'rb'),
                    f'{furniture_data["name"]}\n\nЦена: {"<s>" + str(furniture_data["price"]) + "</s>" + "  " + str(furniture_data["price"]-furniture_data["price"]*(furniture_data["discount"]/100)) if furniture_data["discount"] != 0 else furniture_data["price"]}₽\n\n{furniture_data["description"]}\n\nХарактеристики: {furniture_data["composition"]}\n\nКоличество в корзине: {carts[callback_query.from_user.id][furniture]}.',
                ),
                reply_markup=change_furniture_kb(furniture, is_first=True)
            )
        else:
            await callback_query.message.edit_media(
                media=types.InputMediaPhoto(
                    open(f'static/{furniture_data["photo"]}', 'rb'),
                    f'{furniture_data["name"]}\n\nЦена: {"<s>" + str(furniture_data["price"]) + "</s>" + "  " + str(furniture_data["price"]-furniture_data["price"]*(furniture_data["discount"]/100)) if furniture_data["discount"] != 0 else furniture_data["price"]}₽\n\n{furniture_data["description"]}\n\nХарактеристики: {furniture_data["composition"]}\n\nКоличество в корзине: {carts[callback_query.from_user.id][furniture]}.',
                ),
                reply_markup=change_furniture_kb(furniture, is_first=False)
            )

@dp.callback_query_handler(lambda c: 'append_furniture' in c.data)
async def change_append_furniture(callback_query: types.CallbackQuery):
    furniture = callback_query.data.split(':')[1]
    await add_in_cart(callback_query, change=True, furniture=furniture)

@dp.callback_query_handler(lambda c: 'subtract_furniture' in c.data)
async def change_append_furniture(callback_query: types.CallbackQuery):
    furniture = callback_query.data.split(':')[1]
    await del_in_cart(callback_query, change=True, furniture=furniture)

@dp.callback_query_handler(lambda c: 'delete_furniture' in c.data)
async def change_delete_furniture(callback_query: types.CallbackQuery):
    furniture = callback_query.data.split(':')[1]
    if furniture in carts[callback_query.from_user.id]:
        del carts[callback_query.from_user.id][furniture]
        await callback_query.message.delete()
        await my_cart(callback_query)
    else:
        await my_cart(callback_query)

@dp.callback_query_handler(lambda c: c.data == 'change_back_furniture')
async def back_to_change_furniture(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    await change_cart(callback_query)

@dp.callback_query_handler(lambda c: c.data == 'create_order')
async def create_order(callbcak_query: types.CallbackQuery):
    await callbcak_query.message.edit_text(
        text=f'Выберите способ получения:',
        reply_markup=type_of_order_kb()
    )


@dp.callback_query_handler(lambda c: c.data == 'order_type_dilivery')
async def order_type_dilivery(callback_query: types.CallbackQuery):
    delivery = await get_dilivery_db(callback_query.from_user.id)
    if delivery:
        await callback_query.message.edit_text(
            text=f'Ваш адрес: {delivery}\n\nВсё верно?',
            reply_markup=delivery_is_true_kb()
        )
    else:
        await change_in_ofline_delivery(callback_query)
    


@dp.callback_query_handler(lambda c: c.data == 'del_is_true')
async def del_is_true(callback_query: types.CallbackQuery):
    await ofline_order(callback_query, is_delivery=True)

@dp.callback_query_handler(lambda c: c.data == 'change_in_ofline_delivery')
async def change_in_ofline_delivery(callback_query: types.CallbackQuery):
    await user_states.Delivery.delivery.set()
    await callback_query.message.edit_text(
        'Введите адрес доставки:'
    )

@dp.message_handler(state=user_states.Delivery.delivery)
async def change_in_ofline_delivery_state(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["delivery"] = msg.text
    await state.finish()
    await change_delivery(msg.from_user.id, data["delivery"])
    await ofline_order(msg, is_delivery=True)
    

@dp.callback_query_handler(lambda c: c.data == 'order_type_warehouse')
async def order_type_warehouse(callback_query: types.CallbackQuery):
    await ofline_order(callback_query)





@dp.callback_query_handler(lambda c: c.data == 'order_type_warehouse')
async def ofline_order(callback_query: types.CallbackQuery, is_delivery=False):
    for furniture in dict(carts[callback_query.from_user.id]):
            furniture_datas = await get_furniture_data(furniture)
            if furniture_datas['is_active'] == False:
                del carts[callback_query.from_user.id][furniture]
    price = 0
    message = ''
    discount = None
    for furniture in carts[callback_query.from_user.id]:
        furniture_datas = await get_furniture_data(furniture)
        price += (furniture_datas["price"]-furniture_datas["price"]*(furniture_datas["discount"]/100))*carts[callback_query.from_user.id][furniture]
        message += f'{furniture}\t x \t{carts[callback_query.from_user.id][furniture]}\t = \t{(furniture_datas["price"]-furniture_datas["price"]*(furniture_datas["discount"]/100))*carts[callback_query.from_user.id][furniture]:.2f}₽\n'
    if callback_query.from_user.id in promo_in_carts:
        discount = await check_promocode(promo_in_carts[callback_query.from_user.id])
        if discount:
            message += f'\nИтоговая цена: <s>{price}</s>₽'    
            price = price - (price * (discount/100))
            message += f'  {price}'
            await delete_promocode(promo_in_carts[callback_query.from_user.id])
        else:
            del promo_in_carts[callback_query.from_user.id]
    else:
        message += f'\nИтоговая цена: {price}₽'
    
    user_data = await get_user_data(callback_query.from_user.id)
    if user_data:
        order_id = await create_transaction(
            user_id=str(callback_query.from_user.id),
            phone_number=user_data["phone"],
            coast=price,
            is_online=False,
            furniturees=carts[callback_query.from_user.id]
        )
    carts[callback_query.from_user.id] = {}
    if not is_delivery:
        await callback_query.message.edit_text(
            text=f"Ваш заказ #{order_id} на сумму {price}₽ принят. Вам скоро позвонят, чтобы уточнить данные."
    )
    else:
        await bot.send_message(
            callback_query.from_user.id, 
            f"Ваш заказ #{order_id} на сумму {price}₽ принят. Вам скоро позвонят, чтобы уточнить данные."
        )
    if await get_count_orders(callback_query.from_user.id) == 1:
        await bot.send_message(
            callback_query.from_user.id,
            'Поздравляем вас с первым заказом!\n\nНапишите отзыв о нас и скиньте скриншот отзыва нашему администратору! После этого вы получите промокод на скидку!!!\n\n https://yandex.ru/maps/org/dik_tsentralny_sklad/209098064287/',
            disable_web_page_preview=True
        )
    await bot.send_message(
        CHANNEL_ID,
        f'Новый заказ! #{order_id}\n\n{message}\n{"(скидка " + str(discount) + "%)" if discount else ""}\n\nИмя: {user_data["name"]}\nНомер телефона: {user_data["phone"]}\nЮзернейм тг: @{user_data["user_name"]}\n\nВремя формирования заказа: {datetime.datetime.now()}\n\n{"Адрес доставки:" + await get_dilivery_db(callback_query.from_user.id) if is_delivery else ""}'
    )



@dp.message_handler(lambda message: message.text == '📦 Мои заказы', state='*')
async def my_orders(msg: types.Message, state=None):
    if state is not None:  # Проверяем, находится ли пользователь в каком-либо состоянии
        await state.finish()  # Завершаем текущее состояние
    history_list = await get_user_history(msg.from_user.id)
    if history_list:
        history_list = history_list[::-1]
        history_list = history_list[:6]
        date_list = []
        for i in history_list:
            date_list.append(str(i.date))
        await bot.send_message(
            msg.from_user.id,
            'Выберите:',
            reply_markup=history_kb(date_list)
        )
    else:
        await bot.send_message(
            msg.from_user.id,
            'В вашей истории пока ничего нет...',
        )


@dp.callback_query_handler(lambda c: 'history_my_order' in c.data)
async def get_my_history_order(callback_query: types.CallbackQuery):
    index = callback_query.data.split(':')[1]
    user_history = await get_user_history(str(callback_query.from_user.id))
    user_history = user_history[::-1]
    user_history = user_history[:6]
    order_data = user_history[int(index)]
    message = f'{str(order_data.date)}\n\n'
    for furniture in order_data.furnitures:
        message += f'{furniture}\t x \t{order_data.furnitures[furniture]}\n'
    message += f'\nИтоговая цена: {order_data.coast}₽'
    await callback_query.message.edit_text(
        text=message,
        reply_markup=history_order_kb(index)
    )
    

@dp.callback_query_handler(lambda c: 'repeat_cart' in c.data)
async def repeat_cart(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    index = callback_query.data.split(':')[1]
    user_history = await get_user_history(str(callback_query.from_user.id))
    order_data = user_history[int(index)]
    carts[callback_query.from_user.id] = order_data.furnitures
    await my_cart(callback_query)

@dp.callback_query_handler(lambda c: c.data == 'history_back_order')
async def history_back_order(callbcak_query: types.CallbackQuery):
    await callbcak_query.message.delete()
    await my_orders(callbcak_query)




@dp.message_handler(lambda message: message.text == '🔎 Поиск товара', state='*')
async def search_furniture(msg: types.Message, state=None):
    if state is not None:  # Проверяем, находится ли пользователь в каком-либо состоянии
        await state.finish()  # Завершаем текущее состояние
    await user_states.SearchFurniture.words.set()
    await bot.send_message(
        msg.from_user.id,
        'Введите название, номер, фразу из описания и т.д:'
    )


word_list = {}

@dp.message_handler(state=user_states.SearchFurniture.words)
async def search_furniture_state(msg, state=None, place=0):
    if state is not None:
        async with state.proxy() as data:
            data["words"] = msg.text
        await state.finish()
        message = await bot.send_message(
            msg.from_user.id,
            'Немного подождите, идет поиск...'
        )
        result = await search_furniture_db(data["words"])
        word_list[msg.from_user.id] = data["words"]
        await message.delete()
    else:
        words = word_list[msg.from_user.id]
        result = await search_furniture_db(words)
        if place == -1:
            place = len(result) - 1
        if place >= len(result):
            place = 0    
    if result:
        if isinstance(msg, types.Message):
                if len(result) == 1:
                    await bot.send_photo(
                        msg.from_user.id,
                        photo=types.InputFile(
                            open(f'static/{result[place].photo}', 'rb')
                        ),
                        caption=f'{result[place].name}\n\nЦена: {"<s>" + str(result[place].price) + "</s>" + "  " + str(result[place].price-result[place].price*(result[place].discount/100)) if result[place].discount != 0 else result[place].price}₽\n\n{result[place].description}\n\nХарактеристики: {result[place].caracteristic}',
                        reply_markup=search_furniture_kb(result[place].category, result[place].subcategory, place, is_one=True)
                   )
                else:
                    await bot.send_photo(
                        msg.from_user.id,
                        photo=types.InputFile(
                            open(f'static/{result[place].photo}', 'rb')
                        ),
                        caption=f'{result[place].name}\n\nЦена: {"<s>" + str(result[place].price) + "</s>" + "  " + str(result[place].price-result[place].price*(result[place].discount/100)) if result[place].discount != 0 else result[place].price}₽\n\n{result[place].description}\n\nХарактеристики: {result[place].caracteristic}',
                        reply_markup=search_furniture_kb(result[place].category, result[place].subcategory, place, is_one=False)
                    )

        else:
                await msg.message.delete()
                await bot.send_photo(
                        msg.from_user.id,
                        photo=types.InputFile(
                            open(f'static/{result[place].photo}', 'rb')
                        ),
                        caption=f'{result[place].name}\n\nЦена: {"<s>" + str(result[place].price) + "</s>" + "  " + str(result[place].price-result[place].price*(result[place].discount/100)) if result[place].discount != 0 else result[place].price}₽\n\n{result[place].description}\n\nХарактеристики: {result[place].caracteristic}',
                        reply_markup=search_furniture_kb(result[place].category, result[place].subcategory, place, is_one=False)
                    )
    else:
        await bot.send_message(
            msg.from_user.id,
            'Ничего найти не удалось('
        )


@dp.callback_query_handler(lambda c: 'search_last' in c.data)
async def search_furniture_last(callback_query: types.CallbackQuery):
    place = int(callback_query.data.split(':')[1])
    await search_furniture_state(callback_query, place=place-1)


@dp.callback_query_handler(lambda c: 'search_next' in c.data)
async def search_furniture_next(callback_query: types.CallbackQuery):
    place = int(callback_query.data.split(':')[1])
    await search_furniture_state(callback_query, place=place+1)


@dp.callback_query_handler(lambda c: 'op_in_cat' in c.data)
async def search_open_in_catalog(callback_query: types.CallbackQuery):
    category = callback_query.data.split(':')[1]
    subcat = callback_query.data.split(':')[2]
    place = int(callback_query.data.split(':')[3])
    words = word_list[callback_query.from_user.id]
    result = await search_furniture_db(words)
    good = result[place].name
    goods = await get_furniturees_in_category(category, subcat)
    pl = 0
    for index, tovar in enumerate(goods):
        if tovar == good:
            pl = index
    await menu_in_cat(callback_query, place=pl, cat_name=category, subcat_name=subcat)




@dp.message_handler(lambda  message:  message.text == '💸 Скидки', state='*')
async def disount_and_benifits(callback_query, place=0, state=None):
    if state is not None:  # Проверяем, находится ли пользователь в каком-либо состоянии
        await state.finish()  # Завершаем текущее состояние
    discounts = await get_discount_list()
    furniture_data = discounts[place]
    if discounts:
        if furniture_data:
            if furniture_data.name not in carts[callback_query.from_user.id]:
                if isinstance(callback_query, types.CallbackQuery):
                    if callback_query.message.photo:
                        await callback_query.message.edit_media(
                            media=types.InputMediaPhoto(
                                open(f'static/{furniture_data.photo}', 'rb'),
                                f'{furniture_data.name}\n\nЦена: {"<s>" + str(furniture_data.price) + "</s>" + "  " + str(furniture_data.price-furniture_data.price*(furniture_data.discount/100)) if furniture_data.discount != 0 else furniture_data.price}₽\n\n{furniture_data.description}\n\nХарактеристики: {furniture_data.caracteristic}',
                            ),
                            reply_markup=get_furnitures_in_discount_kb(place, is_first=True)
                        )
                    else:
                        await callback_query.message.delete()
                        await bot.send_photo(
                            callback_query.from_user.id,
                            photo=types.InputFile(
                                open(f'static/{furniture_data.photo}', 'rb'),
                            ),
                            caption=f'{furniture_data.name}\n\nЦена: {"<s>" + str(furniture_data.price) + "</s>" + "  " + str(furniture_data.price-furniture_data.price*(furniture_data.discount/100)) if furniture_data.discount != 0 else furniture_data.price}₽\n\n{furniture_data.description}\n\nХарактеристики: {furniture_data.caracteristic}',
                            reply_markup=get_furnitures_in_discount_kb(place, is_first=True)
                        )
                else:
                    await bot.send_photo(
                        callback_query.from_user.id,
                        photo=types.InputFile(
                            open(f'static/{furniture_data.photo}', 'rb'),
                        ),
                        caption=f'{furniture_data.name}\n\nЦена: {"<s>" + str(furniture_data.price) + "</s>" + "  " + str(furniture_data.price-furniture_data.price*(furniture_data.discount/100)) if furniture_data.discount != 0 else furniture_data.price}₽\n\n{furniture_data.description}\n\nХарактеристики: {furniture_data.caracteristic}',
                        reply_markup=get_furnitures_in_discount_kb(place, is_first=True)
                    )

            else:
                if isinstance(callback_query, types.CallbackQuery):
                    if callback_query.message.photo:
                        await callback_query.message.edit_media(
                            media=types.InputMediaPhoto(
                                open(f'static/{furniture_data.photo}', 'rb'),
                                caption=f'{furniture_data.name}\n\nЦена: {"<s>" + str(furniture_data.price) + "</s>" + "  " + str(furniture_data.price-furniture_data.price*(furniture_data.discount/100)) if furniture_data.discount != 0 else furniture_data.price}₽\n\n{furniture_data.description}\n\nХарактеристики: {furniture_data.caracteristic}\n\nКоличество в корзине: {carts[callback_query.from_user.id][furniture_data.name]}.',
                            ),
                            reply_markup=get_furnitures_in_discount_kb(place, is_first=False)

                        )
                    else:
                        await callback_query.message.delete()
                        await bot.send_photo(
                            callback_query.from_user.id,
                            photo=types.InputFile(
                                open(f'static/{furniture_data.photo}', 'rb'),
                            ),
                            caption=f'{furniture_data.name}\n\nЦена: {"<s>" + str(furniture_data.price) + "</s>" + "  " + str(furniture_data.price-furniture_data.price*(furniture_data.discount/100)) if furniture_data.discount != 0 else furniture_data.price}₽\n\n{furniture_data.description}\n\nХарактеристики: {furniture_data.caracteristic}\n\nКоличество в корзине: {carts[callback_query.from_user.id][furniture_data.name]}.',
                            reply_markup=get_furnitures_in_discount_kb(place, is_first=False)
                        )
                else:
                        await bot.send_photo(
                            callback_query.from_user.id,
                            photo=types.InputFile(
                                open(f'static/{furniture_data.photo}', 'rb'),
                            ),
                            caption=f'{furniture_data.name}\n\nЦена: {"<s>" + str(furniture_data.price) + "</s>" + "  " + str(furniture_data.price-furniture_data.price*(furniture_data.discount/100)) if furniture_data.discount != 0 else furniture_data.price}₽\n\n{furniture_data.description}\n\nХарактеристики: {furniture_data.caracteristic}',
                            reply_markup=get_furnitures_in_discount_kb(place, is_first=True)
                        )

    else:
        await callback_query.message.edit_text(
            text='Тут пока ничего нет'
        )
                    


@dp.callback_query_handler(lambda c: 'discount_last' in c.data)
async def discount_last(callback_query: types.CallbackQuery):
    place = int(callback_query.data.split(':')[1])
    furniturees = await get_discount_list()
    if place == 0:
        place = len(furniturees) - 1
    else:
        place -= 1
    await disount_and_benifits(callback_query, place=place)


@dp.callback_query_handler(lambda c: 'discount_next' in c.data)
async def discount_next(callback_query:  types.CallbackQuery):
    place = int(callback_query.data.split(':')[1])
    furniturees = await get_discount_list()
    if place >= len(furniturees) - 1:
        place = 0
    else:
        place += 1
    await disount_and_benifits(callback_query, place=place)

@dp.callback_query_handler(lambda c: 'app_in_cart_with_disk' in c.data)
async def app_in_cart_with_disk(callback_query: types.CallbackQuery):
    place = int(callback_query.data.split(':')[1])
    furniturees = await get_discount_list()
    if furniturees[place].name in carts[callback_query.from_user.id]:
        carts[callback_query.from_user.id][furniturees[place].name] += 1
    else:
        carts[callback_query.from_user.id][furniturees[place].name] = 1
    await disount_and_benifits(callback_query, place=place)

@dp.callback_query_handler(lambda c: 'drop_in_cart_with_disk' in c.data)
async def del_in_cart_with_disk(callback_query: types.CallbackQuery):
    place = int(callback_query.data.split(':')[1])
    furniturees = await get_discount_list()
    if furniturees[place].name in carts[callback_query.from_user.id]:
        carts[callback_query.from_user.id][furniturees[place].name] -= 1
        if carts[callback_query.from_user.id][furniturees[place].name] == 0:
            del carts[callback_query.from_user.id][furniturees[place].name] 
    else:
        del carts[callback_query.from_user.id][furniturees[place].name]
    await disount_and_benifits(callback_query, place=place)

  

@dp.message_handler(lambda message: message.text == '🚛 Доставка', state='*')
async def delivery(msg: types.Message, state=None):
    if state is not None:  # Проверяем, находится ли пользователь в каком-либо состоянии
        await state.finish()  # Завершаем текущее состояние
    text = await get_delivery()
    await bot.send_message(
        msg.from_user.id,
        text
    )


@dp.message_handler(lambda message: message.text == '📍 О нас', state='*')
async def about_us(msg: types.Message, state=None):
    if state is not None:  # Проверяем, находится ли пользователь в каком-либо состоянии
        await state.finish()  # Завершаем текущее состояние
    text = await get_about_us()
    await bot.send_message(
        msg.from_user.id,
        text
    )

@dp.message_handler(lambda message: message.text == '🛟 Помощь')
async def help(msg: types.Message, state=None):
    if state is not None:  # Проверяем, находится ли пользователь в каком-либо состоянии
        await state.finish()  # Завершаем текущее состояние
    await bot.send_message(
        msg.from_user.id,
        'Нужна помощь?\nВы можете написать в чат поддержки или заказать звонок!',
        reply_markup=help_kb()
    )

@dp.callback_query_handler(lambda c: c.data == 'book_a_call')
async def book_a_call(callback_query: types.CallbackQuery):
    user_data = await get_user_data(callback_query.from_user.id)
    await bot.send_message(
        CHANNEL_ID,
        f'Заявка на звонок!\n\nИмя: {user_data["name"]}\nНомер телефона: {user_data["phone"]}\nЮзернейм тг: @{user_data["user_name"]}'
    )
    await callback_query.message.edit_text(
        'Отлично, вам скоро позвонят!'
    )



################################### Admin ###################################


@dp.message_handler(commands='admin')
@admin_access
async def cmd_admin(msg: types.Message):
    await bot.send_message(
        msg.from_user.id,
        'Выберите:',
        reply_markup=admin_main_kb()
    )


    


@dp.callback_query_handler(lambda c: c.data == 'admin_edit_menu')
@admin_access
async def admin_edit_menu(callback_query: types.CallbackQuery):
    await bot.send_message(
        callback_query.from_user.id,
        'Выберите категорию',
        reply_markup=await admin_get_category_kb()
    )    

@dp.callback_query_handler(lambda c: 'admin_in_cat_edit' in c.data)
@admin_access
async def admin_edit_menu_subcat(callback_query: types.CallbackQuery):
    cat_name = callback_query.data.split(':')[1]
    await callback_query.message.edit_text(
        'Выберите подкатегорию',
        reply_markup=await admin_edit_menu_subcat_kb(cat_name)
    )




@dp.callback_query_handler(lambda c: 'admin_subcat_edit_menu' in c.data)
@admin_access
async def admin_in_cat_edit(callback_query: types.CallbackQuery, place=0, cat_name=None, subcat=None):
    if not cat_name:
        cat_name = callback_query.data.split(':')[1]
        subcat = callback_query.data.split(':')[2]
    furniturees = await admin_get_furniturees_in_category(cat_name)
    furniture_data = await get_furniture_data(furniturees[place])
    if isinstance(callback_query, types.CallbackQuery):
        if furniture_data["is_active"]:
            if callback_query.message.photo:
                await callback_query.message.edit_media(
                    media=types.InputMediaPhoto(
                        open(f'static/{furniture_data["photo"]}', 'rb'),
                        f'{furniture_data["name"]}\n\nЦена: {"<s>" + str(furniture_data["price"]) + "</s>" + "  " + str(furniture_data["price"]-furniture_data["price"]*(furniture_data["discount"]/100)) if furniture_data["discount"] != 0 else furniture_data["price"]}₽\n\n{furniture_data["description"]}\n\nХарактеристики: {furniture_data["composition"]}',
                    ),
                    reply_markup=admin_get_furniturees_in_category_kb(cat_name, place, is_active=True, subcat=subcat)
                )
            else:
                await callback_query.message.delete()
                await bot.send_photo(
                    callback_query.from_user.id,
                    photo=types.InputFile(
                        open(f'static/{furniture_data["photo"]}', 'rb'),
                    ),
                    caption=f'{furniture_data["name"]}\n\nЦена: {"<s>" + str(furniture_data["price"]) + "</s>" + "  " + str(furniture_data["price"]-furniture_data["price"]*(furniture_data["discount"]/100)) if furniture_data["discount"] != 0 else furniture_data["price"]}\n\n{furniture_data["description"]}\n\nХарактеристики: {furniture_data["composition"]}',
                    reply_markup=admin_get_furniturees_in_category_kb(cat_name, place, is_active=True, subcat=subcat)
                )
        else:
            if callback_query.message.photo:
                await callback_query.message.edit_media(
                    media=types.InputMediaPhoto(
                        open(f'static/{furniture_data["photo"]}', 'rb'),
                        f'{furniture_data["name"]}\n\nЦена: {"<s>" + str(furniture_data["price"]) + "</s>" + "  " + str(furniture_data["price"]-furniture_data["price"]*(furniture_data["discount"]/100)) if furniture_data["discount"] != 0 else furniture_data["price"]}₽\n\n{furniture_data["description"]}\n\nХарактеристики: {furniture_data["composition"]}\n\nТовар неактивен',
                    ),
                    reply_markup=admin_get_furniturees_in_category_kb(cat_name, place, is_active=False, subcat=subcat)
                )
            else:
                await callback_query.message.delete()
                await bot.send_photo(
                    callback_query.from_user.id,
                    photo=types.InputFile(
                        open(f'static/{furniture_data["photo"]}', 'rb'),
                    ),
                    caption=f'{furniture_data["name"]}\n\nЦена: {"<s>" + str(furniture_data["price"]) + "</s>" + "  " + str(furniture_data["price"]-furniture_data["price"]*(furniture_data["discount"]/100)) if furniture_data["discount"] != 0 else furniture_data["price"]}₽\n\n{furniture_data["description"]}\n\nХарактеристики: {furniture_data["composition"]}\n\nТовар неактивен',
                    reply_markup=admin_get_furniturees_in_category_kb(cat_name, place, is_active=False, subcat=subcat)
                )
    else:
        await bot.send_photo(
            callback_query.from_user.id,
            photo=types.InputFile(
                open(f'static/{furniture_data["photo"]}', 'rb'),
                ),
            caption=f'{furniture_data["name"]}\n\nЦена: {"<s>" + str(furniture_data["price"]) + "</s>" + "  " + str(furniture_data["price"]-furniture_data["price"]*(furniture_data["discount"]/100)) if furniture_data["discount"] != 0 else furniture_data["price"]}₽\n\n{furniture_data["description"]}\n\nХарактеристики: {furniture_data["composition"]}\n\nТовар неактивен',
            reply_markup=admin_get_furniturees_in_category_kb(cat_name, place, is_active=False, subcat=subcat, is_find=True)
        )

@dp.callback_query_handler(lambda c: 'menu_admin_l' in c.data)
@admin_access
async def menu_admin_last(callback_query: types.CallbackQuery):
    cat_name = callback_query.data.split(':')[1]
    place = int(callback_query.data.split(':')[2])
    subcat = callback_query.data.split(':')[3]
    furniturees = await admin_get_furniturees_in_category(cat_name)
    if place == 0:
        place = len(furniturees) - 1
    else:
        place -= 1
    await admin_in_cat_edit(callback_query, place=place, cat_name=cat_name, subcat=subcat)


@dp.callback_query_handler(lambda c: 'menu_admin_n' in c.data)
@admin_access
async def menu_admin_next(callback_query: types.CallbackQuery):
    cat_name = callback_query.data.split(':')[1]
    place = int(callback_query.data.split(':')[2])
    subcat = callback_query.data.split(':')[3]
    furniturees = await admin_get_furniturees_in_category(cat_name)
    if place >= len(furniturees) - 1:
        place = 0
    else:
        place += 1
    await admin_in_cat_edit(callback_query, place=place, cat_name=cat_name, subcat=subcat)



@dp.callback_query_handler(lambda c: 'admin_deactive_f' in c.data)
@admin_access
async def admin_deactive_furniture(callback_query: types.CallbackQuery):
    cat_name = callback_query.data.split(':')[1]
    place = int(callback_query.data.split(':')[2])
    subcat = callback_query.data.split(':')[3]
    furniturees = await admin_get_furniturees_in_category(cat_name)
    furniture_data = await get_furniture_data(furniturees[place])
    await change_active(furniture_data["name"])
    await admin_in_cat_edit(callback_query, place=place, cat_name=cat_name, subcat=subcat)


@dp.callback_query_handler(lambda c: 'admin_del_f' in c.data)
@admin_access
async def admin_del_furniture(callback_query: types.CallbackQuery):
    cat_name = callback_query.data.split(':')[1]
    place = int(callback_query.data.split(':')[2])
    furniturees = await admin_get_furniturees_in_category(cat_name)
    furniturees = furniturees[place]
    await admin_delete_furniture(furniturees)
    await callback_query.message.delete()
    await bot.send_message(
        callback_query.from_user.id,
        text='Успешно удалено!',

    )

@dp.callback_query_handler(lambda c: c.data == 'from_admin_furniture_to_back')
@admin_access
async def admin_del_task_back(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    await admin_edit_menu(callback_query)


@dp.callback_query_handler(lambda c: c.data == 'admin_new_subcategory')
@admin_access
async def admin_new_subcategory(callbcak_query: types.CallbackQuery):
    await admin_states.AddNewSubcategory.category.set()
    await bot.send_message(
        callbcak_query.from_user.id,
        'Выберите категорию, в которую нужно добавить подкатегорию:',
        reply_markup=await admin_add_subcategory_kb()
    )

@dp.callback_query_handler(lambda c: 'admin_kb_add_sub' in c.data, state=admin_states.AddNewSubcategory.category)
@admin_access
async def admin_new_subcategory_state_1(callbcak_query: types.CallbackQuery, state: FSMContext):
    category = callbcak_query.data.split(':')[1]
    async with state.proxy() as data:
        data['category'] = category
    await admin_states.AddNewSubcategory.name.set()
    await bot.send_message(
        callbcak_query.from_user.id,
        'Введите название подкатегории:'
    )

@dp.message_handler(state=admin_states.AddNewSubcategory.name)
@admin_access
async def admin_new_subcategory_state_2(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = msg.text
    await admin_states.AddNewSubcategory.conf.set()
    await bot.send_message(
        msg.from_user.id,
        f'Вы уверены, что хотите добавить подкатегорию {data["name"]} в категорию {data["category"]}',
        reply_markup=admin_add_new_subcat_conf_kb()
    )

@dp.callback_query_handler(lambda c: 'new_subconf_cat' in c.data, state=admin_states.AddNewSubcategory.conf)
@admin_access
async def admin_new_subcategory_state_3(callback_query: types.CallbackQuery, state: FSMContext):
    conf = callback_query.data.split(':')[1]
    async with state.proxy() as  data:
        data["conf"] = conf
    if conf == 'yes':
        await create_subcategory(category=data['category'], name=data['name'])
        await state.finish()
        await callback_query.message.delete()
        await bot.send_message(
            callback_query.from_user.id,
            'Подкатегория создана!'
        )
    else:
        await state.finish()
        await callback_query.message.delete()
        await bot.send_message(
            callback_query.from_user.id,
            'Отменено!'
        )


@dp.callback_query_handler(lambda c: c.data == 'admin_new_category')
@admin_access
async def admin_new_category(callback_query: types.CallbackQuery):
    await admin_states.AddNewCategory.name.set()
    await bot.send_message(
        callback_query.from_user.id,
        'Введите новую категорию'
    )

@dp.message_handler(state=admin_states.AddNewCategory.name)
@admin_access
async def admin_new_category_state(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = msg.text
    await admin_states.AddNewCategory.next()
    await bot.send_message(
        msg.from_user.id,
        f'Вы уверены что хотите добавить категорию {data["name"]}?',
        reply_markup=admin_add_new_cat_conf_kb()
    )

@dp.callback_query_handler(lambda c: 'new_conf_cat' in c.data, state=admin_states.AddNewCategory.conf)
@admin_access
async def admin_new_category_state(callback_query: types.CallbackQuery, state: FSMContext):
    conf = callback_query.data.split(':')[1]
    async with state.proxy() as  data:
        data["conf"] = conf
    if conf == 'yes':
        await create_category(data["name"])
        await state.finish()
        await callback_query.message.delete()
        await bot.send_message(
            callback_query.from_user.id,
            'Категория создана!'
        )
    else:
        await state.finish()
        await callback_query.message.delete()
        await bot.send_message(
            callback_query.from_user.id,
            'Отменено!'
        )

#
@dp.callback_query_handler(lambda c: c.data == 'admin_delete_category')
@admin_access
async def admin_delete_category(callback_query: types.CallbackQuery):
    await bot.send_message(
        callback_query.from_user.id,
        'Выберите:',
        reply_markup=await admin_delete_category_kb()
    )

@dp.callback_query_handler(lambda c: 'admin_del_cat' in c.data)
@admin_access
async def admin_del_cat(callback_query: types.CallbackQuery):
    cat_name = callback_query.data.split(':')[1]
    await callback_query.message.edit_text(
        f'Вы уверены что хотите удалить категорию {cat_name}?',
        reply_markup=admin_delete_category_conf_kb(cat_name)
    )

@dp.callback_query_handler(lambda c: 'admin_conf_del_cat' in c.data)
@admin_access
async def admin_del_cat_conf(callback_query: types.CallbackQuery):
    cat_name = callback_query.data.split(':')[1]
    conf = callback_query.data.split(':')[2]
    if conf == 'yes':
        await delete_category(cat_name)
        await callback_query.message.edit_text(
            text='Успешно!'
        )
    else:
        await callback_query.message.edit_text(
            text='Отменено!'
        )
#

@dp.callback_query_handler(lambda c: c.data == 'admin_delete_subcategory')
@admin_access
async def admin_delete_subcategory(callbcak_query: types.CallbackQuery):
    await bot.send_message(
        callbcak_query.from_user.id,
        'Выберите категорию, в которой хотите удалить подкатегорию:',
        reply_markup=await admin_get_category_for_del_sub_kb()
    )

@dp.callback_query_handler(lambda c: 'admin_get_category_for_del_sub' in c.data)
@admin_access
async def admin_get_category_for_del_sub(callback_query: types.CallbackQuery):
    cat = callback_query.data.split(':')[1]
    await callback_query.message.edit_text(
        'Выберите подкатегорию, которую хотите удалить:',
        reply_markup=await admin_del_subcategory_kb(cat)
    )

@dp.callback_query_handler(lambda c: 'admin_kb_del_subcat' in c.data)
@admin_access
async def admin_del_subcat(callback_query: types.CallbackQuery):
    subcat = callback_query.data.split(':')[1]
    await  admin_del_subcategory(subcat)
    await callback_query.message.edit_text(
        'Успешно!'
    )


@dp.callback_query_handler(lambda c: c.data == 'admin_new_furniture')
@admin_access
async def admin_new_furniture(callback_query: types.CallbackQuery):
    await admin_states.AddNewfurniture.name.set()
    await bot.send_message(
        callback_query.from_user.id,
        'Введите название товара'
    )

@dp.message_handler(state=admin_states.AddNewfurniture.name)
@admin_access
async def admin_new_furniture_state_name(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = msg.text
    await admin_states.AddNewfurniture.photo.set()
    await bot.send_message(
        msg.from_user.id,
        'Отправьте ОДНО фото'
    )

import transliterate

@dp.message_handler(content_types=[ContentType.PHOTO], state=admin_states.AddNewfurniture.photo)
@admin_access
async def admin_new_furniture_state_photo(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        transliterated_text = transliterate.translit(data["name"], 'ru', reversed=True)
        words = transliterated_text.split()
        snake_case_text = '_'.join(words)
        data["photo"] = snake_case_text + '.jpg'
    path = f'static/{snake_case_text}.jpg'
    await msg.photo[-1].download(path)
    await admin_states.AddNewfurniture.description.set()
    await bot.send_message(
        msg.from_user.id,
        'Введите описание товара'
    )

@dp.message_handler(state=admin_states.AddNewfurniture.description)
@admin_access
async def admin_new_furniture_state_description(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["description"] = msg.html_text
    await admin_states.AddNewfurniture.composition.set()
    await bot.send_message(
        msg.from_user.id,
        'Введите Характеристики товара'
    )

@dp.message_handler(state=admin_states.AddNewfurniture.composition)
@admin_access
async def admin_new_furniture_state_composition(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["composition"] = msg.html_text
    await admin_states.AddNewfurniture.price.set()
    await bot.send_message(
        msg.from_user.id,
        'Введите цену (разделитель нецелой части - ":" Например - 3.14)'
    )

@dp.message_handler(state=admin_states.AddNewfurniture.price)
@admin_access
async def admin_new_furniture_state_price(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["price"] = msg.text
    await admin_states.AddNewfurniture.category.set()
    await bot.send_message(
        msg.from_user.id,
        'Выберите категорию:',
        reply_markup=await admin_set_category_for_new_furniture()
    )

@dp.callback_query_handler(lambda c: 'admin_set_cat' in c.data, state=admin_states.AddNewfurniture.category)
@admin_access
async def admin_new_furniture_state_category(callbcak_query: types.CallbackQuery, state: FSMContext):
    cat_name = callbcak_query.data.split(':')[1]
    async with state.proxy() as data:
        data["category"] = cat_name
    await admin_states.AddNewfurniture.subcategory.set()
    await bot.send_message(
        callbcak_query.from_user.id,
        'Выберите субкатегорию:',
        reply_markup=await admin_set_subcategory_for_new_furniture(cat_name)
    )


@dp.callback_query_handler(lambda c: 'admin_set_subcat' in c.data, state=admin_states.AddNewfurniture.subcategory)
@admin_access
async def admin_new_furniture_state_subcategory(callbcak_query: types.CallbackQuery, state: FSMContext):
    subcat_name = callbcak_query.data.split(':')[1]
    async with state.proxy() as data:
        data["subcategory"] = subcat_name
    await bot.send_message(
        callbcak_query.from_user.id,
        'Всё верно?'
    )
    await bot.send_photo(
        callbcak_query.from_user.id,
        photo=types.InputFile(
            open(f'static/{data["photo"]}', 'rb'),
        ),
        caption=f'{data["name"]}\n\nЦена: {data["price"]}₽\n\n{data["description"]}\n\nХарактеристики: {data["composition"]}',
        reply_markup=admin_new_furniture_conf()
    )
    await admin_states.AddNewfurniture.conf.set()


@dp.callback_query_handler(lambda c: 'admin_new_conf' in c.data, state=admin_states.AddNewfurniture.conf)
@admin_access
async def admin_new_furniture_state_conf(callback_query: types.CallbackQuery, state: FSMContext):
    conf = callback_query.data.split(':')[1]
    if conf == 'yes':
        async with state.proxy() as data:
            await create_furniture(
                name=data["name"],
                photo=data["photo"],
                description=data["description"],
                caracteristic=data["composition"],
                price=float(data["price"]),
                category=data["category"],
                subcategory=data["subcategory"]
            )
        await state.finish()
        await bot.send_message(
            callback_query.from_user.id,
            'Товар добавлен!'
        )
    else:
        await state.finish()
        await bot.send_message(
            callback_query.from_user.id,
            'Отменено!'
        )



@dp.callback_query_handler(lambda c: 'admin_edit_pr' in c.data)
@admin_access
async def admin_edit_price(callback_query: types.CallbackQuery, state: FSMContext):
    cat_name = callback_query.data.split(':')[1]
    place = int(callback_query.data.split(':')[2])
    subcat = callback_query.data.split(':')[3]
    await admin_states.AdminEditPrice.cat_name.set()
    async with state.proxy() as data:
        data["cat_name"] = cat_name
        data["place"] = place
        data["subcat"] = subcat
    await admin_states.AdminEditPrice.price.set()
    await bot.send_message(
        callback_query.from_user.id,
        'Введите новую цену'
    )

import re

@dp.message_handler(state=admin_states.AdminEditPrice.price)
@admin_access
async def admin_edit_price_state(msg: types.Message, state: FSMContext):
    def is_number_using_regex(s):
        pattern = r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$'
        return re.match(pattern, s) is not None

    if is_number_using_regex(msg.text):
        async with state.proxy() as data:
            data["price"] = float(msg.text)
        dishes = await get_furniturees_in_category(data["cat_name"], data["subcat"])
        dish = dishes[int(data["place"])]
        await edit_price(data["price"], dish)
        await state.finish()
        await bot.send_message(
            msg.from_user.id,
            'Успешно'
        )
        await cmd_admin(msg)
    else:
        await bot.send_message(
            msg.from_user.id,
            'Вы допустили ошибку!'
        )
        await state.finish()
        await cmd_admin(msg)
        


@dp.callback_query_handler(lambda c: 'admin_edit_dis' in c.data)
async def admin_edit_discount(callback_query: types.CallbackQuery, state: FSMContext):
    cat_name = callback_query.data.split(':')[1]
    place = int(callback_query.data.split(':')[2])
    subcat = callback_query.data.split(':')[3]
    await admin_states.AdminEditDiscount.cat_name.set()
    async with state.proxy() as data:
        data["cat_name"] = cat_name
        data["place"] = place
        data["subcat"] = subcat
    await admin_states.AdminEditDiscount.discount.set()
    await bot.send_message(
        callback_query.from_user.id,
        'Введите скидку (число, разделитель дробной части - "." в %):'
    )

@dp.message_handler(state=admin_states.AdminEditDiscount.discount)
async def admin_edit_discount_state(msg: types.Message, state: FSMContext):
    def is_number_using_regex(s):
        pattern = r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$'
        return re.match(pattern, s) is not None
    if is_number_using_regex(msg.text):
        async with state.proxy() as data:
            data["discount"] = msg.text
        dishes = await get_furniturees_in_category(data["cat_name"], data["subcat"])
        dish = dishes[int(data["place"])]
        await change_discount(dish, data["discount"])
        await state.finish()
        await bot.send_message(
            msg.from_user.id,
            'Успешно'
        )
        await cmd_admin(msg)
    else:
        await bot.send_message(
            msg.from_user.id,
            'Вы допустили ошибку, попробуйте еще раз'
        )
        return



@dp.callback_query_handler(lambda c: 'admin_edit_des' in c.data)
@admin_access
async def admin_edit_description(callback_query: types.CallbackQuery, state: FSMContext):
    cat_name = callback_query.data.split(':')[1]
    place = int(callback_query.data.split(':')[2])
    subcat = callback_query.data.split(':')[3]
    await admin_states.AdminEditDescription.cat_name.set()
    async with state.proxy() as data:
        data["cat_name"] = cat_name
        data["place"] = place
        data["subcat"] = subcat
    await admin_states.AdminEditDescription.description.set()
    await bot.send_message(
        callback_query.from_user.id,
        'Введите новое описание'
    )


@dp.message_handler(state=admin_states.AdminEditDescription.description)
@admin_access
async def admin_edit_description_state(msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data["description"] = msg.html_text
        dishes = await get_furniturees_in_category(data["cat_name"], data["subcat"])
        dish = dishes[int(data["place"])]
        await edit_description(data["description"], dish)
        await state.finish()
        await bot.send_message(
            msg.from_user.id,
            'Успешно'
        )
        await cmd_admin(msg)



@dp.callback_query_handler(lambda c: 'admin_edit_comp' in c.data)
@admin_access
async def admin_edit_composition(callback_query: types.CallbackQuery, state: FSMContext):
    cat_name = callback_query.data.split(':')[1]
    place = int(callback_query.data.split(':')[2])
    subcat = callback_query.data.split(':')[3]
    await admin_states.AdminEditComposition.cat_name.set()
    async with state.proxy() as data:
        data["cat_name"] = cat_name
        data["place"] = place
        data["subcat"] = subcat
    await admin_states.AdminEditComposition.composition.set()
    await bot.send_message(
        callback_query.from_user.id,
        'Введите новый Характеристики'
    )


@dp.message_handler(state=admin_states.AdminEditComposition.composition)
@admin_access
async def admin_edit_composition_state(msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data["composition"] = msg.html_text
        dishes = await get_furniturees_in_category(data["cat_name"], data["subcat"])
        dish = dishes[int(data["place"])]
        await edit_composition(data["composition"], dish)
        await state.finish()
        await bot.send_message(
            msg.from_user.id,
            'Успешно'
        )
        await cmd_admin(msg)


@dp.callback_query_handler(lambda c: 'admin_edit_na' in c.data)
@admin_access
async def admin_edit_name(callback_query: types.CallbackQuery, state: FSMContext):
    cat_name = callback_query.data.split(':')[1]
    place = int(callback_query.data.split(':')[2])
    subcat = callback_query.data.split(':')[3]
    await admin_states.AdminEditName.cat_name.set()
    async with state.proxy() as data:
        data["cat_name"] = cat_name
        data["place"] = place
        data["subcat"] = subcat
    await admin_states.AdminEditName.name.set()
    await bot.send_message(
        callback_query.from_user.id,
        'Введите новое имя'
    )


@dp.message_handler(state=admin_states.AdminEditName.name)
@admin_access
async def admin_edit_composition_state(msg: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data["name"] = msg.html_text
        dishes = await get_furniturees_in_category(data["cat_name"], data["subcat"])
        dish = dishes[int(data["place"])]
        for user in dict(carts):
            if dish in dict(carts)[user]:
                ed = carts[user][dish]
                del carts[user][dish]
                carts[user][data['name']] = ed
        await edit_name(data["name"], dish)
        await state.finish()
        await bot.send_message(
            msg.from_user.id,
            'Успешно'
        )
        await cmd_admin(msg)



@dp.callback_query_handler(lambda c: 'admin_edit_ph' in c.data)
@admin_access
async def admin_edit_photo(callback_query: types.CallbackQuery, state: FSMContext):
    cat_name = callback_query.data.split(':')[1]
    place = int(callback_query.data.split(':')[2])
    subcat = callback_query.data.split(':')[3]
    await admin_states.AdminEditPhoto.photo.set()
    async with state.proxy() as data:
        data["cat_name"] = cat_name
        data["place"] = place
        data["subcat"] = subcat
    await admin_states.AdminEditPhoto.photo.set()
    await bot.send_message(
        callback_query.from_user.id,
        'Отправьте ОДНУ фотографию'
    )

@dp.message_handler(content_types=[ContentType.PHOTO], state=admin_states.AdminEditPhoto.photo)
@admin_access
async def admin_edit_photo_state(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        dishes = await get_furniturees_in_category(data["cat_name"], data["subcat"])
        dish = dishes[int(data["place"])]
        transliterated_text = transliterate.translit(dish, 'ru', reversed=True)
        words = transliterated_text.split()
        snake_case_text = '_'.join(words)
        data["photo"] = snake_case_text + '.jpg'
    path = f'static/{snake_case_text}.jpg'
    await msg.photo[-1].download(path)
    await edit_photo(data['photo'], dish)
    await state.finish()
    await bot.send_message(
        msg.from_user.id,
        'Успешно'
    )
    await cmd_admin(msg)



@dp.callback_query_handler(lambda c: c.data == 'admin_create_promocode')
@admin_access
async def admin_create_promocode(callbcak_query: types.CallbackQuery):
    await admin_states.AdminCreatePromocode.discount.set()
    await bot.send_message(
        callbcak_query.from_user.id,
        'Введите процент скидки:'
    )

@dp.message_handler(state=admin_states.AdminCreatePromocode.discount)
@admin_access
async def admin_create_promocode_state(msg: types.Message, state: FSMContext):
    async def generate_promo_code(length=10):
        promo_list = await get_promocodes()
        characters = string.ascii_letters + string.digits  # буквы и цифры
        promo_code = ''.join(random.choice(characters) for _ in range(length))
        if promo_code not in promo_list:
            return promo_code
        else:
            await generate_promo_code()
    if msg.text.isdigit():
        async with state.proxy() as data:
            data["discount"] = msg.text
        await state.finish()
        promocode = await generate_promo_code()
        await create_promocode(promocode, int(data["discount"]))
        await bot.send_message(
            msg.from_user.id,
            f'Промокод на скидку {data["discount"]}% сформирован: <code>{promocode}</code>'
        )
    else:
        await bot.send_message(
            msg.from_user.id,
            'Введите число!'
        )
        return
    

@dp.callback_query_handler(lambda c: c.data == 'admin_find_furniture')
@admin_access
async def admin_find_furniture(callback_query: types.CallbackQuery):
    await admin_states.AdminFindFurniture.name.set()
    await bot.send_message(
        callback_query.from_user.id,
        'Введите имя товара:'
    )

@dp.message_handler(state=admin_states.AdminFindFurniture.name)
@admin_access
async def admin_find_furniture_state(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = msg.text
    await state.finish()
    furniture_data = await get_furniture_data(data["name"])
    if furniture_data:
        furniturees = await admin_get_furniturees_in_category(furniture_data['category'])
        place = furniturees.index(furniture_data["name"])
        await admin_in_cat_edit(msg, place, furniture_data['category'], furniture_data['subcategory'])
    else:
        await bot.send_message(
            msg.from_user.id,
            'Такого товара не существует'
        )

        


@dp.callback_query_handler(lambda c: c.data == 'admin_edit_inf_delivery')
@admin_access
async def admin_edit_inf_delivery(callback_query: types.CallbackQuery):
    await admin_states.AdminChangeDelivery.text.set()
    await bot.send_message(
        callback_query.from_user.id,
        'Введите текст:'
    )

@dp.message_handler(state=admin_states.AdminChangeDelivery.text)
@admin_access
async def admin_edit_inf_delivery_state(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = msg.html_text
    await state.finish()
    await change_delivery(data["text"])
    await bot.send_message(
        msg.from_user.id,
        'Успешно!'
    )

@dp.callback_query_handler(lambda c: c.data == 'admin_edit_inf_about_us')
@admin_access
async def admin_edit_inf_about_us(callback_query: types.CallbackQuery):
    await admin_states.AdminChangeAboutUs.text.set()
    await bot.send_message(
        callback_query.from_user.id,
        'Введите текст:'
    )

@dp.message_handler(state=admin_states.AdminChangeAboutUs.text)
@admin_access
async def admin_edit_inf_about_us_state(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = msg.html_text
    await state.finish()
    await change_about_us(data["text"])
    await bot.send_message(
        msg.from_user.id,
        'Успешно!'
    )

            
        
        



from utils.dump import dump_dict

@dp.message_handler(commands='create_backups')
@admin_access
async def admin_create_backups(msg: types.Message):
    up = await dump_dict(carts, word_list)
    if up:
        await bot.send_message(
            msg.from_user.id,
            'Бэкап создан'
        )
    else:
        await bot.send_message(
            msg.from_user.id,
            'Что-то пошло не так'
        )




def load_data():
    global carts, word_list
    try:
        with open('backups/dump.pkl', 'rb') as file:
            carts = pickle.load(file)
        with open('backups/word_list.pkl', 'rb') as file:
            word_list = pickle.load(file)
    except:
        pass


from utils.scheduler import start_schedule

if __name__ == '__main__':
    start_db()
    load_data()
    scheduler = AsyncIOScheduler()
    thread_backup_dict_of_profiles = threading.Thread(target=start_schedule, daemon=True, args=(scheduler, carts, word_list))
    thread_backup_dict_of_profiles.start()
    scheduler.start()

    executor.start_polling(dp, skip_updates=True)

