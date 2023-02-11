def setup_app(app):
    app.secret_key = '487162874612'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'myflaskapp'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
