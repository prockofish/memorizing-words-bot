from aiogram.types import InlineKeyboardMarkup as InMarkup, InlineKeyboardButton as InButton

agree = InMarkup( inline_keyboard=[
    [InButton( text="Я согласен", callback_data="agree" )]
], resize_keyboard=True )

gender = InMarkup( inline_keyboard=[
    [InButton( text="М", callback_data="MEN" ),
    InButton( text="Ж", callback_data="WOMEN" )]
], resize_keyboard=True )

params = InMarkup( inline_keyboard=[
    [InButton( text="Случайность", callback_data="random" )],
    [InButton( text="По забытым", callback_data="memoriz" )]
], resize_keyboard=True )