from . import bp
from .forms import NewQuizForm
from application.core.services import quizzes, channels
from flask import render_template, url_for, redirect, flash, abort
from flask_login import login_required
from application.core.models import Channel, Quiz, Answer, BotUser


@bp.route('/channels/<int:channel_id>/quizzes', methods=['GET'])
@login_required
def channel_quizzes(channel_id):
    chann_quizzes = Channel.get_quizzes_by_channel_id(channel_id)
    channel = channels.get_by_id(channel_id)
    if channel_quizzes is None:
        abort(404)
    return render_template('admin/quizzes.html', quizzes=chann_quizzes, channel=channel)


@bp.route('/channels/<int:channel_id>/quizzes/create', methods=['GET', 'POST'])
@login_required
def create_quiz(channel_id: int):
    form = NewQuizForm()
    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        top_count = int(form.top_count.data)
        quizzes.create_quiz(start_date, end_date, top_count, channel_id)
        flash('Викторина {} - {} создана!'.format(start_date, end_date), category='success')
        return redirect(url_for('admin.channel_quizzes', channel_id=channel_id))
    channel = channels.get_by_id(channel_id)
    return render_template('admin/new-quiz.html', form=form, channel=channel)


@bp.route('/channels/<int:channel_id>/<int:quiz_id>/remove', methods=['GET'])
@login_required
def remove_quiz(quiz_id: int, channel_id: int):
    # TODO: Delete all scheduled jobs and files with tests in this quiz
    Quiz.remove(quiz_id)
    return redirect(url_for('admin.channel_quizzes', channel_id=channel_id))


@bp.route('/channels/<int:channel_id>/<int:quiz_id>/ratings', methods=['GET'])
@login_required
def quiz_ratings(channel_id: int, quiz_id: int):
    quiz = quizzes.get_by_id(quiz_id)
    users_ids__points = Answer.get_summary_user_points_by_channel_and_period(quiz_id, quiz.top_count)
    users_points = []
    for user_id__points in users_ids__points:
        user_id = user_id__points[0]
        points = user_id__points[1]
        user = BotUser.get_by_id(user_id)
        users_points.append((user, points))
    return render_template('admin/ratings.html', users_points=users_points, quiz=quiz)
