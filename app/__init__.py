import os

from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from domain.repository.product_repository import read_all_products, initialize_products_if_empty
from domain.repository.user_repository import read_user_by_id
from gateways.api_fake.api_sale_gateway import fetch_and_store_products
from gateways.databases.connection import engine

from controllers.home_controller import home_blueprint
from controllers.login_controller import authentication_blueprint
from controllers.products_controller import product_blueprint

db = SQLAlchemy()
login_manager = LoginManager()


def register_extensions(app):
    login_manager.init_app(app)
    login_manager.login_view = "authentication.login"  # Match the route name in your login blueprint

    @login_manager.user_loader
    def load_user(user_id):
        return read_user_by_id(user_id)


def register_blueprints(app):
    app.register_blueprint(authentication_blueprint)
    app.register_blueprint(product_blueprint)
    app.register_blueprint(home_blueprint)


def configure_database(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'postgresql://postgres:root@appstore-db:5432/sale')


    @app.before_first_request
    def initialize_database():
        from gateways.databases.gateway_database import Base
        Base.metadata.create_all(engine)

        if not read_all_products():
            products = fetch_and_store_products()
            if products:
                initialize_products_if_empty(products)


def page_not_found(error):
    return render_template('home/page-404.html'), 404


def internal_server_error(error):
    return render_template('home/page-500.html'), 500


def access_forbidden(error):
    return render_template('home/page-403.html'), 403


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)
    app.register_error_handler(403, access_forbidden)
    return app
