import asyncio, random
from aiogram import Dispatcher, F, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup as InMarkup, InlineKeyboardButton as InButton

from KeyBoards import inline, reply
from state import UserForm, EducationForm
from DataBase.database import users_db, dicts_db

TOKEN = ""    # Укажите свой токен
MAX_LINE_IN_PAGE = 8

disp = Dispatcher()
storage = MemoryStorage()
 
def dict_create( public_dicts ) -> list:
    if type( public_dicts ) == str:
        public_dicts = render_dict( public_dicts )
    return [{'id': one_dict[0], 'name': one_dict[1], 'content': one_dict[2]} for one_dict in public_dicts]

def render_dict( public_dicts ) -> list:
    return [[int( one_dict.split( '[' )[0] )] + one_dict.split( '[' )[1:] for one_dict in public_dicts.split( '$' ) if one_dict != ""]

def get_word( selected_dict, param, old_words=[] ):
    words = selected_dict.split( '&' )
    if param == 'random':   # Отслеживаем методики обучения
        i = random.choice( list( set( range( len( words ) ) ) - set( old_words ) ) )
        return words[i].split( '|' ), old_words + [i]
    
def update_dict_selected( result, dict_selected, word, time_update=False ):    # Обновляем данные в личном словаре
    if len( word ) == 3:
        old_word =  '|'.join( word )
        new_word = '|'.join( word ) + '|' +  f'{ result }|{ result }'
    else:
        old_word = '|'.join( word )
        if time_update:  # Обновляется параметр последнего обучения слову
            new_word = '|'.join( word[:-2] ) + '|' +  f'{ int( word[-2] ) }|{ int( word[-1] ) + result }'
        else:   # Обновляется параметр запоминания слова
            new_word = '|'.join( word[:-2] ) + '|' +  f'{ int( word[-2] ) + result }|0' # Обнуляется параметр времени 
    dict_selected['content'] = dict_selected['content'].replace( old_word, new_word, 1 )
    return dict_selected

def update_dicts( selected_dict, dicts ):   # Заменяет слово в словаре
    dicts = dicts.split('$')
    result = []
    for one_dict in dicts:
        if selected_dict.split('[')[0] == one_dict.split('[')[0]:
            result += [selected_dict]
        else:
            result += [one_dict]
    return '$'.join(result)

def delete_dict( dict_id, dicts ):  # Удаляет слово в словаре
    dicts = dicts.split('$')
    result = []
    for one_dict in dicts:
        if str( dict_id ) != one_dict.split('[')[0]:
            result += [one_dict]
    return '$'.join(result)

#
# Отслеживание text-ов
#
@disp.message( F.text == "/start" )
async def command_start_handler( message ) -> None:
    STEP_REG = await users_db.get_count_not_empty_in_page( message.chat.id )
    if STEP_REG == 0:
        await users_db.create( message.chat.id )
        await message.answer( "Здравствуйте! Это бот для изучения слов.\n\n" \
                             "Чтобы начать пользоваться его функциями вы должны согласиться " \
                             "с тем, что результаты использования этого бота будут анонимно " \
                             "использоваться в моём исследовательском проекте.", reply_markup=inline.agree )
    elif STEP_REG < 4:
        await message.answer( "Уже идёт процесс регистрации" )
    else:
        await message.answer( "Вы уже зарегистрированы" )
    for i in range(20): # Добавляем тестовые словари для отладки
        await dicts_db.create(i)
        await dicts_db.enter(i, 'name', f'Тест словарь {i}')
        await dicts_db.enter(i, 'content', 'кот|кОт|потому что ...&как|кАк|None&мот|мОт|потому что')

@disp.message( F.text == "Выбрать словарь" )
async def choosing_dict_handler( message ) -> None:
    STEP_REG = await users_db.get_count_not_empty_in_page( message.chat.id )
    if STEP_REG >= 4:
        public_dicts = dict_create( await dicts_db.get_all() )
        inButtons = [[InButton( text=one_dict['name'], callback_data=f"open-dict:{ one_dict['id'] }:0" )] \
                          for one_dict in public_dicts[:8]]
        if len( inButtons ) >= MAX_LINE_IN_PAGE:
            inButtons += [[InButton( text='--->', callback_data=f'view-page:{ MAX_LINE_IN_PAGE }' )]]
        keyboard = InMarkup( inline_keyboard=inButtons, resize_keyboard=True )
        await message.answer( "Вот доступные словари:", reply_markup=keyboard )
    else:
        await message.answer( "Вы не зарегистрированы" )


@disp.message( F.text == "Добавить словарь" )
async def dict_add_handler( message ) -> None:
    await message.answer( "Скоро функция добавления своих словарей будет реализована.\n" \
                         "На данный момент, чтобы добавить новый словарь обратитесь к нам по кнопке ниже.", reply_markup=inline.help_button )
    
@disp.message( F.text == "Настройки" )
async def settings_handler( message ) -> None:
    await message.answer( "Реализация настроек" )

@disp.message( F.text == "Помощь" )
async def help_handler( message ) -> None:
    await message.answer( "Реализация помощи" )

@disp.message( F.text == "Начать обучение" )
async def education_handler( message ) -> None:
    STEP_REG = await users_db.get_count_not_empty_in_page( message.chat.id )
    if STEP_REG >= 4:
        public_dicts = dict_create( await users_db.get( message.chat.id, 'dataTrain' ) )
        inButtons = [[InButton( text=public_dict['name'], callback_data=f"open-my-dict:{ public_dict['id'] }:0" )] \
                          for public_dict in public_dicts[:MAX_LINE_IN_PAGE]]
        if len( inButtons ) >= MAX_LINE_IN_PAGE:
            inButtons += [[InButton( text='--->', callback_data=f'view-my-page:{ MAX_LINE_IN_PAGE }' )]]
        keyboard = InMarkup( inline_keyboard=inButtons, resize_keyboard=True )
        if len( inButtons ) != 0:
            await message.answer( "Вот ваши словари:", reply_markup=keyboard )
        else:
            await message.answer( "У вас нет выбранных словарей" )
    else:
        await message.answer( "Вы не зарегестрированы" )

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
        if call.data in ['M', 'W']:
            await users_db.enter( call.message.chat.id, "gender", call.data )
            await call.message.edit_text( "Выберите принцип обучения (Позже его можно изменить в настройках):\n\n" \
                             "1) Случайность - при обучении будут предлогаться слова в случайном порядке\n\n" \
                             "2) По забываемости - будут предлогаться слова с наихудшим качеством запоминания\n\n" \
                             "3) По времени - будут предлогаться слова, которые были последние в обучении\n\n" \
                             "4) По забываемости и времени - объединение 2 и 3 техники", reply_markup=inline.params )
    elif STEP_REG == 3:
        if call.data in ['random', 'memoriz']:
            await users_db.enter( call.message.chat.id, "param", call.data )
            await call.message.edit_text( "Регистрация окончена!" )
            await call.message.answer( "Все функции находяться в меню над клавиатурой", reply_markup=reply.main )
    else:
        if 'open' in call.data: #open*:dict_id:page
            dict_id, page = map( int, call.data.split( ':' )[1:] )
            if 'open-dict' in call.data:    #open:dict_id:page
                dicts = dict_create( await dicts_db.get_all() )    # Public dicts
                button_name = 'Добавить в личные словари'
                command_names = ['add-dict', 'view-page']
            elif 'open-my-dict' in call.data:   #open-my-dict:dict_id:page
                dicts = dict_create( await users_db.get( call.message.chat.id, 'dataTrain' ) )   # Person dicts
                button_name = 'Начать обучение'
                command_names = ['start-education', 'view-my-page']
            for selected_dict in dicts:
                if selected_dict['id'] == dict_id:  break
            keyboard = InMarkup( inline_keyboard=[
                [InButton( text=button_name, callback_data=f"{ command_names[0] }:{ selected_dict['id'] }:{ page }" )]
            ], resize_keyboard=True )
            if 'open-my-dict' in call.data:
                keyboard.inline_keyboard.append( [InButton( text="Удалить", callback_data=f"delete:{ dict_id }:{ page }" )] )
            keyboard.inline_keyboard.append( [InButton( text="Назад", callback_data=f"{ command_names[1] }:{ page }" )] )
            await call.message.edit_text( f"Вы выбрали словарь: \"{ selected_dict['name'] }\"", reply_markup=keyboard )
        elif 'view' in call.data:   #view*:page
            page = int( call.data.split( ':' )[1] )
            await state.clear()
            if 'view-page' in call.data:
                dicts = dict_create( await dicts_db.get_all() )    # Public dicts
                inButtons = [[InButton( text=public_dict['name'], callback_data=f'open-dict:{ public_dict["id"] }:{ page }' )] \
                          for public_dict in dicts[page:page + MAX_LINE_IN_PAGE]]
                command_name = 'view-page'
                name = 'доступные'
            elif 'view-my-page' in call.data:
                dicts = dict_create( await users_db.get( call.message.chat.id, 'dataTrain' ) )   # Person dicts
                inButtons = [[InButton( text=person_dict['name'], callback_data=f'open-my-dict:{ person_dict["id"] }:{ page }' )] \
                          for person_dict in dicts[page:page + MAX_LINE_IN_PAGE]]
                command_name = 'view-my-page'
                name = 'ваши'
            if page != 0 and len( dicts ) - page - MAX_LINE_IN_PAGE> 0:
                inButtons += [[InButton( text='<---', callback_data=f'{ command_name }:{ page - MAX_LINE_IN_PAGE }' ), \
                                   InButton( text='--->', callback_data=f'{ command_name }:{ page + MAX_LINE_IN_PAGE }' )]]
            elif page != 0 and len( dicts ) - page - MAX_LINE_IN_PAGE <= 0:
                inButtons += [[InButton( text='<---', callback_data=f'{ command_name }:{ page - MAX_LINE_IN_PAGE }' )]]
            elif page == 0 and len( dicts ) - page - MAX_LINE_IN_PAGE > 0:
                inButtons += [[InButton( text='--->', callback_data=f'{ command_name }:{ page + MAX_LINE_IN_PAGE }' )]]
            keyboard = InMarkup( inline_keyboard=inButtons, resize_keyboard=True )
            await call.message.edit_text( f"Вот { name } словари:", reply_markup=keyboard )
        elif 'add-dict' in call.data:    #add-dict:dict_id:page
            dict_id, page = map( int, call.data.split( ':' )[1:] )
            dicts = dict_create( await dicts_db.get_all() )
            for selected_dict in dicts:
                if selected_dict['id'] == dict_id:  break
            dataTrain = await users_db.get( call.message.chat.id, 'dataTrain' )
            dataTrain += "$" + str( selected_dict['id'] ) + '[' + selected_dict['name'] + '[' + selected_dict['content']
            await users_db.enter( call.message.chat.id, 'dataTrain', dataTrain )
            keyboard = InMarkup( inline_keyboard=[[InButton( text="Назад", callback_data=f"view-page:{page}" )]], resize_keyboard=True)
            await call.message.edit_text( "Словарь добавлен!", reply_markup=keyboard )
        elif 'start-education' in call.data:    #start-education:dict_id:page
            dicts = dict_create( await users_db.get( call.message.chat.id, 'dataTrain' ) )
            dict_id, page = map( int, call.data.split( ':' )[1:] )
            for selected_dict in dicts:
                if selected_dict['id'] == dict_id:  break
            keyboard = InMarkup( inline_keyboard=[
                [InButton( text="Назад", callback_data=f"view-my-page:{ page }" )] 
            ], resize_keyboard=True )
            param = await users_db.get( call.message.chat.id, 'param' )
            words, old_words = get_word( selected_dict['content'], param )
            await state.set_state( EducationForm.step1 )
            await state.update_data( education=[words, selected_dict, old_words] )
            await state.update_data( keyboard=keyboard )
            await call.message.edit_text( f"Начнём обучение!\n{ words[0] } - ?", reply_markup=keyboard )
        elif 'ball' in call.data:
            ball = call.data.split( ':' )[1]
            param = await users_db.get( call.message.chat.id, 'param' )
            data = await state.get_data()
            selected_dict =  data['education'][1]
            old_words = data['education'][2]
            if len(old_words) == len(selected_dict['content'].split('&')):
                old_words = []
            keyboard = data['keyboard']
            selected_dict = update_dict_selected( int(ball), selected_dict, data['education'][0] )
            newDataTrain = update_dicts( '['.join(map(str, list(selected_dict.values()))), await users_db.get( call.message.chat.id, 'dataTrain' ) )
            await users_db.enter( call.message.chat.id, 'dataTrain', newDataTrain )
            words, old_words = get_word( selected_dict['content'], param, old_words )
            await state.update_data( education=[words, selected_dict, old_words] )
            await call.message.edit_text( f"Продолжим обучение!\n{ words[0] } - ?", reply_markup=keyboard )
        elif 'delete' in call.data: #delete:dict_id:page
            dicts = await users_db.get( call.message.chat.id, 'dataTrain' )
            dict_id, page = map( int, call.data.split( ':' )[1:] )
            dicts = delete_dict( dict_id, dicts )
            await users_db.enter( call.message.chat.id, 'dataTrain', dicts )
            keyboard = InMarkup( inline_keyboard=[
                [InButton( text="Назад", callback_data=f"view-my-page:{ page }" )] 
            ], resize_keyboard=True )
            await call.message.edit_text( "Словарь удалён", reply_markup=keyboard )
        elif 'help' in call.data:
            await call.message.edit_text( "Реализация помощи" )

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

@disp.message( EducationForm.step1 )
async def education_form_step1( message, state ) -> None:
    data = await state.get_data()
    if message.text != data['education'][0][1]:
        keyboard = InMarkup(inline_keyboard=[
            [InButton( text="1", callback_data=f"ball:-5" ),
            InButton( text="2", callback_data=f"ball:-4" ),
            InButton( text="3", callback_data=f"ball:-3" ),
            InButton( text="4", callback_data=f"ball:-2" ),
            InButton( text="5", callback_data=f"ball:-1" )]
        ], resize_keyboard=True)
        await message.answer(f"Не правильно, нужно { data['education'][0][1] }, { 'потомучто ' + data['education'][0][2] if data['education'][0][2] != 'None' else '' }\nКак вы оцените, насколько хорошо помните это слово? (0 - вы совсем не помните слово, 5 - вы отлично его помните, а ошиблись случайно)", reply_markup=keyboard)
    else:
        keyboard = InMarkup(inline_keyboard=[
            [InButton( text="1", callback_data=f"ball:1" ),
            InButton( text="2", callback_data=f"ball:2" ),
            InButton( text="3", callback_data=f"ball:3" ),
            InButton( text="4", callback_data=f"ball:4" ),
            InButton( text="5", callback_data=f"ball:5" )]
        ], resize_keyboard=True)
        await message.answer(f"Вы правы!\nКак вы оцените, насколько хорошо помните это слово?\n0 - вы совсем не помните слово\n5 - вы отлично его помните, а ошиблись случайно", reply_markup=keyboard)

#
# Запуск
#
async def main() -> None:
    bot = Bot( TOKEN )
    await bot.delete_webhook( drop_pending_updates=True )
    await disp.start_polling( bot, skip_updates=True )

if __name__ == "__main__":
    asyncio.run( main() )