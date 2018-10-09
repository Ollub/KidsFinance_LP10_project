import csv
import datetime

from kf_bd import db_session, User, Role, Task, Condition

#преобразование в datetime даты из excel
def to_datetime(date):
    dt_date = datetime.datetime.strptime(date, '%d.%m.%Y')
    return dt_date


# with open('user_list.csv', 'r', encoding='utf-8') as f:
#     fields = ['first_name', 'last_name', 'email', 'password', 'status', 'birthday', 'about']
#     reader = csv.DictReader(f, fields, delimiter=';', quotechar='"')
#     for row in reader:
#         row['birthday'] = datetime.datetime.strptime(row['birthday'], '%d.%m.%Y')
#         role = Role.query.filter(Role.status == row['status']).first()
#         row['role'] = role.id
#         user = User(row['first_name'], row['last_name'], row['email'], row['password'], row['role'], row['birthday'], row['about'])
#         db_session.add(user)

with open('task_list.csv', 'r', encoding='windows-1251') as f:
    #fields = ['first_name', 'last_name', 'email', 'password', 'status', 'birthday', 'about']
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        if row['creation_date']:
            row['creation_date'] = to_datetime(row['creation_date'])
        if row['assign_date']: 
            row['assign_date'] = to_datetime(row['assign_date'])
        if row['finish_date']:     
            row['finish_date'] = to_datetime(row['finish_date'])
        creator = User.query.filter(User.first_name == row['first_name'] and 
                                User.last_name == row['last_name'] ).first()
        row['creator'] = creator.id
        holder = User.query.filter(User.first_name == row['holder_first'] and 
                                User.last_name == row['holder_last'] ).first()
        if holder:
            row['holder'] = holder.id
        else: row['holder'] = None
        status = Condition.query.filter(Condition.status == row['condition']).first()
        if status:
            row['status'] = status.id
        else: row['status'] = None

        print(row['creator'], row['holder'], row['status'])
        
        task = Task(row['creator'], row['name'], row['description'], row['price'],
                    row['status'], row['holder'])
        db_session.add(task)

db_session.commit()
