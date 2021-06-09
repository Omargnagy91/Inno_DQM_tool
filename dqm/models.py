import flask_bcrypt

from dqm import db, login_manager
from dqm import bcryt
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), unique=True, nullable=False)
    email_address = db.Column(db.String(length=50), unique=True, nullable=False)
    password_hash = db.Column(db.String(length=60), nullable=False)

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = flask_bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcryt.check_password_hash(self.password_hash, attempted_password)

    def __repr__(self):
        return f'User  {self.username}'

class MetaData(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    column_num = db.Column(db.Integer(), nullable=False)
    row_num = db.Column(db.Integer(), nullable=False)
    unique_row_num = db.Column(db.Integer(), nullable=False)
    unique_row_rate = db.Column(db.String(), nullable=False)
    filled_row_num = db.Column(db.Integer(), nullable=False)
    filled_row_rate = db.Column(db.String(), nullable=False)
    missing_row_num = db.Column(db.Integer(), nullable=False)
    missing_row_rate = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'{self.name}'

