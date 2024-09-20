from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import current_user, login_user, logout_user


from flask import Blueprint

logout_blueprint = Blueprint('logout_blueprint', __name__, url_prefix='/logout')


@logout_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login.login'))
