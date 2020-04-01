import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    bday = sqlalchemy.Column(sqlalchemy.Date,
                             nullable=True)
    posts = orm.relation("Posts", back_populates='user')
    messages_from = orm.relation("Messages", back_populates='from_user')
    messages_to = orm.relation("Messages", back_populates='to_user')

    def __repr__(self):
        return '; '.join((self.name, self.surname, self.email))

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
