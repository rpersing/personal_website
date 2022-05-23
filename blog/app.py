import sqlite3
from flask import Flask, redirect, render_template, url_for, flash
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap
from flask_admin import Admin
from flask_login import login_required, login_user, LoginManager, logout_user, current_user
from flask_migrate import Migrate
from forms import LoginForm, RegisterForm, BlogpostForm
from models import db, Users, Blogpost
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid as uuid
import os
import secrets

app = Flask(__name__)
secret_key = secrets.token_hex(16)
app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///C:\Users\ryper\Desktop\DGST101\personal_website\blog\database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', page="Home")


@app.route('/blog')
def blog():

    posts = Blogpost.query.order_by(Blogpost.date_posted.desc())


    return render_template('blog.html', page="Blog", posts=posts)

@app.route('/blog/<int:id>')
def post(id):
    post = Blogpost.query.get_or_404(id)

    return render_template('post.html', post=post, page=f"Post {id}")

@app.route('/blog/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    post = Blogpost.query.get_or_404(id)
    form = BlogpostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data

        db.session.add(post)
        db.session.commit()
        flash("Post has been updated!")
        return redirect(url_for('post', id=post.id))
    
    if current_user.is_authenticated:
        form.title.data = post.title
        form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        return render_template('blog.html', page="Edit Post", form=form)


@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html', page="Portfolio")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        query = Users.query.filter_by(username=form.username.data).all()
        if not query:
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            new_user = Users(username=form.username.data, email=form.email.data, password=hashed_password)
            form.email.data = ''
            form.username.data = ''
            form.password.data = ''
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully!")
        else:
            flash('Sorry, that username not available')
            return redirect(url_for('register'))

    return render_template('register.html', page="Register", form=form)


@app.route('/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember_me.data)
                flash('User logged in succesfully!')
                return redirect(url_for('admin'))
            

    return render_template('login.html', page="Admin Login", form=form)


@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 1:
        return render_template('admin.html', page="Admin")
    else:
        flash("Sorry, you must be an admin to access this page.")
        return redirect(url_for('home'))


@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():

    id = current_user.id

    if id == 1:

        form = BlogpostForm()

        if form.validate_on_submit():
            poster = current_user.id
            post_pic = form.post_pic.data
            pic_filename = secure_filename(post_pic.filename)
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            post_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            post = Blogpost(title=form.title.data, content=form.content.data, author=form.author.data, post_thumbnail=pic_name, poster_id=poster, slug=form.slug.data)
            form.title.data = ''
            form.author.data = ''
            form.content = ''
            form.slug.data = ''

            db.session.add(post)
            db.session.commit()

            flash('Blog Post has been posted successfully!')
            return redirect(url_for('blog'))

        return render_template("add_post.html", page="Add Post", form=form)
    
    else:
        flash("Sorry, you must be an admin to access this page.")
        return redirect(url_for('home'))
        

if __name__ == '__main__':
    db.create_all(app=app)
    app.run()
