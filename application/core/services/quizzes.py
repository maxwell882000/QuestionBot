from application import db
from application.core.models import Quiz
from datetime import datetime


def create_quiz(start_date: str, end_date: str, top_count: int, channel_id: int):
    quiz = Quiz()
    quiz.start_date = datetime.strptime(start_date, '%d.%m.%Y')
    quiz.end_date = datetime.strptime(end_date, '%d.%m.%Y')
    quiz.top_count = top_count
    quiz.channel_id = channel_id
    db.session.add(quiz)
    db.session.commit()
    return quiz


def get_by_id(quiz_id):
    return Quiz.query.get_or_404(quiz_id)
