from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date, datetime
db = SQLAlchemy()

class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
	# Foreign Key To Link Users (refer to primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_thumbnail = db.Column(db.String(), nullable=True)

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(320))
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(30))
    