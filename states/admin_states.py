from aiogram.dispatcher.filters.state import State, StatesGroup


class AddNewCategory(StatesGroup):
    name = State()
    conf = State()

class AddNewSubcategory(StatesGroup):
    category = State()
    name = State()
    conf = State()


class AddNewfurniture(StatesGroup):
    name = State()
    photo = State()
    description = State()
    composition = State()
    price = State()
    category = State()
    subcategory = State()
    conf = State()

class AdminEditPrice(StatesGroup):
    cat_name = State()
    subcat = State()
    place = State()
    price = State()

class AdminEditDescription(StatesGroup):
    cat_name = State()
    subcat = State()
    place = State()
    description = State()

class AdminEditComposition(StatesGroup):
    cat_name = State()
    subcat = State()
    place = State()
    composition = State()

class AdminEditPhoto(StatesGroup):
    cat_name = State()
    subcat = State()
    place = State()
    photo = State()


class AdminEditName(StatesGroup):
    cat_name = State()
    subcat = State()
    place = State()
    name = State()

class AdminEditDiscount(StatesGroup):
    cat_name = State()
    subcat = State()
    place = State()
    discount = State()

class AdminFindFurniture(StatesGroup):
    name = State()


class AdminCreatePromocode(StatesGroup):
    discount = State()

class AdminChangeDelivery(StatesGroup):
    text = State()


class AdminChangeAboutUs(StatesGroup):
    text = State()