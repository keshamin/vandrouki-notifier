import logging
from functools import wraps
from telebot.types import Message, CallbackQuery


def handler_log(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        log_string = ''
        if len(args) > 0:
            if isinstance(args[0], Message):
                log_string = f'Chat ID: {args[0].chat.id}, Handler: {func.__name__}, Text: {args[0].text}'
            if isinstance(args[0], CallbackQuery):
                log_string = f'Chat ID: {args[0].message.chat.id}, Handler: {func.__name__}, Data: {args[0].data}'
        if len(args) > 1:
            log_string += f', Additional args: {args[1:]}'

        logger.info(log_string)
        return func(*args, **kwargs)

    return wrapper


logger = logging.getLogger('Bot')
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(
    logging.Formatter('%(filename)-10s[LINE:%(lineno)04d]# %(levelname)-8s [%(asctime)s]  %(message)s')
)
logger.addHandler(stream_handler)
