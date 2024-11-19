from aiogram.dispatcher.filters.state import State, StatesGroup

class Registration(StatesGroup):
    name = State()
    phone_number = State()

class UsePromocode(StatesGroup):
    code = State()

class SearchFurniture(StatesGroup):
    words = State()
    
class Delivery(StatesGroup):
    delivery = State()

