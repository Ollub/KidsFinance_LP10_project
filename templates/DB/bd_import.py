import csv
import datetime

from kf_db import db_session, User, Task, Role, Condition, Account

#преобразование в datetime даты из excel
def to_datetime(date):
    dt_date = datetime.datetime.strptime(date, '%d.%m.%Y')
    return dt_date

def users_fill():
    with open('./tables/users.csv', 'r', encoding='utf-8') as f:
        #fields = ['first_name', 'last_name', 'email', 'password', 'status', 'birthday', 'about']
        reader = csv.DictReader(f, delimiter=';', quotechar='"')
        for row in reader:
            row['birthday'] = to_datetime(row['birthday'])
            row['role_id'] = int(row['role_id'])
            
            user = User(row['first_name'], row['last_name'], row['email'], 
                    row['password'], row['role_id'], row['birthday'], row['info'])
            db_session.add(user)
        return 'Sucsessfully'

def roles_fill():
    with open('./tables/roles.csv', 'r', encoding='utf-8') as f:
        #fields = ['first_name', 'last_name', 'email', 'password', 'status', 'birthday', 'about']
        reader = csv.DictReader(f, delimiter=';', quotechar='"')
        for row in reader:
            role = Role(row['status'], row['description'])
            db_session.add(role)
        return 'Sucsessfully'

def tasks_fill():
    with open('./tables/task_list.csv', 'r', encoding='windows-1251') as f:
        #fields = ['first_name', 'last_name', 'email', 'password', 'status', 'birthday', 'about']
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            row['creator_id'] = int(row['creator_id'])
            row['condition'] = int(row['condition'])
            task = Task(row['creator_id'], row['name'], row['description'], row['price'], row['condition'])
            db_session.add(task)
        return 'Sucsessfully'

def conditions_fill():
    with open('./tables/conditions.csv', 'r', encoding='windows-1251') as f:
        #fields = ['first_name', 'last_name', 'email', 'password', 'status', 'birthday', 'about']
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            condition = Condition(row['status'], row['description'])
            db_session.add(condition)
        return 'Sucsessfully'

def account_fill():
    with open('./tables/accounts.csv', 'r', encoding='windows-1251') as f:
        #fields = ['first_name', 'last_name', 'email', 'password', 'status', 'birthday', 'about']
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            row['gold'] = int(row['gold'])
            row['user_id'] = int(row['user_id'])
            account = Account(row['gold'], row['user_id'])
            db_session.add(account)
        return 'Sucsessfully'


if __name__ == '__main__':
    #roles_fill()
    #conditions_fill()
    account_fill()
    #users_fill()
    #tasks_fill()
    db_session.commit()
