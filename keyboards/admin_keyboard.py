from aiogram.types import (
    InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, 
    InlineKeyboardButton, 
    KeyboardButton
)
from database.db_commands import get_category, get_subcategory


def admin_main_kb():
    btn1 = InlineKeyboardButton(text='Редактировать каталог', callback_data='admin_edit_menu')
    btn2 = InlineKeyboardButton(text='Новый товар', callback_data='admin_new_furniture')
    btn3 = InlineKeyboardButton(text='Добавить категорию', callback_data='admin_new_category')
    btn4 = InlineKeyboardButton(text='Удалить категорию', callback_data='admin_delete_category')
    btn5 = InlineKeyboardButton(text='Добавить подкатегорию', callback_data='admin_new_subcategory')
    btn6 = InlineKeyboardButton(text='Удалить подкатегорию', callback_data='admin_delete_subcategory')
    btn7 = InlineKeyboardButton(text='Создать промокод', callback_data='admin_create_promocode')
    btn8 = InlineKeyboardButton(text='Поиск', callback_data='admin_find_furniture')
    btn9 = InlineKeyboardButton(text='Изменить доставку', callback_data='admin_edit_inf_delivery')
    btn10 = InlineKeyboardButton(text='Изменить О нас', callback_data='admin_edit_inf_about_us')
    keyboard = InlineKeyboardMarkup().add(btn1, btn2).add(btn3, btn4).add(btn5, btn6).add(btn7, btn8).add(btn9, btn10)
    return keyboard


async def admin_get_category_kb():
    category = await get_category()
    keyboard = InlineKeyboardMarkup()
    if category:
        for cat in category:
            btn = InlineKeyboardButton(text=cat, callback_data=f'admin_in_cat_edit:{cat}')
            keyboard.add(btn)
    else:
        btn = InlineKeyboardButton(text='Тут пока ничего нет', callback_data='nothing')
        keyboard.add(btn)
    return keyboard


async def admin_get_category_for_del_sub_kb():
    category = await get_category()
    keyboard = InlineKeyboardMarkup()
    if category:
        for cat in category:
            btn = InlineKeyboardButton(text=cat, callback_data=f'admin_get_category_for_del_sub:{cat}')
            keyboard.add(btn)
    else:
        btn = InlineKeyboardButton(text='Тут пока ничего нет', callback_data='nothing')
        keyboard.add(btn)
    return keyboard




def admin_get_furniturees_in_category_kb(cat_name, place, is_active, subcat, is_find=False):
    if not is_find:
        if is_active:
            btn1 = InlineKeyboardButton(text='👈', callback_data=f'menu_admin_l:{cat_name}:{place}:{subcat}')
            btn2 = InlineKeyboardButton(text='👉', callback_data=f'menu_admin_n:{cat_name}:{place}:{subcat}')
            btn3 = InlineKeyboardButton(text='Убрать из каталога', callback_data=f'admin_deactive_f:{cat_name}:{place}:{subcat}')
            btn4 = InlineKeyboardButton(text='Удалить', callback_data=f'admin_del_f:{cat_name}:{place}:{subcat}')
            btn6 = InlineKeyboardButton(text='Изменить цену', callback_data=f'admin_edit_pr:{cat_name}:{place}:{subcat}')
            btn7 = InlineKeyboardButton(text='Изменить Описание', callback_data=f'admin_edit_des:{cat_name}:{place}:{subcat}')
            btn8 = InlineKeyboardButton(text='Изменить Характеристики', callback_data=f'admin_edit_comp:{cat_name}:{place}:{subcat}')
            btn9 = InlineKeyboardButton(text='Изменить фото', callback_data=f'admin_edit_ph:{cat_name}:{place}:{subcat}')
            btn10 = InlineKeyboardButton(text='Изменить имя', callback_data=f'admin_edit_na:{cat_name}:{place}:{subcat}')
            btn11 = InlineKeyboardButton(text='Скдика', callback_data=f'admin_edit_dis:{cat_name}:{place}:{subcat}')
            btn5 = InlineKeyboardButton(text='⬅️', callback_data='from_admin_furniture_to_back')
            keyboard = InlineKeyboardMarkup().add(btn1, btn2).add(btn4).add(btn6, btn7).add(btn8, btn9).add(btn10, btn11).add(btn3).add(btn5)
            return keyboard
        else:
            btn1 = InlineKeyboardButton(text='👈', callback_data=f'menu_admin_l:{cat_name}:{place}:{subcat}')
            btn2 = InlineKeyboardButton(text='👉', callback_data=f'menu_admin_n:{cat_name}:{place}:{subcat}')
            btn3 = InlineKeyboardButton(text='Вернуть в каталог', callback_data=f'admin_deactive_f:{cat_name}:{place}:{subcat}')
            btn4 = InlineKeyboardButton(text='Удалить', callback_data=f'admin_del_f:{cat_name}:{place}:{subcat}')
            btn6 = InlineKeyboardButton(text='Изменить цену', callback_data=f'admin_edit_pr:{cat_name}:{place}:{subcat}')
            btn7 = InlineKeyboardButton(text='Изменить Описание', callback_data=f'admin_edit_des:{cat_name}:{place}:{subcat}')
            btn8 = InlineKeyboardButton(text='Изменить Характеристики', callback_data=f'admin_edit_comp:{cat_name}:{place}:{subcat}')
            btn9 = InlineKeyboardButton(text='Изменить фото', callback_data=f'admin_edit_ph:{cat_name}:{place}:{subcat}')
            btn10 = InlineKeyboardButton(text='Изменить имя', callback_data=f'admin_edit_na:{cat_name}:{place}:{subcat}')
            btn5 = InlineKeyboardButton(text='⬅️', callback_data='from_admin_furniture_to_back')
            btn11 = InlineKeyboardButton(text='Скдика', callback_data=f'admin_edit_dis:{cat_name}:{place}:{subcat}')

            keyboard = InlineKeyboardMarkup().add(btn1, btn2).add(btn4).add(btn6, btn7).add(btn8, btn9).add(btn10, btn11).add(btn3).add(btn5)
            
            return keyboard
    else:
        if is_active:
            btn3 = InlineKeyboardButton(text='Убрать из каталога', callback_data=f'admin_deactive_f:{cat_name}:{place}:{subcat}')
            btn4 = InlineKeyboardButton(text='Удалить', callback_data=f'admin_del_f:{cat_name}:{place}:{subcat}')
            btn6 = InlineKeyboardButton(text='Изменить цену', callback_data=f'admin_edit_pr:{cat_name}:{place}:{subcat}')
            btn7 = InlineKeyboardButton(text='Изменить Описание', callback_data=f'admin_edit_des:{cat_name}:{place}:{subcat}')
            btn8 = InlineKeyboardButton(text='Изменить Характеристики', callback_data=f'admin_edit_comp:{cat_name}:{place}:{subcat}')
            btn9 = InlineKeyboardButton(text='Изменить фото', callback_data=f'admin_edit_ph:{cat_name}:{place}:{subcat}')
            btn10 = InlineKeyboardButton(text='Изменить имя', callback_data=f'admin_edit_na:{cat_name}:{place}:{subcat}')
            btn11 = InlineKeyboardButton(text='Скдика', callback_data=f'admin_edit_dis:{cat_name}:{place}:{subcat}')
            keyboard = InlineKeyboardMarkup().add(btn4).add(btn6, btn7).add(btn8, btn9).add(btn10, btn11).add(btn3)
            return keyboard
        else:
            btn3 = InlineKeyboardButton(text='Вернуть в каталог', callback_data=f'admin_deactive_f:{cat_name}:{place}:{subcat}')
            btn4 = InlineKeyboardButton(text='Удалить', callback_data=f'admin_del_f:{cat_name}:{place}:{subcat}')
            btn6 = InlineKeyboardButton(text='Изменить цену', callback_data=f'admin_edit_pr:{cat_name}:{place}:{subcat}')
            btn7 = InlineKeyboardButton(text='Изменить Описание', callback_data=f'admin_edit_des:{cat_name}:{place}:{subcat}')
            btn8 = InlineKeyboardButton(text='Изменить Характеристики', callback_data=f'admin_edit_comp:{cat_name}:{place}:{subcat}')
            btn9 = InlineKeyboardButton(text='Изменить фото', callback_data=f'admin_edit_ph:{cat_name}:{place}:{subcat}')
            btn10 = InlineKeyboardButton(text='Изменить имя', callback_data=f'admin_edit_na:{cat_name}:{place}:{subcat}')
            btn11 = InlineKeyboardButton(text='Скдика', callback_data=f'admin_edit_dis:{cat_name}:{place}:{subcat}')

            keyboard = InlineKeyboardMarkup().add(btn4).add(btn6, btn7).add(btn8, btn9).add(btn10, btn11).add(btn3)
            
            return keyboard
    
    


def admin_del_task_back_kb():
    btn1 = InlineKeyboardButton(text='⬅️', callback_data='from_admin_dish_to_back')
    keyboard = InlineKeyboardMarkup().add(btn1)
    return keyboard


def admin_add_new_cat_conf_kb():
    btn1 = InlineKeyboardButton(text='Да', callback_data='new_conf_cat:yes')
    btn2 = InlineKeyboardButton(text='Отмена', callback_data='new_conf_cat:no')
    keyboard = InlineKeyboardMarkup().add(btn1, btn2)
    return keyboard


def admin_add_new_subcat_conf_kb():
    btn1 = InlineKeyboardButton(text='Да', callback_data='new_subconf_cat:yes')
    btn2 = InlineKeyboardButton(text='Отмена', callback_data='new_subconf_cat:no')
    keyboard = InlineKeyboardMarkup().add(btn1, btn2)
    return keyboard




async def admin_add_subcategory_kb():
    category = await get_category()
    keyboard = InlineKeyboardMarkup()
    if category:
        for cat in category:
            btn = InlineKeyboardButton(text=cat, callback_data=f'admin_kb_add_sub:{cat}')
            keyboard.add(btn)
    else:
        btn = InlineKeyboardButton(text='Тут пока ничего нет', callback_data='nothing')
        keyboard.add(btn)
    return keyboard



async def admin_delete_category_kb():
    category = await get_category()
    keyboard = InlineKeyboardMarkup()
    if category:
        for cat in category:
            btn = InlineKeyboardButton(text=cat, callback_data=f'admin_del_cat:{cat}')
            keyboard.add(btn)
    else:
        btn = InlineKeyboardButton(text='Тут пока ничего нет', callback_data='nothing')
        keyboard.add(btn)
    return keyboard

def admin_delete_category_conf_kb(cat_name):
    btn1 = InlineKeyboardButton(text='Да', callback_data=f'admin_conf_del_cat:{cat_name}:yes')
    btn2 = InlineKeyboardButton(text='Отмена', callback_data=f'admin_conf_del_cat:{cat_name}:no')
    keyboard = InlineKeyboardMarkup().add(btn1, btn2)
    return keyboard

async def admin_set_category_for_new_furniture():
    category = await get_category()
    keyboard = InlineKeyboardMarkup()
    if category:
        for cat in category:
            btn = InlineKeyboardButton(text=cat, callback_data=f'admin_set_cat:{cat}')
            keyboard.add(btn)
    else:
        btn = InlineKeyboardButton(text='Тут пока ничего нет', callback_data='nothing')
        keyboard.add(btn)
    return keyboard

async def admin_set_subcategory_for_new_furniture(cat_name):
    subcategory = await get_subcategory(cat_name)
    keyboard = InlineKeyboardMarkup()
    if subcategory:
        for cat in subcategory:
            btn = InlineKeyboardButton(text=cat, callback_data=f'admin_set_subcat:{cat}')
            keyboard.add(btn)
    else:
        btn = InlineKeyboardButton(text='Тут пока ничего нет', callback_data='nothing')
        keyboard.add(btn)
    return keyboard

async def admin_edit_menu_subcat_kb(cat_name):
    subcategory = await get_subcategory(cat_name)
    keyboard = InlineKeyboardMarkup()
    if subcategory:
        for cat in subcategory:
            btn = InlineKeyboardButton(text=cat, callback_data=f'admin_subcat_edit_menu:{cat_name}:{cat}')
            keyboard.add(btn)
    else:
        btn = InlineKeyboardButton(text='Тут пока ничего нет', callback_data='nothing')
        keyboard.add(btn)
    return keyboard



async def admin_del_subcategory_kb(cat_name):
    subcategory = await get_subcategory(cat_name)
    keyboard = InlineKeyboardMarkup()
    if subcategory:
        for cat in subcategory:
            btn = InlineKeyboardButton(text=cat, callback_data=f'admin_kb_del_subcat:{cat}')
            keyboard.add(btn)
    else:
        btn = InlineKeyboardButton(text='Тут пока ничего нет', callback_data='nothing')
        keyboard.add(btn)
    return keyboard


def admin_new_furniture_conf():
    btn1 = InlineKeyboardButton(text='Всё верно', callback_data='admin_new_conf:yes')
    btn2 = InlineKeyboardButton(text='Отмена', callback_data='admin_new_conf:no')
    keyboard = InlineKeyboardMarkup().add(btn1, btn2)
    return keyboard