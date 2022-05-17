from flask import render_template
from app import app

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', page="Home")

@app.route('/login')
def login():
    return render_template('login.html', page="Login")

@app.route('/blog')
def blog():
    return render_template('blog.html', page="Blog")


@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html', page="Portfolio")


if __name__ == '__main__':
    app.run()