from flask import Flask, render_template, flash, redirect, url_for, request, session
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
from functools import wraps

from forms import RegisterForm, LoginForm, ArticleForm
from supersecret import setup_app

app = Flask(__name__)
setup_app(app)
mysql = MySQL(app)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        return redirect(url_for('home'))

    return decorated_function


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()
    all_articles = cur.execute(
        'SELECT * FROM articles'
    )
    if all_articles:
        all_articles = cur.fetchall()
    cur.close()
    if all_articles:
        return render_template('dashboard.html', all_articles=all_articles)
    return render_template('dashboard.html', msg='No Articles Found')


@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('home'))


@app.route('/articles')
def articles():
    cur = mysql.connection.cursor()
    all_articles = cur.execute(
        'SELECT * FROM articles'
    )
    if all_articles:
        all_articles = cur.fetchall()
    cur.close()
    if all_articles:
        return render_template('articles.html', all_articles=all_articles)
    return render_template('articles.html', msg='No Articles Found')


@app.route('/article/<string:article_id>')
def article(article_id):
    cur = mysql.connection.cursor()
    art = cur.execute(
        'SELECT * FROM articles WHERE id = %s',
        [article_id]
    )
    if art:
        art = cur.fetchone()
    cur.close()
    return render_template('article.html', art=art)


@app.route('/edit_article/<string:article_id>', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        cur = mysql.connection.cursor()
        cur.execute(
            'UPDATE articles SET title = %s, body = %s WHERE id = %s',
            [title, body, article_id]
        )
        mysql.connection.commit()
        cur.close()
        flash('Article changed', 'success')
        return redirect(url_for('dashboard'))
    cur = mysql.connection.cursor()
    art = cur.execute(
        'SELECT * FROM articles WHERE id = %s',
        [article_id]
    )
    if art:
        art = cur.fetchone()
    cur.close()
    form.title.data = art['title']
    form.body.data = art['body']
    return render_template('edit_article.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.hash(form.password.data)
        cur = mysql.connection.cursor()
        cur.execute(
            'INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)',
            [name, email, username, password]
        )
        mysql.connection.commit()
        cur.close()
        flash('You are now registered and can log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        cur = mysql.connection.cursor()
        users = cur.execute(
            'SELECT * FROM users WHERE username = %s',
            [username]
        )
        if users:
            user = cur.fetchone()
            if sha256_crypt.verify(password, user['password']):
                session['logged_in'] = True
                session['username'] = username
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Wrong Password', 'danger')
        else:
            flash('Wrong Username', 'danger')
        cur.close()
    return render_template('login.html', form=form)


@app.route('/add_article', methods=['GET', 'POST'])
@login_required
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        cur = mysql.connection.cursor()
        cur.execute(
            'INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)',
            [title, body, session['username']]
        )
        mysql.connection.commit()
        cur.close()
        flash('Article created', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_article.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
