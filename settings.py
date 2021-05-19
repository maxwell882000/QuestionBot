import shelve
from config import basedir
import os
import logging


filename = os.path.join(basedir, 'settings.data')


def _get_value(key: str):
    logging.info(key)
    settings = shelve.open(filename)
    value = settings[key]
    settings.close()
    return value


def _set_value(key: str, value):
    settings = shelve.open(filename)
    settings[key] = value
    settings.close()


def get_right_answer_points() -> int:
    return _get_value('right_answer_points')


def set_right_answer_points(points):
    _set_value('right_answer_points', points)


def get_bot_state() -> str:
    return _get_value('bot_state')


def set_bot_state(state):
    _set_value('bot_state', state)


class BotStates:
    PAUSED = 'paused'
    WORK = 'work'
    STOPPED = 'stopped'
