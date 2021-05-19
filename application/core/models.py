from application import db, loginManager
from datetime import datetime
import settings
from application.utils import date as dateutils
from werkzeug.utils import secure_filename
from application.utils import files
from config import Config
import os
from sqlalchemy import and_
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

members = db.Table('channel_members',
                   db.Column('bot_user_id', db.Integer, db.ForeignKey('bot_user.id'), primary_key=True),
                   db.Column('channel_id', db.Integer, db.ForeignKey('channel.id'), primary_key=True))


class AdminUser(db.Model, UserMixin):
    __tablename__ = 'admin_users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), index=True)
    password_hash = db.Column(db.String(120))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_email(email):
        return AdminUser.query.filter(AdminUser.email == email).first()


@loginManager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))


class BotUser(db.Model):
    __tablename__ = 'bot_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    answers = db.relationship('Answer', lazy='dynamic', backref=db.backref('user', lazy=True))

    @staticmethod
    def add_user(user_id, first_name, last_name, username):
        current_user = BotUser.query.get(user_id)
        if current_user:
            return current_user
        new_user = BotUser(id=user_id, username=username, first_name=first_name, last_name=last_name)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def get_name(self):
        if self.last_name:
            return self.first_name + ' ' + self.last_name
        else:
            return self.first_name

    @staticmethod
    def get_by_id_and_channel_name(channel_name: str, user_id: int):
        channel = Channel.get_by_name(channel_name)
        if channel.is_member_exists(user_id):
            return channel, BotUser.query.get(user_id)
        else:
            return None, None

    @staticmethod
    def get_by_id(user_id: int):
        return BotUser.query.get(user_id)

    def get_answers_by_channel_id(self, channel_id: int):
        return self.answers.filter(Answer.channel_id == channel_id).all()

    def to_dict(self, include_answers=False):
        if include_answers:
            answers = self.answers.all()
        else:
            answers = []
        return {
            'id': self.id,
            'username': self.username,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'answers': [a.to_dict() for a in answers]
        }


class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.BigInteger)
    channel_name = db.Column(db.String(100))
    channel_title = db.Column(db.String(100))
    members = db.relationship('BotUser', secondary=members, lazy='dynamic', backref=db.backref('channels', lazy=True))
    quizzes = db.relationship('Quiz', lazy='dynamic', backref='channel')

    def to_dict(self):
        return {
            'id': self.id,
            'chatId': self.chat_id,
            'channelName': self.channel_name,
            'channelTitle': self.channel_title
        }

    @staticmethod
    def add(channel_name, channel_title, chat_id):
        channel = Channel(channel_name=channel_name, channel_title=channel_title, chat_id=chat_id)
        db.session.add(channel)
        db.session.commit()
        return channel

    @staticmethod
    def get_by_name(channel_name: str):
        return Channel.query.filter(Channel.channel_name == channel_name).first()

    @staticmethod
    def get_by_chat_id(channel_chat_id: int):
        return Channel.query.filter(Channel.chat_id == channel_chat_id).first()
    
    @staticmethod
    def get_quizzes_by_channel_name(channel_name: str):
        channel = Channel.get_by_name(channel_name)
        if not channel:
            return None
        return channel.quizzes.order_by(Quiz.id.desc()).all()

    @staticmethod
    def get_quizzes_by_channel_id(channel_id: int):
        channel = Channel.query.get(channel_id)
        if not channel:
            return None
        return channel.quizzes.order_by(Quiz.id.desc()).all()

    def is_member_exists(self, bot_user_id: int) -> bool:
        return self.members.filter(members.c.bot_user_id == bot_user_id).count() > 0

    def add_member(self, bot_user: BotUser):
        if not self.is_member_exists(bot_user.id):
            self.members.append(bot_user)

    def remove_member(self, bot_user: BotUser):
        if self.is_member_exists(bot_user.id):
            self.members.remove(bot_user)

    def get_current_quiz(self):
        now = datetime.utcnow()
        return self.quizzes.filter(and_(Quiz.start_date <= now, now <= Quiz.end_date)).first()

    def get_channel_tests(self):
        return Test.query.filter(Test.channel_id == self.id).all()


class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(100))
    is_answer = db.Column(db.Boolean, default=False)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'value': self.value,
            'isAnswer': self.is_answer
        }

    @staticmethod
    def from_jsons(json_options):
        return [Option(value=opt['value'], is_answer=opt['isAnswer']) for opt in json_options]


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(150))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'))
    channel_id = db.Column(db.Integer)
    publish_date = db.Column(db.DateTime)
    file_path = db.Column(db.String(150))
    published = db.Column(db.Boolean, default=False)
    options = db.relationship('Option', lazy='dynamic', cascade="all,delete-orphan")
    answers = db.relationship('Answer', lazy='dynamic', cascade="all,delete-orphan")

    def to_dict(self):
        options = self.options.all()
        if self.file_path:
            file = os.path.basename(self.file_path)
        else:
            file = None
        return {
            'id': self.id,
            'question': self.question,
            'quizId': self.quiz_id,
            'publishDate': self.publish_date.strftime('%d.%m.%Y %H:%M'),
            'file': file,
            'options': [option.to_dict() for option in options],
            'answersCount': self.answers.count()
        }

    @staticmethod
    def create(json):
        test = Test()
        test.question = json['question']
        date_json = json['publishDate']
        time_json = json['publishTime']
        test.publish_date = datetime.strptime(date_json + ' ' + time_json, '%d.%m.%Y %H:%M')
        new_options = Option.from_jsons(json['options'])
        for opt in new_options:
            test.options.append(opt)
            db.session.add(opt)
        test.quiz_id = json['quizId']
        test.channel_id = Quiz.get_by_id(quiz_id=json['quizId']).channel_id
        db.session.add(test)
        db.session.commit()
        return test

    @staticmethod
    def get_by_id(test_id: int):
        return Test.query.get(test_id)
    
    @staticmethod
    def save_file(test_id: int, file):
        test = Test.get_by_id(test_id)
        if test.file_path:
            files.remove_file(test.file_path)
        file_path = os.path.join(Config.UPLOAD_FOLDER, secure_filename(file.filename))
        files.save_file(file, file_path, recreate=True)
        test.file_path = file_path
        db.session.commit()
        return file_path
    
    @staticmethod
    def update(test_id: int, json: dict):
        test = Test.get_by_id(test_id)
        test.question = json['question']
        date_json = json['publishDate']
        time_json = json['publishTime']
        test.publish_date = datetime.strptime(date_json + ' ' + time_json, '%d.%m.%Y %H:%M')
        new_options = Option.from_jsons(json['options'])
        current_options = test.options.all()
        for option in current_options:
            db.session.delete(option)
        for opt in new_options:
            test.options.append(opt)
            db.session.add(opt)
        db.session.commit()
        return test
    
    @staticmethod
    def remove(test_id: int):
        db.session.delete(Test.get_by_id(test_id))
        db.session.commit()

    def add_answer(self, answer):
        self.answers.append(answer)
        db.session.add(answer)
        db.session.commit()

    def get_count_user_answers(self, user_id):
        return self.answers.filter(Answer.user_id == user_id).count()

    def get_right_answer(self) -> Option:
        return self.options.filter(Option.is_answer == True).first()

    def user_given_right_answer(self, user_id):
        return self.answers.filter(and_(Answer.user_id == user_id, Answer.is_right == True)).count() > 0

    def make_published(self):
        self.published = True
        db.session.commit()


class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    top_count = db.Column(db.Integer)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))
    tests = db.relationship('Test', lazy='dynamic', backref='quiz', cascade='all,delete-orphan')

    def to_dict(self, include_tests=False, sortcallback=None):
        if include_tests:
            tests = self.tests.all()
        else:
            tests = []
        if include_tests and sortcallback:
            sortcallback(tests)
        return {
            'id': self.id,
            'startDate': self.start_date.strftime('%d.%m.%Y'),
            'endDate': self.end_date.strftime('%d.%m.%Y'),
            'topCount': self.top_count,
            'channelId': self.channel_id,
            'tests': [t.to_dict() for t in tests]
        }

    @staticmethod
    def create(json: dict, channel: Channel):
        new_quiz = Quiz()
        new_quiz.start_date = datetime.strptime(json['startDate'], '%d.%m.%Y')
        new_quiz.end_date = datetime.strptime(json['endDate'], '%d.%m.%Y')
        new_quiz.top_count = json['topCount']
        channel.quizzes.append(new_quiz)
        db.session.add(new_quiz)
        db.session.commit()
        return new_quiz
    
    @staticmethod
    def update(quiz_id: int, json: dict):
        quiz = Quiz.get_by_id(quiz_id)
        quiz.startDate = dateutils.convert_asia_tz_to_utc(datetime.strptime(json['startDate'], '%d.%m.%Y'))
        quiz.end_date = dateutils.convert_asia_tz_to_utc(datetime.strptime(json['endDate'], '%d.%m.%Y'))
        quiz.top_count = json['topCount']
        db.session.commit()
        return quiz
    
    @staticmethod
    def remove(quiz_id: int):
        db.session.delete(Quiz.query.get(quiz_id))
        db.session.commit()
    
    @staticmethod
    def get_by_id(quiz_id: int):
        return Quiz.query.get(quiz_id)
    
    @staticmethod
    def get_tests_by_quiz_id(quiz_id: int):
        quiz = Quiz.get_by_id(quiz_id)
        if not quiz:
            return None
        return quiz.tests.all()

    def get_published_tests(self):
        return self.tests.filter(Test.published == True).all()


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('bot_user.id'))
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'))
    points = db.Column(db.Integer)
    is_right = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    quiz_id = db.Column(db.Integer)
    channel_id = db.Column(db.Integer)

    @staticmethod
    def get_summary_user_points_by_channel_and_period(quiz_id: int, top_count):
        from sqlalchemy.sql import text
        sql = text("""SELECT bot_user.id, SUM(a.points) points_sum FROM bot_user 
        LEFT JOIN answer a on bot_user.id = a.user_id 
        WHERE a.quiz_id = :quiz_id GROUP BY bot_user.id ORDER BY points_sum DESC, a.id LIMIT :limit;""")
        result = db.engine.execute(sql, quiz_id=quiz_id, limit=top_count)
        return [(row[0], row[1]) for row in result]

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'testId': self.test_id,
            'points': self.points,
            'is_right': self.is_right,
            'createdAt': dateutils.convert_utc_to_asia_tz(self.created_at).strftime('%d.%m.%Y'),
            'channelId': self.channel_id,
            'quizId': self.quiz_id
        }


class Poll:
    def __init__(self, question: str, options: list):
        self.question = question
        self.options = options
