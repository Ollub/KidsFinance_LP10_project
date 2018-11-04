from datetime import datetime

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm, \
                      EditProfileForm, CreateGroup, \
                      EditGroupForm , TaskForm
from app.models import User, Role, Group, Task


@app.route('/')
@app.route('/index')
@login_required
def index():
    print('********************')
    print(current_user)
    print('********************')

    form = TaskForm(user=current_user)
    if form.validate_on_submit:
        task = Task(body=form.task.data, author=current_user, gold=form.price.data)
        db.session.add(task)
        # for group in form.groups.data:
        #     task.groups.append(task)
        db.session.commit()
        flash('Your task was successfully published!')
        return redirect(url_for('index'))
    user = current_user.username
    tasks = Task.query.all()
    return render_template('index.html', title='Home', user=user, tasks=tasks, form=form)

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
    return render_template('login.html', title='Sign In', form=form)


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
        user.set_password(form.password.data)
        user.set_role(form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    tasks = [
             {'author': user, 'body': 'Test post #1'},
             {'author': user, 'body': 'Test post #2'}
         ]
    return render_template('user.html', user=user, tasks=tasks)


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

    tasks = [
            {
                'author': {'username': 'Oleg'},
                'body': 'to wash the dishes'
            },
            {
                'author': {'username': 'Jane'},
                'body': 'to clean the room'
            }
            ]
    return render_template('group.html', title='Group', group=group, members=members, tasks=tasks)


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