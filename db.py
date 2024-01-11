from peewee import *
from playhouse.sqliteq import SqliteQueueDatabase

db = SqliteQueueDatabase('db.db')

class child(Model):
    id = IntegerField()
    fio = TextField()

    class Meta:
        db_table = "children"
        database = db

class parents(Model): 
    id = IntegerField()
    fio = TextField()
    number = TextField()
    child_id = IntegerField()

    class Meta:
        db_table = "parents"
        database = db

class reg(Model):
    tgid = IntegerField()
    par_id = IntegerField()
    child_id = IntegerField()

    class Meta:
        primary_key = False
        db_table = "reg"
        database = db

class schedule(Model):
    child_id = IntegerField()
    day = TextField()
    
    class Meta:
        primary_key = False
        db_table = "eat_schedule"
        database = db
