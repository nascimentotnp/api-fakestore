# import os
#
# from flask import Flask, render_template
# from flask.cli import load_dotenv
# # from config.log import setup_log
# # from config.timezone import set_default_timezone
# from controllers.authentication_controller import login_manager
# from domain.repository.product_repository import initialize_products_if_empty, read_all_products
# from gateways.api_fake.api_sale_gateway import fetch_and_store_products
# from gateways.databases.connection import engine
#
#
# def configure_database(app):
#     @app.before_first_request
#     def initialize_database():
#         from gateways.databases.gateway_database import Base
#         Base.metadata.create_all(engine)
#
#         if not read_all_products():
#             products = fetch_and_store_products()
#             if products:
#                 initialize_products_if_empty(products)
#
#
# def page_not_found(error):
#     return render_template('home/page-404.html'), 404
#
#
# def internal_server_error(error):
#     return render_template('home/page-500.html'), 500
#
#
# def access_forbidden(error):
#     return render_template('home/page-403.html'), 403
#
#
# def create_app(config_class):
#     load_dotenv()
#
#     app = Flask(__name__)
#
#     app.config.from_object(config_class)
#     app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', os.path.join(app.root_path, 'uploads'))
#
#     app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
#     app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#
#     login_manager.init_app(app)
#     configure_database(app)
#
#     app.register_error_handler(404, page_not_found)
#     app.register_error_handler(500, internal_server_error)
#     app.register_error_handler(403, access_forbidden)
#
#     return app
