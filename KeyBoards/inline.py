from aiogram.types import InlineKeyboardMarkup as InMarkup, InlineKeyboardButton as InButton

agree = InMarkup( inline_keyboard=[
    [InButton( text="Я согласен", callback_data="agree" )]
], resize_keyboard=True )

gender = InMarkup( inline_keyboard=[
    [InButton( text="М", callback_data="M" ),
    InButton( text="Ж", callback_data="W" )]
], resize_keyboard=True )

params = InMarkup( inline_keyboard=[
    [InButton( text="Случайность", callback_data="random" )],
    [InButton( text="Забываемость", callback_data="memoriz" )],
    [InButton( text="По времени", callback_data="time" )],
    [InButton( text="Забыв. и врем.", callback_data="ran-time" )]
], resize_keyboard=True )

help_button = InMarkup( inline_keyboard=[
    [InButton( text="Помощь", callback_data="help" )]
], resize_keyboard=True )