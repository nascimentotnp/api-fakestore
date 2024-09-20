from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import TextAreaField, SubmitField
from wtforms.validators import Email, DataRequired


class LoginForm(FlaskForm):
    username = StringField('Username',
                           id='username_login',
                           validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])


class CreateAccountForm(FlaskForm):
    username = StringField('Login', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    firstname = StringField('Nome', validators=[DataRequired()])
    lastname = StringField('Sobrenome', validators=[DataRequired()])
    address = StringField('Endereço', validators=[DataRequired()])
    phone = StringField('Telefone', validators=[DataRequired()])
    gender = SelectField('Gênero', choices=[
        ('Masculino', 'Masculino'),
        ('Feminino', 'Feminino'),
        ('Não declarado', 'Não declarado')
    ], validators=[DataRequired()])
