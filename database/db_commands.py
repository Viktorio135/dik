from .models import *

from sqlalchemy.orm import Session
from sqlalchemy import or_
from asgiref.sync import sync_to_async

import datetime


@sync_to_async
def create_transaction(user_id, phone_number, coast, is_online, furniturees):
    with Session(autoflush=False, bind=engine) as session:
        try:
            transaction = Transactions(
                user_id=user_id,
                phone_number=phone_number,
                date=datetime.datetime.now(),
                coast=coast,
                is_online=is_online,
                furnitures=furniturees
            )
            session.add(transaction)
            session.commit()
            return transaction.id
        except:
            return 0




@sync_to_async
def create_user(user_id, name, phone, user_name):
    try:
        with Session(autoflush=False, bind=engine) as session:
            user = User(user_id=user_id, name=name, phone=phone, user_name=user_name)
            session.add(user)
            session.commit()
            return 1
    except: 
        return 0
    

@sync_to_async
def get_user_data(user_id):
    with Session(autoflush=False, bind=engine) as session:
        user = session.query(User).filter(User.user_id == str(user_id)).first()
        if user:
            return {
                'name': user.name,
                'phone': user.phone,
                'user_name': user.user_name
            }
        else:
            return None
    

@sync_to_async
def get_user_history(user_id):
    with Session(autoflush=False, bind=engine) as session:
        sp = []
        ls = session.query(Transactions).filter(Transactions.user_id == str(user_id)).all()
        if not ls:
            return None
        for his in ls:
            sp.append(his)
        return sp
            



@sync_to_async
def has_register(user_id):
    with Session(autoflush=False, bind=engine) as session:
        user = session.query(User).filter(User.user_id == str(user_id)).first()
        if user:
            return 1
        else:
            return 0
        

@sync_to_async
def get_category():
    with Session(autoflush=False, bind=engine) as session:
        category = session.query(Category).all()
        if category:
            return [cat.name for cat in category]
        else:
            return None
        

@sync_to_async
def get_subcategory(cat):
    with Session(autoflush=False, bind=engine) as session:
        subcategory = session.query(Subcategory).filter(Subcategory.category == cat).all()
        if subcategory:
            return [cat.name for cat in subcategory]
        else:
            return None


@sync_to_async
def get_furniturees_in_category(cat_name, subcat_name):
    with Session(autoflush=False, bind=engine) as session:
        furniturees = session.query(Furniture).filter(Furniture.category == cat_name).filter(Furniture.subcategory == subcat_name).filter(Furniture.is_active == True).all()
    if furniturees:
        return [furniture.name for furniture in furniturees]
    else:
        return None
    
@sync_to_async
def get_furniture_data(name):
    with Session(autoflush=False, bind=engine) as session:
        furniture = session.query(Furniture).filter(Furniture.name == name).first()
        if furniture:
            return {
                'name': furniture.name,
                'category': furniture.category,
                'subcategory': furniture.subcategory,
                'photo': furniture.photo,
                'description': furniture.description,
                'composition': furniture.caracteristic,
                'price': furniture.price,
                'discount': furniture.discount,
                'is_active': furniture.is_active
            }
        else:
            return None
        


@sync_to_async
def get_admin_list():
    with Session(autoflush=False, bind=engine) as session:
        admins = session.query(Admins).all()
        sp = []
        if admins:
            for admin in admins:
                sp.append(admin.user_id)
        return sp
    

@sync_to_async
def change_active(name):
    with Session(autoflush=False, bind=engine) as session:
        furniture = session.query(Furniture).filter(Furniture.name == name).first()
        if furniture.is_active:
            furniture.is_active = False
        else:
            furniture.is_active = True
        session.commit()



@sync_to_async
def admin_get_furniturees_in_category(cat_name):
    with Session(autoflush=False, bind=engine) as session:
        furniturees = session.query(Furniture).filter(Furniture.category == cat_name).all()
    if furniturees:
        return [furniture.name for furniture in furniturees]
    else:
        return None
    

@sync_to_async
def admin_delete_furniture(name):
    with Session(autoflush=False, bind=engine) as session:
        furniture = session.query(Furniture).filter(Furniture.name == name).delete()
        session.commit()

@sync_to_async
def admin_del_subcategory(name):
    with Session(autoflush=False, bind=engine) as session:
        sub = session.query(Subcategory).filter(Subcategory.name == name).delete()
        session.commit()

@sync_to_async
def create_category(name):
    with Session(autoflush=False, bind=engine) as session:
        cat = Category(name=name)
        session.add(cat)
        session.commit()


@sync_to_async
def create_subcategory(category, name):
    with Session(autoflush=False, bind=engine) as session:
        subcat = Subcategory(category=category, name=name)
        session.add(subcat)
        session.commit()


@sync_to_async
def delete_category(name):
    with Session(autoflush=False, bind=engine) as session:
        cat = session.query(Category).filter(Category.name == name).delete()
        session.commit()

# @sync_to_async
def create_furniture(name, photo, description, caracteristic, price, category, subcategory):
    with Session(autoflush=False, bind=engine) as session:
        furniture = Furniture(
            name=name,
            photo=photo,
            description=description,
            caracteristic=caracteristic,
            price=price,
            is_active=True,
            category=category,
            subcategory=subcategory,
        )

        session.add(furniture)
        session.commit()
        

@sync_to_async
def edit_price(price, dish):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(Furniture).filter(Furniture.name == dish).first()
        if obj:
            obj.price = float(price)
            session.commit()


@sync_to_async
def edit_description(description, dish):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(Furniture).filter(Furniture.name == dish).first()
        if obj:
            obj.description = description
            session.commit()

        
@sync_to_async
def edit_composition(caracteristic, dish):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(Furniture).filter(Furniture.name == dish).first()
        if obj:
            obj.caracteristic = caracteristic
            session.commit()

@sync_to_async
def edit_photo(photo, dish):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(Furniture).filter(Furniture.name == dish).first()
        if obj:
            obj.photo = photo
            session.commit()

@sync_to_async
def edit_name(name, dish):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(Furniture).filter(Furniture.name == dish).first()
        if obj:
            obj.name = name
            session.commit()


@sync_to_async
def get_promocodes():
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(Promocodes).all()
        sp = []
        if obj:
            for code in obj:
                sp.append(code.code)
            return sp
        return []
    
@sync_to_async
def check_promocode(code):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(Promocodes).filter(Promocodes.code == code).first()
        if obj:
            return obj.discount
        return None

        
@sync_to_async
def create_promocode(code, discount):
    with Session(autoflush=False, bind=engine) as session:
        promocode = Promocodes(
            code=code,
            discount=discount
        )
        session.add(promocode)
        session.commit()

@sync_to_async
def delete_promocode(code):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(Promocodes).filter(Promocodes.code == code)
        if obj:
            obj.delete()
            session.commit()

@sync_to_async
def search_furniture_db(words):
    search_pattern = f"%{words}%"
    
    with Session(autoflush=False, bind=engine) as session:
        objs = session.query(Furniture).filter(
            or_(
                Furniture.name.ilike(search_pattern),
                Furniture.description.ilike(search_pattern),
                Furniture.caracteristic.ilike(search_pattern),
                Furniture.category.ilike(search_pattern),
                Furniture.subcategory.ilike(search_pattern)
            )
        ).all()
        
        return objs
    
@sync_to_async
def get_dilivery_db(user_id):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(User).filter(User.user_id == str(user_id)).first()
        if obj:
            return obj.delivery
        return 0
    
@sync_to_async
def change_delivery(user_id, delivery):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(User).filter(User.user_id == str(user_id)).first()
        if obj:
            obj.delivery = delivery
            session.commit()



@sync_to_async
def get_discount_list():
    with Session(autoflush=False, bind=engine) as session:
        objs = session.query(Furniture).filter(Furniture.discount != 0).all()
        if objs:
            return objs
        
@sync_to_async
def change_discount(name, discount):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(Furniture).filter(Furniture.name == name).first()
        if obj:
            obj.discount = float(discount)
            session.commit()


@sync_to_async
def get_count_orders(user_id):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(Transactions).filter(Transactions.user_id == str(user_id)).count()
        if obj:
            return obj
        return 0
    
@sync_to_async
def change_delivery(text):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(Information).filter(Information.id == 1).first()
        if obj:
            obj.delivery = text
            session.commit()

@sync_to_async
def change_about_us(text):
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(Information).filter(Information.id == 1).first()
        if obj:
            obj.about_us = text
            session.commit()

@sync_to_async
def get_delivery():
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(Information).filter(Information.id == 1).first()
        if obj:
            return obj.delivery
        return 'NONE'
    
@sync_to_async
def get_about_us():
    with Session(autoflush=False, bind=engine) as session:
        obj = session.query(Information).filter(Information.id == 1).first()
        if obj:
            return obj.about_us
        return 'NONE'
    