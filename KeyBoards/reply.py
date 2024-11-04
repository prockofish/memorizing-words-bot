from aiogram.types import ReplyKeyboardMarkup as ReMarkup, KeyboardButton as ReButton

main = ReMarkup( keyboard=[
    [ReButton( text="Начать обучение" )],
    [ReButton( text="Выбрать словарь" )],
    [ReButton( text="Добавить словарь" )],
    [ReButton( text="Настройки" )],
    [ReButton( text="Помощь" )]
], resize_keyboard=True )