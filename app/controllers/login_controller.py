from datetime import datetime, timezone

import flask
from flask import Blueprint, flash
from flask import render_template, redirect, request, url_for
from flask_login import current_user, logout_user, login_user
from flask_restx import Resource, Api, fields
from werkzeug.security import check_password_hash, generate_password_hash

from authentication.forms import CreateAccountForm, LoginForm, ChangePassForm
from authentication.jwt_auth import verify_pass, generate_api_token, get_api
from domain.entity.entities import User
from domain.repository.login_repository import is_strong_password
from domain.repository.user_repository import read_user_by_username, read_user_by_email, update_password
from gateways.databases.connection import session

authentication_blueprint = Blueprint('authentication_blueprint', __name__, url_prefix='/')

api = get_api(authentication_blueprint)
login_model = api.model('Login', {
    'username': fields.String(required=True, description='Nome de usuário'),
    'password': fields.String(required=True, description='Senha')
})


@authentication_blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))


@authentication_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)

    if flask.request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = read_user_by_username(username=username)

        if user and verify_pass(user.password, password):
            login_user(user)
            return redirect(url_for('authentication_blueprint.route_default'))

        return render_template('accounts/login.html',
                               msg='Wrong user or password',
                               form=login_form)
    if current_user.is_authenticated:
        return redirect(url_for('home_blueprint.index'))
    else:
        return render_template('accounts/login.html', form=login_form)


@api.route('/login/jwt/', methods=['POST'])
class JWTLogin(Resource):
    @api.expect(login_model)
    def post(self):
        try:
            data = request.form if request.form else request.json
            if not data:
                return {
                    'message': 'username or password is missing',
                    "data": None,
                    'success': False
                }, 400
            username = data.get('username')
            password = data.get('password')
            user = read_user_by_username(username)
            if user and verify_pass(user.password, password):
                try:
                    if not user.api_token:
                        user.api_token = generate_api_token(user.id)
                        user.api_token_ts = int(datetime.now(timezone.utc).timestamp())
                        session.commit()
                    return {
                        "message": "Successfully fetched auth token",
                        "success": True,
                        "data": user.api_token
                    }
                except Exception as e:
                    return {
                        "error": "Something went wrong",
                        "success": False,
                        "message": str(e)
                    }, 500
            return {
                'message': 'username or password is wrong',
                'success': False
            }, 403
        except Exception as e:
            return {
                "error": "Something went wrong",
                "success": False,
                "message": str(e)
            }, 500


@authentication_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))


@authentication_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        address = request.form.get('address')
        phone = request.form.get('phone')
        gender = request.form.get('gender')

        valid_fields = {
            'email': email,
            'username': username,
            'password': password,
            'firstname': firstname,
            'lastname': lastname,
            'address': address,
            'phone': phone,
            'gender': gender
        }

        user = read_user_by_username(username=username)
        if user:
            return render_template('accounts/register.html',
                                   msg='Username already registered',
                                   success=False,
                                   form=create_account_form)

        user = read_user_by_email(email=email)
        if user:
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form)

        user = User(username=username, email=email, password=password,
                    firstname=firstname, lastname=lastname,
                    address=address, phone=phone, gender=gender,
                    api_token=None, api_token_ts=None)
        if not is_strong_password(password):
            flash(
                'A nova senha deve ter pelo menos 8 caracteres, incluindo letras maiúsculas, minúsculas, números e símbolos.',
                'danger')
            return render_template('accounts/register.html',
                                   msg='A nova senha não atende aos requisitos de segurança.', form=create_account_form)
        if not gender:
            return render_template('accounts/register.html',
                                   msg='Por favor, selecione um gênero.',
                                   success=False,
                                   form=create_account_form)

        session.add(user)
        session.commit()

        user.api_token = generate_api_token(user.id)
        user.api_token_ts = int(datetime.now(timezone.utc).timestamp())
        session.commit()

        logout_user()

        return render_template('accounts/register.html',
                               msg=f"Usuário {request.form.get('username')} criado com sucesso.",
                               success=True,
                               form=create_account_form)
    else:
        return render_template('accounts/register.html', form=create_account_form)


@authentication_blueprint.route('/change-password/', methods=['GET', 'POST'])
def change_password():
    change_pass_form = ChangePassForm()

    print(f"metodo {flask.request.method}")

    if flask.request.method == 'POST':
        current_password = change_pass_form.current_password.data
        new_password = change_pass_form.new_password.data
        confirm_new_password = change_pass_form.confirm_new_password.data
        print(confirm_new_password)

        if not check_password_hash(current_user.password, current_password):
            flash('Senha atual incorreta.', 'danger')
            return render_template('accounts/change_password.html', msg='Senha atual incorreta.', form=change_pass_form)

        # Check if new passwords match
        if new_password != confirm_new_password:
            flash('As novas senhas não coincidem.', 'danger')
            return render_template('accounts/change_password.html', msg='As novas senhas não coincidem.',
                                   form=change_pass_form)

        # Check password strength
        if not is_strong_password(new_password):
            flash(
                'A nova senha deve ter pelo menos 8 caracteres, incluindo letras maiúsculas, minúsculas, números e símbolos.',
                'danger')
            return render_template('accounts/change_password.html',
                                   msg='A nova senha não atende aos requisitos de segurança.', form=change_pass_form)

        update_password(current_user.id, password=generate_password_hash(new_password))

        flash('Senha alterada com sucesso!', 'success')
        return redirect(url_for('authentication_blueprint.logout'))

    return render_template('accounts/change_password.html', form=change_pass_form)


# Errors
@authentication_blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@authentication_blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@authentication_blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
