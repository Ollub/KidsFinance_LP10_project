from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, make_response
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm, \
                      EditProfileForm, CreateGroup, \
                      EditGroupForm , TaskForm, EditTaskForm
from app.models import User, Role, Group, Task, TaskTrack, \
                       users_to_groups, tasks_to_groups, Account


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():    
    user = current_user.username
    tasks = Task.query.order_by(Task.timestamp.desc()).all()


    return render_template('index.html', title='Home', user=user, tasks=tasks)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('form_login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.accounts = Account(balance = 10000)
        user.set_password(form.password.data)
        user.set_role(form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('form_register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    user_groups = [group.id for group in user.groups]
    #user_groups = db.session.query(Group.id).join(users_to_groups, (users_to_groups.c.member_id == user.id)).all()
    todo = Task.query.join(TaskTrack).filter(TaskTrack.done != None).filter(TaskTrack.approved == None).count()
    if user_groups:
        new_tasks = Task.query.join(tasks_to_groups).join(TaskTrack). \
                filter(tasks_to_groups.c.group_id.in_(user_groups)). \
                filter(TaskTrack.accepted==None).all()
        assigned_tasks = Task.query.join(tasks_to_groups).join(TaskTrack). \
                filter(tasks_to_groups.c.group_id.in_(user_groups)). \
                filter(TaskTrack.accepted != None).filter(TaskTrack.approved==None).all()

    else:
        new_tasks, assigned_tasks = [], []
    for task in assigned_tasks:
        print("*************assigned", task)
    return render_template('user.html', user=user, new_tasks=new_tasks, \
                         assigned_tasks=assigned_tasks, todo=todo)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data

        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/user_groups/<username>')
@login_required
def user_groups(username):
    user = User.query.filter_by(username=username).first_or_404()
    groups = user.groups
    return render_template('user_groups.html', title='User', user=user, groups=groups)


@app.route('/group/<groupname>')
@login_required
def group(groupname):
    group = Group.query.filter_by(groupname=groupname).first_or_404()
    members = group.members
    new_tasks = Task.query.join(tasks_to_groups).join(TaskTrack). \
                filter(tasks_to_groups.c.group_id == group.id). \
                filter(TaskTrack.accepted==None).all()
    assigned_tasks = Task.query.join(tasks_to_groups).join(TaskTrack). \
                filter(tasks_to_groups.c.group_id == group.id). \
                filter(TaskTrack.accepted != None).filter(TaskTrack.approved==None).all()


    return render_template('group.html', title='Group', group=group, members=members, \
                        new_tasks=new_tasks, assigned_tasks=assigned_tasks)


@app.route('/expand_group/<groupname>/')
@login_required
def expand_group(groupname):
    group = Group.query.filter_by(groupname=groupname).first()
    members = group.members
    all_users = User.query.all()
    for member in members:
        all_users.remove(member)

    return render_template('expand_group.html', title='Expand_group', group=group, all_users=all_users, members=members)


@app.route('/add_member/<username>/<groupname>')
@login_required
def add_member(username, groupname):
    user = User.query.filter_by(username=username).first()
    group = Group.query.filter_by(groupname=groupname).first()
    group.members.append(user)
    db.session.commit()
    return redirect(url_for('expand_group', groupname=groupname))
    

@app.route('/remove_member/<username>/<groupname>')
@login_required
def remove_member(username, groupname):
    user = User.query.filter_by(username=username).first()
    group = Group.query.filter_by(groupname=groupname).first()
    group.members.remove(user)
    db.session.commit()
    return redirect(url_for('expand_group', groupname=groupname))
    

@app.route('/group_search')
@login_required
def group_search():
    all_groups = Group.query.all() 
    
    for group in current_user.groups:
        all_groups.remove(group)
    return render_template('group_search.html', title='Group search', all_groups=all_groups)


@app.route('/join_group/<groupname>')
@login_required
def join_group(groupname):
    group = Group.query.filter_by(groupname=groupname).first()
    if current_user in group.members:
        flash('You are already in the group!')
    else:
        group.members.append(current_user)
        db.session.commit()
        flash('Successfully joined')
    return redirect(url_for('group', groupname=groupname))


@app.route('/leave_group/<groupname>')
@login_required
def leave_group(groupname):
    group = Group.query.filter_by(groupname=groupname).first()
    if current_user not in group.members:
        flash('You are not a members of the group')
    else:
        group.members.remove(current_user)
        db.session.commit()
        flash('Successfully leaved. Please go back if you change your mind :)')
    return redirect(url_for('group', groupname=groupname))


@app.route('/new_group', methods=['GET', 'POST'])
@login_required
def new_group():
    form = CreateGroup()
    if form.validate_on_submit():
        current_user.new_group(
                            groupname=form.groupname.data,
                            description=form.description.data
                            )
        db.session.commit()
        flash('Your group have been created!')
        return redirect(url_for('group', groupname=form.groupname.data))
    return render_template('new_group.html', title='New group',
                           form=form)


@app.route('/edit_group/<groupname>', methods=['GET', 'POST'])
@login_required
def edit_group(groupname):
    form = EditGroupForm(groupname)
    group = Group.query.filter_by(groupname=groupname).first()
    if form.validate_on_submit():
        
        group.groupname = form.groupname.data
        group.description = form.description.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('group', groupname=group.groupname))
    elif request.method == 'GET':
        form.groupname.data = group.groupname
        form.description.data = group.description
    return render_template('edit_group.html', title='Edit Group',
                           form=form, group=group)

@app.route('/delete_group/<groupname>')
@login_required
def delete_group(groupname):
    group = Group.query.filter_by(groupname=groupname).first()
    db.session.delete(group)
    db.session.commit()
    flash('Group {} was deleted. So sad :('.format(groupname))
    return redirect(url_for('user', username=current_user.username))


@app.route('/new_task', methods=['GET', 'POST'])
@login_required
def new_task():
    form = TaskForm()
    # list of groups to add
    form.groups.choices = [(group.groupname, group.groupname) for group in current_user.groups]
    
    if form.validate_on_submit():
        if int(form.price.data) > current_user.accounts.balance:
            flash('Not enough gold to create task!')
        else:
            task = Task(taskname=form.task.data, body=form.body.data, author=current_user, gold=int(form.price.data))
            current_user.accounts.balance -= int(form.price.data)
            db.session.add(task)
            print('********groups', form.groups.data)
            for group in form.groups.data:
                group = Group.query.filter_by(groupname=group).first()
                task.groups.append(group)
            track = TaskTrack(task_id=task.id)
            db.session.add(track)
            db.session.commit()
            flash('Your task was successfully published in {} groups!'.format(form.groups.data))
            next_url = request.cookies.get('next_url')
            return redirect(next_url)
    # url for previous page
    resp = make_response(render_template('new_task.html', title='New Task', form=form))
    if request.method == 'GET':
        next_url = request.referrer or '/'
        resp.set_cookie('next_url', next_url)
    return resp


@app.route('/task_info/<task_id>')
@login_required
def task_info(task_id):
    task = Task.query.filter_by(id=task_id).first()
    return render_template('task_info.html', title='Task Info', task=task)

@app.route('/edit_task/<task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    form = EditTaskForm()
    task = Task.query.filter_by(id=task_id).first()
    form.groups.choices = [(group.groupname, group.groupname) for group in current_user.groups]
    if form.validate_on_submit():
        if int(form.price.data) - task.gold > current_user.accounts.balance:
            flash('Not enough gold to create task!')
        else:
            current_user.accounts.balance = current_user.accounts.balance + \
                                            task.gold - int(form.price.data) 
            task.taskname = form.taskname.data
            task.body = form.body.data
            task.gold = form.price.data
            task.groups.clear()
            for group in form.groups.data:
                group = Group.query.filter_by(groupname=group).first()
                task.groups.append(group)
            db.session.commit()
            flash('Your changes have been saved.')
            next_url = request.cookies.get('next_url')
            return redirect(next_url)
    # url for previous page
    resp = make_response(render_template('edit_task.html', title='Task Info', form=form))
    if request.method == 'GET':
        form.taskname.data = task.taskname
        form.body.data = task.body
        form.price.data = task.gold
        next_url = request.referrer or '/'
        resp.set_cookie('next_url', next_url)
    return render_template('edit_task.html', title='Task Info', form=form)



@app.route('/delete_task/<task_id>')
@login_required
def delete_task(task_id):
    next_url = request.referrer or '/'
    task = Task.query.filter_by(id=task_id).first()
    if task.tracking:
        db.session.delete(task.tracking)
    task.author.accounts.balance += task.gold
    db.session.delete(task)
    db.session.commit()
    flash('Task was deleted')
    return redirect('/')


@app.route('/leave_task/<task_id>')
@login_required
def leave_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    task.holders.remove(current_user)
    task.tracking.accepted = None
    db.session.commit()
    flash('You are leved task "{}"'.format(task.taskname))
    return redirect(url_for('task_info', task_id=task_id))


@app.route('/accept_task/<task_id>')
@login_required
def accept_task(task_id):
    next_url = request.referrer or '/'
    task = Task.query.filter_by(id=task_id).first()
    taskname = task.taskname
    if not task.team or len(task.holders) < task.team:
        task.holders.append(current_user)
        task.tracking.accepted = datetime.utcnow()
        db.session.commit()
        flash('Your assigned to the task {}'.format(task.taskname))
    else:
        flash('Number of participants exceeded. Choose another tasks')
    return redirect(next_url)


@app.route('/finish_task/<task_id>')
@login_required
def finish_task(task_id):
    next_url = request.referrer or '/'
    task = Task.query.filter_by(id=task_id).first()
    task.tracking.done = datetime.utcnow()
    db.session.commit()
    flash('Great job! You finished task {}. Wait for {}\'s confiramation'.format(task.taskname, task.author.username))
    return redirect(next_url)

@app.route('/approve_task/<task_id>')
@login_required
def approve_task(task_id):
    next_url = request.referrer or '/'
    task = Task.query.filter_by(id=task_id).first()
    if current_user != task.author:
        flash('Only author can approve tasks. Please ask {} to approve'.format(task.author))
    task.tracking.approved = datetime.utcnow()
    for user in task.holders:
        if not user.accounts:
            account = Account(user_id=current_user.id)
        user.accounts.balance = user.accounts.balance + int(task.gold/len(task.holders))
    db.session.commit()
    flash('Task closed. {} earned {} gold'.format(task.holders[0], task.gold))
    return redirect(next_url)


@app.route('/todo_page')
@login_required
def todo_page():
    tasks = Task.query.join(TaskTrack).filter(TaskTrack.done != None).filter(TaskTrack.approved == None).all()
    return render_template('todo.html', tasks=tasks)



