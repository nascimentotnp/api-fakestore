import logging
import os
from flask_migrate import Migrate
from flask_minify import Minify
from sys import exit

from controllers.health_check.health_check_controller import health_blueprint
from controllers.home.home_controller import home_blueprint
from controllers.login.login_controller import authentication_blueprint
from controllers.logout.logout_controller import logout_blueprint
from controllers.products.products_controller import products_blueprint
from gateways.databases.config import config_dict
from app import create_app

DEBUG = (os.getenv('DEBUG', 'False') == 'True')

get_config_mode = 'Debug' if DEBUG else 'Production'

try:

    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)
Migrate(app)


app.register_blueprint(authentication_blueprint)
app.register_blueprint(home_blueprint)
app.register_blueprint(logout_blueprint)
app.register_blueprint(products_blueprint)
app.register_blueprint(health_blueprint)


if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)


if __name__ == "__main__":

    app.run()
