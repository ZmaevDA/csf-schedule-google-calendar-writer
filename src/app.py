import os
import re

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

import schedule
from app_config import app, db, login_manager
from forms import AdminForm, LoginForm, SubmitScheduleForm
from model import *

CURRENT_USER_ID = 0


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login_field.data).first()
        if user:
            if check_password_hash(user.password, form.pass_field.data):
                login_user(user)
                return redirect(url_for('admin'))
            else:
                flash("Не верный пароль")
        else:
            flash("Не верный логин")
    return render_template('login.html', form=form)


@app.route('/admin', methods=('GET', 'POST'))
@login_required
def admin():
    curr_id = current_user.user_id
    if curr_id == 1:
        form = AdminForm()
        if form.validate_on_submit():
            file = form.file.data
            if re.match("^\S*.xls$", file.filename):
                file.filename = "schedule.xls"
                file.save(
                    os.path.join(
                        os.path.abspath(
                            os.path.dirname(__file__)
                        ), app.config['UPLOAD_FOLDER'], secure_filename(file.filename)
                    )
                )
                flash("Файл был успешно загружен!")
            else:
                flash("Ошибка при загрузке!")
        return render_template('admin.html', form=form)
    else:
        flash("Не верный логин или пароль для администратора")
        return redirect(url_for('login'))


@app.route('/write-schedule', methods=('GET', 'POST'))
def write_schedule():
    form = SubmitScheduleForm()
    if request.method == 'POST' and form.validate_on_submit():
        course_number = int(form.course_number.data)
        group_number = int(form.group_number.data)
        subgroup_number = int(form.subgroup_number.data)
        week_amount = int(form.week_amount.data)
        schedule.process(course_number, group_number, subgroup_number, week_amount)
        os.remove('resources/token.json')
    return render_template('write-schedule.html', form=form)


@app.route('/temp')
def check():
    return render_template('base.html')
