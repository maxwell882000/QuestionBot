from . import bp
from flask import render_template, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from .forms import LoginForm
from application.core.models import AdminUser
from werkzeug.urls import url_parse


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = AdminUser.get_by_email(form.email.data)
        login_user(user, remember=False)
        next_url = request.args.get('next')
        if not next_url or url_parse(next_url).netloc != '':
            return redirect(url_for('admin.index'))
        return redirect(next_url)
    return render_template('auth/login.html', title="Log in", form=form)
