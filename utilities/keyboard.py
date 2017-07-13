from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def build_main_menu():
    inline_keyboard = [
        [InlineKeyboardButton(text='Tenders',
                              callback_data='tenders'),
         InlineKeyboardButton(text='Register',
                              callback_data='register')],
        [InlineKeyboardButton(text='Exit Menu',
                              callback_data='exit_menu')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def build_tenders_menu(tenders):
    inline_keyboard = []
    for tender in tenders:
        if not tender.number:
            tender.number = 'N/A'
        inline_keyboard.append([
            InlineKeyboardButton(text=tender.title,
                                 callback_data=tender.number)
        ])

    inline_keyboard.append(
        [InlineKeyboardButton(text='Back To Main Menu',
                              callback_data='back_to_main_menu'),
         InlineKeyboardButton(text='Exit Menu',
                              callback_data='exit_menu')]
    )
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def build_tender_actions():
    inline_keyboard = [
        [InlineKeyboardButton(text='Download Document',
                              callback_data='download_document'),
         InlineKeyboardButton(text='Email Document',
                              callback_data='email_document')],
        [InlineKeyboardButton(text='Back To Tenders List',
                              callback_data='tenders_list'),
         InlineKeyboardButton(text='Exit Menu',
                              callback_data='exit_menu')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
