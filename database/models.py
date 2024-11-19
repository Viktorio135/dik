import os
from dotenv import load_dotenv
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Boolean, 
    Text, 
    DateTime,
    create_engine,
    Float,
    JSON
)
from sqlalchemy.ext.declarative import declarative_base


# Загрузка переменных окружения
load_dotenv()

user_bd = os.getenv('USER_BD')
password = os.getenv('PASSWORD')
host = os.getenv('HOST')
database = os.getenv('DATABASE')

# Базовый класс для декларативного стиля
Base = declarative_base()

# Создание движка для подключения к базе данных
engine = create_engine(f"mysql+mysqlconnector://{user_bd}:{password}@{host}/{database}")

class User(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(20))
    user_name = Column(String(100))
    name = Column(String(50))
    phone = Column(String(15))
    delivery = Column(Text(1000), default='')

class Category(Base):
    __tablename__ = 'Category'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

class Subcategory(Base):
    __tablename__ = 'Subcategory'
    id = Column(Integer, primary_key=True)
    category = Column(String(50))
    name = Column(String(50))

class Furniture(Base):
    __tablename__ = 'Furniture'
    id = Column(Integer, primary_key=True)
    name = Column(String(300))
    photo = Column(String(300))
    description = Column(Text(1000))
    caracteristic = Column(Text(100))
    price = Column(Float)
    discount = Column(Float, default=0)
    is_active = Column(Boolean, default=True)
    category = Column(String(50))
    subcategory = Column(String(50))


class Promocodes(Base):
    __tablename__ = 'Promocodes'
    id = Column(Integer, primary_key=True)
    code = Column(String(10))
    discount = Column(Float)


class Information(Base):
    __tablename__ = 'Information'
    id = Column(Integer, primary_key=True)
    delivery = Column(Text(4000))
    about_us = Column(Text(4000))




class Transactions(Base):
    __tablename__ = 'Transactions'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50))
    phone_number = Column(String(20))
    date = Column(DateTime)
    coast = Column(Float)
    furnitures = Column(JSON)
    is_online = Column(Boolean)


class Admins(Base):
    __tablename__ = 'Admins'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50))


def start_db():
    Base.metadata.create_all(bind=engine, checkfirst=True)


