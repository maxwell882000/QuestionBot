from . import bp
from application.core.models import Channel
from application.core.services import channels
from .forms import NewChannelForm
from flask import flash, redirect, request, render_template, url_for
from flask_login import login_required


@bp.context_processor
def admin_view_context_processor():
    return {
        'channels': Channel.query.all()
    }


@bp.route('/channel/create', methods=['GET', 'POST'])
@login_required
def create_channel():
    form = NewChannelForm()
    if form.validate_on_submit():
        chat_id = form.get_channel_chat_id()
        channel = form.get_channel()
        new_channel = channels.create_channel(channel.username, channel.title, chat_id)
        flash('Канал добавлен', category='success')
        return redirect(url_for('admin.channel_quizzes', channel_id=new_channel.id))
    return render_template('admin/add-channel.html', form=form)


@bp.route('/channel/<int:channel_id>/remove')
@login_required
def remove_channel(channel_id: int):
    channels.remove_channel(channel_id)
    flash('Канал удалён', category='success')
    next_url = request.args.get('next', '/')
    return redirect(next_url)
