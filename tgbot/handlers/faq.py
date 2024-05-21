from aiogram import types, Bot
from aiogram.fsm.context import FSMContext

from dj_admin.models import Question
from tgbot.keyboards.inline import get_catalog_ikb
from tgbot.orm.commands import get_faq_questions, ask_or_record_question, get_answer_on_question
from tgbot.settings import PREF
from tgbot.utils.statesform import StepsFSM


async def get_questions(msg: types.Message, bot: Bot, state: FSMContext):
    qst_list = await get_faq_questions()
    if await state.get_state() == StepsFSM.faq_question:
        data = await state.get_data()
        if msg_faq_id := data.get('msg_faq_id'):
            await bot.edit_message_reply_markup(msg.chat.id, msg_faq_id, reply_markup=None)
    await state.set_state(StepsFSM.faq_question)
    msg_id: types.Message = await msg.answer('Часто задаваемые вопросы:', reply_markup=get_catalog_ikb(qst_list, PREF.question))
    await msg.answer('Если ответа нет, задайте свой!')
    await state.update_data({'msg_faq_id': msg_id.message_id, 'questions': qst_list})


async def get_questions_page(cbk: types.CallbackQuery, bot: Bot, state: FSMContext):
    page = int(cbk.data.removeprefix(f"{PREF.question}_page_"))
    data = await state.get_data()
    result: list[Question] = data.get('questions')
    await cbk.message.edit_reply_markup(reply_markup=get_catalog_ikb(result, PREF.question, page=page))
    await cbk.answer()


async def get_answer(cbk: types.CallbackQuery, bot: Bot, state: FSMContext):
    qst_id = int(cbk.data.removeprefix(f"{PREF.question}_select_"))
    answer = await get_answer_on_question(qst_id)
    await cbk.message.answer(answer.answer)
    await cbk.answer()


async def ask_question(msg: types.Message, bot: Bot, state: FSMContext):
    if answer := await ask_or_record_question(msg.text):
        await msg.answer(answer.answer)
    else:
        await msg.answer('Мы записали ваш вопрос. После ответа специалистов он появится в списке вопросов.')
