from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import TextAreaField, SubmitField
from wtforms.validators import Email, DataRequired, EqualTo, NumberRange
from wtforms_components import DecimalField


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


class ChangePassForm(FlaskForm):
    current_password = PasswordField('Senha Atual', validators=[DataRequired()])
    new_password = PasswordField('Nova Senha', validators=[DataRequired()])
    confirm_new_password = PasswordField('Confirmar Nova Senha', validators=[DataRequired()])


class CreateProductForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0.01, message="Price must be greater than zero.")])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Category', choices=[("women's clothing", "Women's Clothing"), ("electronics", "Electronics"),
                                                ("men's clothing", "Men's Clothing"), ("jewelry", "Jewelry")],
                           validators=[DataRequired()])
    rating_rate = DecimalField('Rating Rate', validators=[NumberRange(min=0, max=5, message="Rating must be between 0 and 5.")])
    rating_count = IntegerField('Rating Count', validators=[NumberRange(min=0, message="Rating count must be zero or higher.")])
