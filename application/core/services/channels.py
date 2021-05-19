from application import db
from application.core.models import Channel


def create_channel(channel_name, channel_title, chat_id):
    channel = Channel(channel_name=channel_name, channel_title=channel_title, chat_id=chat_id)
    db.session.add(channel)
    db.session.commit()
    return channel


def remove_channel(channel_id):
    channel = Channel.query.get_or_404(channel_id)
    db.session.delete(channel)
    db.session.commit()


def channel_exists(channel_name):
    return Channel.query.filter(Channel.channel_name == channel_name[1:]).count() > 0


def get_by_id(channel_id) -> Channel:
    return Channel.query.get_or_404(channel_id)
