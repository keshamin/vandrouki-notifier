from time import sleep
from datetime import datetime
from telebot import TeleBot, types
from config import TOKEN, VANDROUKI_URL, ADMIN_ID
import schedule
import threading
from vandrouki_parser import VandroukiParser

from database import *
from messages import M
from markups import main_menu, kw_groups_keyboard, inline_kw_group_markup, yes_no_markup, notification_menu
import argparse


# If configs are default they must be specified as cli args
token_required = TOKEN == 'YOUR_BOT_TOKEN'
admin_id_required = ADMIN_ID == 11111111


parser = argparse.ArgumentParser(description='Vandrouki Parsing bot')
parser.add_argument('--api-token', required=token_required, nargs=1)
parser.add_argument('--admin-id', required=admin_id_required, nargs=1)


args = parser.parse_args()

if token_required:
    TOKEN = args.api_token[0]
if admin_id_required:
    ADMIN_ID = int(args.admin_id[0])


bot = TeleBot(TOKEN)


@bot.message_handler(func=lambda message: message.chat.id != ADMIN_ID)
def permission_denied(message):
    bot.send_message(message.chat.id, M.PERMISSION_DENIED)


@bot.message_handler(commands=['start'])
def welcome(message):
    try:
        user = User.create(telegram_id=message.chat.id)
        bot.send_message(message.chat.id, 'Hey new user', reply_markup=main_menu)
        schedule.every().day().at(user.notification_time.strftime('%H:%M')).do(
            send_digest, user.telegram_id).tag(user.telegram_id)
    except IntegrityError:
        bot.send_message(message.chat.id, 'Hi again', reply_markup=main_menu)


@bot.message_handler(func=lambda message: message.text == M.MAIN_MENU_BUTTON)
def my_keyword_groups(message):
    bot.send_message(message.chat.id, M.RETURN_TO_MAIN_MENU, reply_markup=main_menu)


@bot.message_handler(func=lambda message: message.text == M.KEYWORDS_BUTTON or message.text == M.LIST_GROUPS_BUTTON)
def my_keyword_groups(message):
    kw_groups = KeywordGroup.select().where(KeywordGroup.owner_id == message.chat.id)
    if len(kw_groups) == 0:
        bot.send_message(message.chat.id, M.NO_KW_GROUP_YET, reply_markup=kw_groups_keyboard)
    else:
        bot.send_message(message.chat.id, M.KW_GROUPS_LIST, reply_markup=kw_groups_keyboard)
        for group in kw_groups:
            send_group(message.chat.id, group)


def send_group(chat_id, group):
    msg = '*{}*\n'.format(group.group_name)
    msg += M.GROUP_KEYWORDS + '\n'
    for i, keyword in enumerate(group.keywords):
        msg += '{index}) {kw}\n'.format(index=i + 1,
                                        kw=keyword.keyword)
    bot.send_message(chat_id, msg, parse_mode='Markdown',
                     reply_markup=inline_kw_group_markup(group.group_name))


@bot.callback_query_handler(func=lambda cb: cb.data.startswith('add_keywords'))
def add_keywords_step1(cb):
    group_name = cb.data.split()[1]
    bot.send_message(cb.message.chat.id, M.ENTER_KW_TO_ADD(group=group_name),
                     parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler_by_chat_id(cb.message.chat.id, add_keywords_step2,
                                              group_name)


def add_keywords_step2(message, group_name):
    group = KeywordGroup.get(KeywordGroup.owner_id == message.chat.id,
                             KeywordGroup.group_name == group_name)
    existing_keywords = set([kw.keyword for kw in group.keywords])
    entered_keywords = set([elem.strip() for elem in message.text.strip().strip(',').split(',')])

    keywords_to_add = entered_keywords.difference(existing_keywords)
    if len(keywords_to_add) > 0:
        group.add_keywords(*keywords_to_add.difference(existing_keywords))
        bot.send_message(message.chat.id, M.KEYWORDS_ADDED, reply_markup=kw_groups_keyboard)
        send_group(message.chat.id, group)
    else:
        bot.send_message(message.chat.id, M.KEYWORDS_ALREADY_EXIST, reply_markup=kw_groups_keyboard)


@bot.callback_query_handler(func=lambda cb: cb.data.startswith('remove_keywords'))
def remove_keywords_step1(cb):
    group_name = cb.data.split()[1]
    bot.send_message(cb.message.chat.id, M.ENTER_KW_TO_REMOVE(group=group_name),
                     parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler_by_chat_id(cb.message.chat.id, remove_keywords_step2,
                                              group_name)


def remove_keywords_step2(message, group_name):
    group = KeywordGroup.get(KeywordGroup.owner_id == message.chat.id,
                             KeywordGroup.group_name == group_name)
    existing_keywords = set([kw.keyword for kw in group.keywords])
    entered_keywords = set([elem.strip() for elem in message.text.strip().strip(',').split(',')])
    keywords_to_remove = entered_keywords.intersection(existing_keywords)
    if len(keywords_to_remove) > 0:
        group.remove_keywords(*keywords_to_remove)
        bot.send_message(message.chat.id, M.KEYWORDS_REMOVED, reply_markup=kw_groups_keyboard)
        send_group(message.chat.id, group)
    else:
        bot.send_message(message.chat.id, M.NO_SUCH_KEYWORDS, reply_markup=kw_groups_keyboard)


@bot.callback_query_handler(func=lambda cb: cb.data.startswith('remove_group'))
def remove_group_step1(cb):
    group_name = cb.data.split()[1]
    group = KeywordGroup.get_or_none(KeywordGroup.owner_id == cb.message.chat.id,
                                     KeywordGroup.group_name == group_name)
    if group is not None:
        bot.send_message(cb.message.chat.id, M.REMOVE_CONFIRMATION(group_name),
                         reply_markup=yes_no_markup, parse_mode='Markdown')
        bot.register_next_step_handler_by_chat_id(cb.message.chat.id, remove_group_step2, group_name)
    else:
        bot.answer_callback_query(cb.id, M.NO_SUCH_GROUP(group_name))


def remove_group_step2(message, group_name):
    if message.text == M.YES_BUTTON:
        group = KeywordGroup.get_or_none(KeywordGroup.owner_id == message.chat.id,
                                         KeywordGroup.group_name == group_name)
        if group is not None:
            deleted = group.delete_instance()
            if deleted == 1:
                bot.send_message(message.chat.id, M.GROUP_REMOVED(group_name), parse_mode='Markdown',
                                 reply_markup=kw_groups_keyboard)
            else:
                bot.send_message(message.chat.id, M.FAILED_TO_REMOVE_GROUP(group_name), parse_mode='Markdown',
                                 reply_markup=kw_groups_keyboard)
        else:
            bot.send_message(message.chat.id, M.NO_SUCH_GROUP(group_name), parse_mode='Markdown',
                             reply_markup=kw_groups_keyboard)
    else:
        bot.send_message(message.chat.id, M.GROUP_REMOVE_CANCELED(group_name), parse_mode='Markdown',
                         reply_markup=kw_groups_keyboard)


@bot.message_handler(func=lambda message: message.text == M.ADD_KW_GROUP_BUTTON)
def create_keyword_group_step1(message):
    bot.send_message(message.chat.id, M.ENTER_NEW_GROUP_NAME, reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler_by_chat_id(message.chat.id, create_keyword_group_step2)


def create_keyword_group_step2(message):
    group_name = message.text.strip()
    group = KeywordGroup.get_or_none(KeywordGroup.owner_id == message.chat.id,
                                     KeywordGroup.group_name == group_name)
    if group is None:
        KeywordGroup.create(owner_id=message.chat.id, group_name=group_name)
        bot.send_message(message.chat.id, M.ENTER_KW_TO_ADD(group_name), parse_mode='Markdown',
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler_by_chat_id(message.chat.id, add_keywords_step2, group_name)
    else:
        bot.send_message(message.chat.id, M.SAME_NAME_GROUP_ERROR(group_name), parse_mode='Markdown',
                         reply_markup=kw_groups_keyboard)


@bot.message_handler(func=lambda message: message.text == M.NOTIFICATIONS_BUTTON)
def notifications_menu(message):
    current_notification_time = User.get(User.telegram_id == message.chat.id).notification_time.strftime('%H:%M')
    bot.send_message(message.chat.id, M.MY_NOTIFICATION_TIME(current_notification_time), reply_markup=notification_menu)


@bot.message_handler(func=lambda message: message.text == M.CHANGE_NOTIFICATION_TIME_BUTTON)
def change_notification_time_step1(message):
    bot.send_message(message.chat.id, M.ENTER_NEW_NOTICATION_TIME, reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler_by_chat_id(message.chat.id, change_notification_time_step2)


def change_notification_time_step2(message):
    try:
        new_time = datetime.strptime(message.text, '%H:%M').time()
        user = User.get(User.telegram_id == message.chat.id)
        user.notification_time = new_time
        user.save()
        schedule.clear(user.telegram_id)
        schedule.every().day.at(user.notification_time.strftime('%H:%M')).do(
            send_digest, user.telegram_id).tag(user.telegram_id)
        notifications_menu(message)
    except ValueError:
        bot.send_message(message.chat.id, M.INVALID_TIME_FORMAT)


def send_digest(telegram_id):
    message = ''

    user = User.get(User.telegram_id == telegram_id)
    vp = VandroukiParser(VANDROUKI_URL)
    posts = vp.collect_posts_links(num=20, until_id=user.last_post_seen)

    for keyword_group in user.keyword_groups:
        appears = False
        for post_link in posts.values():
            if vp.post_contains_keywords(post_url=post_link,
                                         keywords_list=[kw.keyword for kw in keyword_group.keywords]):
                if not appears:
                    message += '*{}*\n'.format(keyword_group.group_name)
                    appears = True

                message += post_link + '\n'
        message += '\n'

    if len(message.strip()) > 0:
        bot.send_message(telegram_id, message, parse_mode='Markdown')


def run_pending_and_sleep():
    while True:
        schedule.run_pending()
        sleep(1)


for user in User.select():
    schedule.every().day.at(user.notification_time.strftime('%H:%M')).do(
        send_digest, user.telegram_id).tag(user.telegram_id)


thread = threading.Thread(target=run_pending_and_sleep, daemon=True)
thread.start()

bot.polling()
