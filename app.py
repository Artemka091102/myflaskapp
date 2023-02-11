from flask import Flask, render_template, flash, redirect, url_for, request, session
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
from functools import wraps

from forms import ArticleForm
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
    session['id'] = request.args.get('id', None)
    session['first_name'] = request.args.get('first_name', None)
    session['last_name'] = request.args.get('last_name', None)
    session['username'] = request.args.get('username', None)
    session['photo_url'] = request.args.get('photo_url', None)
    session['auth_date'] = request.args.get('auth_date', None)
    session['hash'] = request.args.get('hash', None)
    session['logged_in'] = True
    flash('You are now logged in', 'success')
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


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
