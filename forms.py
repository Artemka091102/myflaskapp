from wtforms import Form, StringField, PasswordField, validators, TextAreaField


class RegisterForm(Form):
    form_title = 'Register'
    name = StringField('Name', [
        validators.DataRequired(),
        validators.Length(min=1, max=50)
    ])
    username = StringField('Username', [
        validators.DataRequired(),
        validators.Length(min=4, max=25)
    ])
    email = StringField('Email', [
        validators.DataRequired(),
        validators.Length(min=6, max=50)
    ])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm password', [
        validators.DataRequired()
    ])


class LoginForm(Form):
    form_title = 'Login'
    username = StringField('Username', [
        validators.DataRequired(),
        validators.Length(min=4, max=25)
    ])
    password = PasswordField('Password', [
        validators.DataRequired(),
    ])


class ArticleForm(Form):
    form_title = 'New Article'
    title = StringField('Title', [
        validators.Length(min=1, max=200)
    ])
    body = TextAreaField('Body', [
        validators.Length(min=30)
    ])
