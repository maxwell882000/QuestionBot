from . import bp
from flask import render_template, redirect, url_for, flash
from flask_login import login_required
from .forms import SettingsForm
import settings as app_settings
from application.core import schedule


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        right_answer_points = form.right_answer_point.data
        app_settings.set_right_answer_points(right_answer_points)
        flash('Настройки викторин изменены!', category='success')
        return redirect(url_for('admin.settings'))
    form.fill_from_settings()
    bot_state = app_settings.get_bot_state()
    return render_template('admin/settings.html', form=form, bot_state=bot_state)


@bp.route('/settings/bot/start', methods=['GET'])
@login_required
def start_bot():
    current_bot_state = app_settings.get_bot_state()
    if current_bot_state == app_settings.BotStates.PAUSED:
        schedule.resume_scheduler()
    else:
        schedule.start_scheduler()
    app_settings.set_bot_state(app_settings.BotStates.WORK)
    return redirect(url_for('admin.settings'))


@bp.route('/settings/bot/pause', methods=['GET'])
@login_required
def pause_bot():
    schedule.pause_scheduler()
    app_settings.set_bot_state(app_settings.BotStates.PAUSED)
    return redirect(url_for('admin.settings'))


@bp.route('/settings/bot/stop', methods=['GET'])
@login_required
def stop_bot():
    schedule.stop_all_jobs()
    app_settings.set_bot_state(app_settings.BotStates.STOPPED)
    return redirect(url_for('admin.settings'))
