from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms.fields import PasswordField, StringField, TextAreaField, SubmitField
from wtforms.fields.html5 import EmailField, DateField


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    surname = StringField("Фамилия пользователя", validators=[DataRequired()])
    bday = DateField('Дата рождения')
    submit = SubmitField('Регистрация')
