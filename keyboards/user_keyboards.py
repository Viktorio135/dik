from aiogram.types import (
    InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, 
    InlineKeyboardButton, 
    KeyboardButton
)

from database.db_commands import get_category, get_subcategory



def get_contact_kb():
    btn1 = KeyboardButton(text='Отправить номер телефона 📱', request_contact=True)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(btn1)
    return keyboard


def main_menu_kb():
    btn1 = KeyboardButton(text='📝 Каталог')
    btn2 = KeyboardButton(text='📍 О нас')
    btn3 = KeyboardButton(text='🚛 Доставка')
    btn4 = KeyboardButton(text='📦 Мои заказы')
    btn5 = KeyboardButton(text='🛒 Корзина')
    btn6 = KeyboardButton(text='💸 Скидки')
    btn7 = KeyboardButton(text='🔎 Поиск товара')
    btn8 = KeyboardButton(text='🛟 Помощь')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(btn1, btn5).add(btn4, btn6).add(btn2, btn3).add(btn7, btn8)
    return keyboard


async def get_category_kb():
    category = await get_category()
    keyboard = InlineKeyboardMarkup()
    if category:
        for cat in category:
            btn = InlineKeyboardButton(text=cat, callback_data=f'menu_in_category:{cat}')
            keyboard.add(btn)
    else:
        btn = InlineKeyboardButton(text='Тут пока ничего нет', callback_data='nothing')
        keyboard.add(btn)
    return keyboard

async def get_subcategory_kb(cat):
    category = await get_subcategory(cat)
    keyboard = InlineKeyboardMarkup()
    if category:
        for subcat in category:
            btn = InlineKeyboardButton(text=subcat, callback_data=f'menu_in_subcat:{cat}:{subcat}')
            keyboard.add(btn)
    else:
        btn = InlineKeyboardButton(text='Тут пока ничего нет', callback_data='nothing')
        keyboard.add(btn)
    return keyboard


def get_furniturees_in_category_kb(cat_name, place, is_first, subcat):
    if is_first:
        btn1 = InlineKeyboardButton(text='👈', callback_data=f'menu_l:{cat_name}:{place}:{subcat}')
        btn2 = InlineKeyboardButton(text='👉', callback_data=f'menu_n:{cat_name}:{place}:{subcat}')
        btn3 = InlineKeyboardButton(text='✚', callback_data=f'add_in_c:{cat_name}:{place}:{subcat}')
        btn4 = InlineKeyboardButton(text='🛒 Корзина', callback_data='from_furniture_to_cart')
        btn5 = InlineKeyboardButton(text='⬅️', callback_data='from_furniture_to_back')
        keyboard = InlineKeyboardMarkup().add(btn3).add(btn4).add(btn1, btn2).add(btn5)
    else:
        btn1 = InlineKeyboardButton(text='👈', callback_data=f'menu_l:{cat_name}:{place}:{subcat}')
        btn2 = InlineKeyboardButton(text='👉', callback_data=f'menu_n:{cat_name}:{place}:{subcat}')
        btn3 = InlineKeyboardButton(text='✚', callback_data=f'add_in_c:{cat_name}:{place}:{subcat}')
        btn4 = InlineKeyboardButton(text='−', callback_data=f'del_in_c:{cat_name}:{place}:{subcat}')
        btn5 = InlineKeyboardButton(text='🛒 Корзина', callback_data='from_furniture_to_cart')
        btn6 = InlineKeyboardButton(text='⬅️', callback_data='from_furniture_to_back')
        keyboard = InlineKeyboardMarkup().add(btn3, btn4).add(btn5).add(btn1, btn2).add(btn6)
    return keyboard
    

def carts_kb():
    btn1 = InlineKeyboardButton(text='🚀 Оформить заказ', callback_data=f'create_order')
    # btn2 = InlineKeyboardButton(text='✏️ Редактировать', callback_data=f'change_cart')
    btn3 = InlineKeyboardButton(text='🗑️ Очистить', callback_data=f'clear_cart')
    btn4 = InlineKeyboardButton(text='💸 Применить промокод', callback_data='use_promocode')
    keyboard = InlineKeyboardMarkup().add(btn1).add(btn4).add(btn3)
    return keyboard

def change_cart_kb(furniturees):
    keyboard = InlineKeyboardMarkup()

    for furniture in furniturees:
        btn = InlineKeyboardButton(text=furniture, callback_data=f'change_furniture:{furniture}')
        keyboard.add(btn)
    return keyboard


def change_furniture_kb(furniture, is_first):
    keyboard = InlineKeyboardMarkup()
    if is_first:
        btn1 = InlineKeyboardButton(text='+', callback_data=f'append_furniture:{furniture}')
        btn2 = InlineKeyboardButton(text='🗑️ Удалить', callback_data=f'delete_furniture:{furniture}')
        btn3 = InlineKeyboardButton(text='⬅️', callback_data=f'change_back_furniture')
        keyboard.add(btn1).add(btn2).add(btn3)
    else:
        btn1 = InlineKeyboardButton(text='+', callback_data=f'append_furniture:{furniture}')
        btn2 = InlineKeyboardButton(text='🗑️ Удалить', callback_data=f'delete_furniture:{furniture}')
        btn3 = InlineKeyboardButton(text='⬅️', callback_data=f'change_back_furniture')
        btn4 = InlineKeyboardButton(text='-', callback_data=f'subtract_furniture:{furniture}')
        keyboard.add(btn1, btn4).add(btn2).add(btn3)
    return keyboard

def type_of_order_kb():
    btn1 = InlineKeyboardButton(text='Доставка', callback_data='order_type_dilivery')
    btn2 = InlineKeyboardButton(text='В пункте выдачи', callback_data='order_type_warehouse')
    keyboard = InlineKeyboardMarkup().add(btn1).add(btn2)
    return keyboard


def history_kb(data_list):
    keyboard = InlineKeyboardMarkup()
    for index, data in enumerate(data_list, start=0):
        btn = InlineKeyboardButton(text=data, callback_data=f'history_my_order:{index}')
        keyboard.add(btn)
    return keyboard


def history_order_kb(index):
    btn1 = InlineKeyboardButton(text='🔄 Повторить корзину', callback_data=f'repeat_cart:{index}')
    btn2 = InlineKeyboardButton(text='⬅️', callback_data='history_back_order')
    keyboard = InlineKeyboardMarkup().add(btn1).add(btn2)
    return keyboard


def search_furniture_kb(category, subcategory, place, is_one=False):
    keyboard = InlineKeyboardMarkup()
    if is_one:
        btn1 = InlineKeyboardButton(text='Открыть в каталоге', callback_data=f'op_in_cat:{category}:{subcategory}')
        keyboard.add(btn1)
    else:
        btn1 = InlineKeyboardButton(text='👈', callback_data=f'search_last:{place}')
        btn2 = InlineKeyboardButton(text='👉', callback_data=f'search_next:{place}')
        btn3 = InlineKeyboardButton(text='Открыть в каталоге', callback_data=f'op_in_cat:{category}:{subcategory}:{place}')
        keyboard.add(btn1, btn2).add(btn3)
    return keyboard


def delivery_is_true_kb():
    btn1 = InlineKeyboardButton(text='Всё верно', callback_data='del_is_true')
    btn2 = InlineKeyboardButton(text='Изменить', callback_data='change_in_ofline_delivery')
    keyboard = InlineKeyboardMarkup().add(btn1).add(btn2)
    return keyboard


def get_furnitures_in_discount_kb(place, is_first):
    if is_first:
        btn1 = InlineKeyboardButton(text='👈', callback_data=f'discount_last:{place}')
        btn2 = InlineKeyboardButton(text='👉', callback_data=f'discount_next:{place}')
        btn3 = InlineKeyboardButton(text='✚', callback_data=f'app_in_cart_with_disk:{place}')
        btn4 = InlineKeyboardButton(text='🛒 Корзина', callback_data='from_furniture_to_cart')
        keyboard = InlineKeyboardMarkup().add(btn3).add(btn4).add(btn1, btn2)
    else:
        btn1 = InlineKeyboardButton(text='👈', callback_data=f'discount_last:{place}')
        btn2 = InlineKeyboardButton(text='👉', callback_data=f'discount_next:{place}')
        btn3 = InlineKeyboardButton(text='✚', callback_data=f'app_in_cart_with_disk:{place}')
        btn4 = InlineKeyboardButton(text='−', callback_data=f'drop_in_cart_with_disk:{place}')
        btn5 = InlineKeyboardButton(text='🛒 Корзина', callback_data='from_furniture_to_cart')
        keyboard = InlineKeyboardMarkup().add(btn3, btn4).add(btn5).add(btn1, btn2)
    return keyboard

def help_kb():
    btn1 = InlineKeyboardButton(text='Заказать звонок', callback_data='book_a_call')
    btn2 = InlineKeyboardButton(text='Написать в поддержку', url='https://t.me/DIK_Furniture_bot')
    keyboard = InlineKeyboardMarkup().add(btn1, btn2)
    return keyboard