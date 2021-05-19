from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email
from application.core.models import AdminUser


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired('Укажите Email'), Email('Неверный формат Email')])
    password = PasswordField('Пароль', validators=[DataRequired('Введите пароль')])
    submit = SubmitField('Войти')

    def validate_email(self, field):
        if not AdminUser.get_by_email(field.data):
            raise ValidationError('Такой Email не зарегистрирован')

    def validate_password(self, field):
        user = AdminUser.get_by_email(self.email.data)
        if not user:
            return True
        if not user.check_password(field.data):
            raise ValidationError('Неверный пароль для {}'.format(user.email))
        return True
