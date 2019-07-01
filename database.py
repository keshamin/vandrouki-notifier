from peewee import *
from datetime import time

from config import DB_PATH


# pragmas parameter is necessary for correct behavior of foreign keys in SQLite
db = SqliteDatabase(DB_PATH, pragmas={'foreign_keys': 1})
db.connect()


class User(Model):
    telegram_id = IntegerField(primary_key=True)
    username = CharField()
    notification_time = TimeField(default=time(hour=12))
    last_post_seen = CharField(null=True)

    class Meta:
        database = db

    def add_keyword_group(self, group_name, keywords_list):
        group = KeywordGroup.create(group_name=group_name, owner_id=self.telegram_id)
        group.add_keywords(*keywords_list)

    def remove_keyword_group(self, group_name):
        group = KeywordGroup.get(KeywordGroup.owner_id == self.telegram_id,
                                            KeywordGroup.group_name == group_name)
        group.delete_instance()


class KeywordGroup(Model):
    group_id = AutoField()
    owner_id = ForeignKeyField(User, backref='keyword_groups', on_delete='CASCADE')
    group_name = CharField()

    class Meta:
        database = db
        constraints = [SQL('UNIQUE(owner_id, group_name)')]

    def add_keywords(self, *keywords):
        for keyword in keywords:
            Keyword.create(keyword=keyword, parent_group=self.group_id)

    def remove_keywords(self, *keywords):
        for keyword in keywords:
            kw = Keyword.get(Keyword.keyword == keyword,
                             Keyword.parent_group == self.group_id)
            kw.delete_instance()


class Keyword(Model):
    keyword = CharField()
    parent_group = ForeignKeyField(KeywordGroup, backref='keywords', on_delete='CASCADE')

    class Meta:
        database = db
        primary_key = CompositeKey('parent_group', 'keyword')


class NewUserRequest(Model):
    telegram_id = IntegerField(primary_key=True)
    username = CharField()
    application_time = TimestampField()

    class Meta:
        database = db


db.create_tables([User, KeywordGroup, Keyword, NewUserRequest])
