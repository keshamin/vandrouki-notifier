from telebot import types
from messages import M


main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
main_menu.add(*[types.KeyboardButton(text) for text in (M.KEYWORDS_BUTTON, M.NOTIFICATIONS_BUTTON)])

kw_groups_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
kw_groups_keyboard.add(*[types.KeyboardButton(text) for text in (M.LIST_GROUPS_BUTTON,
                                                                 M.ADD_KW_GROUP_BUTTON, M.MAIN_MENU_BUTTON)])

yes_no_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
yes_no_markup.add(*[types.KeyboardButton(text) for text in (M.YES_BUTTON, M.NO_BUTTON)])

notification_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
notification_menu.add(*[types.KeyboardButton(text) for text in (M.CHANGE_NOTIFICATION_TIME_BUTTON,
                                                                M.MAIN_MENU_BUTTON)])


def inline_kw_group_markup(group_name):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(*[types.InlineKeyboardButton(text=text, callback_data=data) for text, data in
                 ((M.ADD_KEYWORDS_BUTTON, 'add_keywords {}'.format(group_name)),
                  (M.REMOVE_KEYWORDS_BUTTON, 'remove_keywords {}'.format(group_name)),
                  (M.REMOVE_GROUP_BUTTON, 'remove_group {}'.format(group_name)))])
    return markup

