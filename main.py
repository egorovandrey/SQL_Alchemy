from flask import Flask
from data import db_session
from data.messages import Messages
from data.posts import Posts
from data.users import User

from flask import render_template, redirect, abort, request, make_response
from forms.register import RegisterForm
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_wtf import FlaskForm
from flask_wtf.html5 import EmailField
from wtforms import PasswordField, BooleanField, SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')


class MessageForm(FlaskForm):
    content = TextAreaField("Сообщение")
    submit = SubmitField('Отправить')


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init('db/blogs.sqlite')


@app.route('/new_message/<int:id>',  methods=['GET', 'POST'])
@login_required
def new_message(id):
    form = MessageForm()
    session = db_session.create_session()
    user = session.query(User).filter(User.id == id).first()
    if form.validate_on_submit():
        message = Messages()
        message.from_id = current_user.id
        message.to_id = id
        message.message = form.content.data
        current_user.messages_from.append(message)
        session.merge(current_user)
        session.commit()
        return redirect('/users')
    return render_template('new_message.html', form=form, user=user)



@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    session = db_session.create_session()
    news = session.query(Posts).filter(Posts.id == id,
                                      Posts.user == current_user).first()
    if news:
        session.delete(news)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        session = db_session.create_session()
        news = session.query(Posts).filter(Posts.id == id,
                                          Posts.user == current_user).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        news = session.query(Posts).filter(Posts.id == id,
                                          Posts.user == current_user).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html', title='Редактирование новости', form=form)


@app.route('/news',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        news = Posts()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.posts.append(news)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            surname=form.surname.data,
            bday=form.bday.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/")
def index():
    session = db_session.create_session()
    if current_user.is_authenticated:
        news = session.query(Posts).filter(
            (Posts.user == current_user) | (Posts.is_private != True))
    else:
        news = session.query(Posts).filter(Posts.is_private != True)
    return render_template("index.html", news=news)


@app.route("/users")
@login_required
def show_users():
    session = db_session.create_session()
    users = session.query(User).filter((User.id != current_user.id))
    return render_template("users.html", users=users)


@app.route("/messages/<int:id>")
@login_required
def show_messages(id):
    session = db_session.create_session()
    user = session.query(User).filter((User.id == id)).first()
    messages = session.query(Messages).filter(Messages.from_id.in_([current_user.id, user.id]),
                                              Messages.to_id.in_([current_user.id, user.id])).order_by(Messages.created_date)
    return render_template("messages.html", user=user, messages=messages)



def main():

    app.run()


if __name__ == '__main__':
    main()
