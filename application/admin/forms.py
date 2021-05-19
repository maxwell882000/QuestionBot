from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, FieldList, BooleanField, Form, FormField, HiddenField
from wtforms.validators import DataRequired, ValidationError, Length
from application.core.services import channels
from application import telegram_bot
from telebot.apihelper import ApiException
import re
from datetime import datetime
import settings


class NewChannelForm(FlaskForm):
    channel_name_url = StringField("Канал", validators=[DataRequired('Укажите ссылку на канал или его юзернейм')])
    submit = SubmitField('Сохранить')

    def validate_channel_name_url(self, field):
        if field.data.strip() != '':
            url_re = r'https?:\/\/(t(elegram)?\.me|telegram\.org)\/([a-z0-9\_])'
            if not (re.match(url_re, field.data) or field.data.startswith('@')):
                raise ValidationError('Указан неверный формат ссылки или юзернейма канала')
            if re.match(url_re, field.data):
                channel_name = '@' + field.data[field.data.rfind('/') + 1:]
            else:
                channel_name = field.data
            if channels.channel_exists(channel_name):
                raise ValidationError('Такой канал уже добавлен')
            try:
                channel_chat = telegram_bot.get_chat(channel_name)
            except ApiException:
                raise ValidationError('Указанный канал отсутствует, либо является привытаным')
            if channel_chat.type != 'channel':
                raise ValidationError('Указанный юзернейм не является каналом')
            try:
                sent_message = telegram_bot.send_message(channel_name, 'Test', disable_notification=True)
                telegram_bot.delete_message(sent_message.chat.id, sent_message.message_id)
            except ApiException:
                raise ValidationError('Бот не имеет доступа к отправке и удалению сообщений')
            self.chat_id = sent_message.chat.id
            self.channel = channel_chat

    def get_channel_chat_id(self):
        return self.chat_id

    def get_channel(self):
        return self.channel


class NewQuizForm(FlaskForm):
    start_date = StringField('Дата начала', validators=[DataRequired('Укажите дату начала викторины')])
    end_date = StringField('Дата конца', validators=[DataRequired('Укажите дату окончания')])
    top_count = StringField('Количество топ игроков', validators=[DataRequired("Укажите количество лучших игроков")])
    submit = SubmitField('Сохранить')

    def validate_top_count(self, field):
        if field.data != '':
            if not field.data.isdigit():
                raise ValidationError('Укажите число')
            if int(field.data) < 0:
                raise ValidationError('Укажите положительное число либо ноль')


class OptionForm(Form):
    value = StringField(validators=[DataRequired('Укажите значение варианта')])
    is_answer = BooleanField()


class TestForm(FlaskForm):
    question = StringField('Тестовый вопрос',
                           validators=[DataRequired('Укажите вопрос'),
                                       Length(max=150, message="Длина вопроса - не более 150 символов.")])
    publish_date = StringField('День публикации', validators=[DataRequired('Укажите день публикации')])
    publish_time = StringField('Время публикации', validators=[DataRequired('Укажите время публикации')])
    file = FileField('Файл')
    options = FieldList(FormField(OptionForm))
    start_date = HiddenField()
    end_date = HiddenField()

    def init(self):
        self.options.append_entry()

    def fill_from_object(self, test):
        self.question.data = test.question
        self.publish_date.data = test.publish_date.strftime('%d.%m.%Y')
        self.publish_time.data = test.publish_date.strftime('%H:%M')
        for option in test.options.all():
            option_field = OptionForm()
            option_field.value = option.value
            option_field.is_answer = option.is_answer
            self.options.append_entry(option_field)
        self.start_date.data = test.quiz.start_date.strftime('%d.%m.%Y')
        self.end_date.data = test.quiz.end_date.strftime('%d.%m.%Y')

    def set_start_end_dates(self, start_date: datetime, end_date: datetime):
        self.start_date.data = start_date.strftime('%d.%m.%Y')
        self.end_date.data = end_date.strftime('%d.%m.%Y')

    def validate_publish_date(self, field):
        if field.data != '':
            date = datetime.strptime(field.data, '%d.%m.%Y')
            start_date = datetime.strptime(self.start_date.data, '%d.%m.%Y')
            end_date = datetime.strptime(self.end_date.data, '%d.%m.%Y')
            if date < start_date or date > end_date:
                raise ValidationError('День публикации выходит за рамки виктрорины')

    def validate_options(self, field):
        answers = list(filter(lambda option: option.is_answer, field.entries))
        if len(answers) == 0:
            raise ValidationError('Вы не выбрали правильный ответ')


class SettingsForm(FlaskForm):
    right_answer_point = StringField("Очков за правильный ответ", validators=[DataRequired()])

    def fill_from_settings(self):
        self.right_answer_point.data = settings.get_right_answer_points()
