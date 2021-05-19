from flask import Blueprint


bp = Blueprint('admin', __name__)

from . import index, channels, quizzes, tests, users, settings
