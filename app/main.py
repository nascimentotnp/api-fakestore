import os
from flask_migrate import Migrate
from flask_minify import Minify
from sys import exit

from flask_restx import Api

from controllers.health_check_controller import health_ns
from controllers.home_controller import home_blueprint
from controllers.login_controller import authentication_blueprint, api
from controllers.products_controller import product_blueprint
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
app.register_blueprint(product_blueprint)
app.register_blueprint(home_blueprint)
api.add_namespace(health_ns)

if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)

if __name__ == "__main__":
    app.run()
