from . import bp
from application.core.services import channels
from application.core.models import BotUser, Answer
from flask import render_template, abort
from flask_login import login_required


@bp.route('/channels/<int:channel_id>/users')
@login_required
def channel_users(channel_id):
    channel = channels.get_by_id(channel_id)
    members = channel.members.all()
    return render_template('admin/users-list.html', channel=channel, members=members)


@bp.route('/channels/<int:channel_id>/users/<int:user_id>')
@login_required
def show_user(channel_id, user_id):
    channel = channels.get_by_id(channel_id)
    member = channel.members.filter(BotUser.id == user_id).first()
    if not member:
        abort(404)
    quiz = channel.get_current_quiz()
    if quiz:
        answers_count = member.answers.filter(Answer.quiz_id == quiz.id).count()
        answers_right_count = member.answers.filter(Answer.quiz_id == quiz.id, Answer.is_right == True).count()
        answers_points = member.answers.filter(Answer.quiz_id == quiz.id, Answer.points != 0).all()
        answers_points_sum = sum((a.points for a in answers_points))
    else:
        answers_count = 0
        answers_right_count = 0
        answers_points_sum = 0
    return render_template('admin/show-user.html', member=member,
                           channel=channel,
                           answers_count=answers_count,
                           answers_right_count=answers_right_count,
                           answers_points_sum=answers_points_sum)
