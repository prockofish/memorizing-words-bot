import asyncio, random
from aiogram import Dispatcher, F, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup as InMarkup, InlineKeyboardButton as InButton

from KeyBoards import inline, reply
from state import UserForm, EducationForm
from DataBase.database import users_db, dicts_db

TOKEN = "7359834273:AAEzraHI224eBQcGkaud25lOfSxGmjYpb9k"    # Укажите свой токен
MAX_LINE_IN_PAGE = 8

disp = Dispatcher()
storage = MemoryStorage()
 
#
# Отслеживание text-ов
#
@disp.message( F.text == "/start" )
async def command_start_handler( message ) -> None:
    STEP_REG = await users_db.get_count_not_empty_in_page( message.chat.id )
    if STEP_REG == 0:
        await users_db.create( message.chat.id )
        await message.answer( "Приветственное сообщение", reply_markup=inline.agree )
    elif STEP_REG < 4:
        await message.answer( "Уже идёт процесс регистрации" )
    else:
        await message.answer( "Вы уже зарегистрированы" )

#
# Отслеживание callback-ов
#
@disp.callback_query()
async def callback_handler( call, state ) -> None:
    STEP_REG = await users_db.get_count_not_empty_in_page( call.message.chat.id )
    if STEP_REG == 1:
        await call.message.edit_text( "Сколько вам лет?" )
        await state.set_state( UserForm.step1 )
    elif STEP_REG == 2:
        if call.data in ['MEN', 'WOMEN']:
            await users_db.enter( call.message.chat.id, "gender", call.data )
            await call.message.edit_text( "Выберите технику обучения. (Позже её можно изменить в настройках)\n\n" \
                             "1) Случаность - при обучении будут предлогаться слова в случайном порядке\n\n" \
                             "2) Забываемость - будут предлогаться слова с наихудшим качеством запоминания\n\n", reply_markup=inline.params )
    elif STEP_REG == 3:
        if call.data in ['random', 'memoriz']:
            await users_db.enter( call.message.chat.id, "param", call.data )
            await call.message.edit_text( "Регистрация окончена!" )
            await call.message.answer( "Все функции находяться в меню над клавиатурой", reply_markup=reply.main )
    else:
        pass

#
# Обработка state-ов
#
@disp.message( UserForm.step1 )
async def user_form_step1( message, state ) -> None:
    STEP_REG = await users_db.get_count_not_empty_in_page( message.chat.id )
    if STEP_REG == 1:
        await users_db.enter( message.chat.id, "age", message.text )
        await message.answer( "Ваш пол:", reply_markup=inline.gender )
        await state.clear()

#
# Запуск
#
async def main() -> None:
    bot = Bot( TOKEN )
    await bot.delete_webhook( drop_pending_updates=True )
    await disp.start_polling( bot, skip_updates=True )

if __name__ == "__main__":
    asyncio.run( main() )