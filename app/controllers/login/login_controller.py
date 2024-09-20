from datetime import datetime, timezone

import flask
from flask import Blueprint
from flask import render_template, redirect, request, url_for
from flask_login import current_user, logout_user, login_user
from flask_restx import Resource, Api

from authentication.forms import CreateAccountForm, LoginForm
from authentication.jwt_auth import verify_pass, generate_api_token
from domain.entity.entities import User
from domain.repository.user_repository import read_user_by_username, read_user_by_email
from gateways.databases.connection import session

authentication_blueprint = Blueprint('authentication_blueprint', __name__)
api = Api(authentication_blueprint)


@authentication_blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))


@authentication_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)

    print(f"{current_user} Passei aqui")

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
        session.add(user)
        session.commit()

        user.api_token = generate_api_token(user.id)
        user.api_token_ts = int(datetime.now(timezone.utc).timestamp())
        session.commit()

        logout_user()

        return render_template('accounts/register.html',
                               msg='User created successfully.',
                               success=True,
                               form=create_account_form)
    else:
        return render_template('accounts/register.html', form=create_account_form)


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
