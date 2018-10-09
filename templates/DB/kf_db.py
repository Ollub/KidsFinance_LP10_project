from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Table, Boolean
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

#creating data base
engine = create_engine('sqlite:///kfbase.sqlite')
#creating connection session with database
db_session = scoped_session(sessionmaker(bind=engine))
# создаем класс, описываем модель работы с базой
# declarative_base означает, что мы будем описывать таблицу как питон-код
# и работать с ней как с питон-кодом
Base = declarative_base()
# привязываем возможность делать запросы к БД
Base.query = db_session.query_property()

# association table users to tasks
users_to_tasks = Table('handlers', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('task_id', Integer, ForeignKey('tasks.id'))
)
# создаем таблицу БД, которая наследуется от класса Base
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(120), unique=True)
    password = Column(String(50))
    role_id = Column(Integer, ForeignKey('roles.id')) 
    birthday = Column(DateTime)
    info = Column(Text)
    male = Column(Boolean)
    #image = Column(Binary)
    own_task = relationship('Task', backref='author')
    account = relationship('Account', backref='owner')
    task = relationship("Task",
                    secondary=users_to_tasks, backref="handler")

    #создаем конструктор класса
    def __init__(self, first_name=None, last_name=None, email=None, password=None, role_id=None,
                    birthday=None, info=None, male=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.role_id = role_id
        self.birthday = birthday
        self.info = info
        self.male = male

    def __repr__(self):
        return '<User {} {}>'.format(self.first_name, self.last_name)

# таблица с заданиями
class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String(50))
    description = Column(Text(500))
    price = Column(Integer)
    condition = Column(Integer, ForeignKey('conditions.id'))


    def __init__(self, creator_id=None, name=None, description=None, price=None, condition=None):
        self.creator_id = creator_id
        self.name = name
        self.description = description
        self.price = price
        self.condition = condition
       
    def __repr__(self):
        return '<Task {}>'.format(self.name) 

class Condition(Base):
    __tablename__ = 'conditions'
    id = Column(Integer, primary_key=True)
    status = Column(String(50))
    description = Column(Text(500))
    tasks = relationship("Task", backref='status')

    def __init__(self, status=None, description=None):
        self.status = status
        self.description = description

    def __repr__(self):
        return '<Status: {}>'.format(self.status) 

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    status = Column(String(50))
    description = Column(Text(500))
    user = relationship('User', backref='role')

    def __init__(self, status=None, description=None):
        self.status = status
        self.description = description

    def __repr__(self):
        return '<Role: {}>'.format(self.status)

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    gold = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))

    def __init__(self, gold=None, user_id=None):
        self.gold = gold
        self.user_id = user_id

    def __repr__(self):
        return '<Gold: {} >'.format(self.gold)


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)