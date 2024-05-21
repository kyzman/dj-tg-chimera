from aiogram.fsm.state import StatesGroup, State


class StepsFSM(StatesGroup):
    select_item = State()
    item_selected = State()
    item_added = State()
    item_removed = State()
    cart_order = State()
    cart_ordered = State()
    faq_question = State()
