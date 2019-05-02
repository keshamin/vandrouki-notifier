from random import choice


class M(object):
    def __getattribute__(self, item):
        attr = super().__getattribute__(item)
        if isinstance(attr, tuple):
            return choice(attr)
        return attr

    # --- Common ---
    YES_BUTTON = 'Да'
    NO_BUTTON = 'Нет'
    PERMISSION_DENIED = 'В данный момент публичный доступ закрыт.\n' \
                        'Для получения доступа обратитесь к автору (@keshamin).'

    # --- Main menu ---
    KEYWORDS_BUTTON = 'Ключевые слова'
    NOTIFICATIONS_BUTTON = 'Настройка времени уведовления'
    MAIN_MENU_BUTTON = 'Главное меню'
    RETURN_TO_MAIN_MENU = 'Главное меню'

    # --- Keyword groups section ---
    LIST_GROUPS_BUTTON = 'Показать список групп'
    ADD_KW_GROUP_BUTTON = 'Добавить группу'
    ADD_KEYWORDS_BUTTON = 'Добавить ключевые слова'
    REMOVE_KEYWORDS_BUTTON = 'Удалить ключевые слова'
    REMOVE_GROUP_BUTTON = 'Удалить группу'

    NO_KW_GROUP_YET = 'Вы еще не создали ни одной группы ключевых слов.'
    KW_GROUPS_LIST = 'Вот список ваших групп ключевых слов:'
    GROUP_KEYWORDS = 'Ключевые слова:'


    @staticmethod
    def ENTER_KW_TO_ADD(group):
        return 'Добавляем ключевые слова в группу *{}*\n' \
               'Отправьте ключевые слова в ответном сообщении через запятую.'.format(group)

    KEYWORDS_ALREADY_EXIST = 'Такие ключевые слова уже есть в этой группе.'
    KEYWORDS_ADDED = 'Ключевые слова добавлены.'
    KEYWORDS_REMOVED = 'Ключевые слова удалены.'
    NO_SUCH_KEYWORDS = 'В этой группе нет таких ключевых слов.'

    @staticmethod
    def ENTER_KW_TO_REMOVE(group):
        return 'Удаляем ключевые слова из группы *{}*.\n' \
               'Отправьте ключевые слова, которые необходимо удалить, в ответном сообщении через запятую.'.format(group)

    @staticmethod
    def REMOVE_CONFIRMATION(group):
        return 'Вы уверены, что хотите удалить группу *{}*?'.format(group)

    @staticmethod
    def NO_SUCH_GROUP(group=None):
        if group:
            return 'Группы ключевых слов *{}* не существует!'
        else:
            return 'Такой группы не существует'

    @staticmethod
    def GROUP_REMOVED(group):
        return 'Группа ключевых слов *{}* удалена.'.format(group)

    @staticmethod
    def FAILED_TO_REMOVE_GROUP(group):
        return 'Не удалось удалить группу ключевых слов *{}*.'.format(group)

    GROUP_REMOVE_CANCELED = 'Удаление группы отменено.'
    ENTER_NEW_GROUP_NAME = 'Введите название новой группы ключевых слов.'

    @staticmethod
    def SAME_NAME_GROUP_ERROR(group_name):
        return 'Группа ключевых слов с именем *{}* уже существует!'.format(group_name)

    # --- Notification section ---
    CHANGE_NOTIFICATION_TIME_BUTTON = 'Изменить время уведомления'

    @staticmethod
    def MY_NOTIFICATION_TIME(time):
        return 'Текущее время ежеджевного уведомления: {}'.format(time)

    ENTER_NEW_NOTICATION_TIME = 'Введите новое время уведомлений в формате ЧЧ:ММ.'
    INVALID_TIME_FORMAT = 'Некорректный формат времени.'
