from flask import render_template
from flask_login import LoginManager

from domain.repository.user_repository import read_user_by_id, read_user_by_username

login_manager = LoginManager()

login_manager.login_view = "authentication_blueprint.login"


@login_manager.user_loader
def load_user(user_id):
    return read_user_by_id(user_id)


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = read_user_by_username(username)
    return user if user else None
