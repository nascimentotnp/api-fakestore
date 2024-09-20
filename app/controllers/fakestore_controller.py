import logging

from flask import Blueprint, jsonify
from flask_restx import Namespace, Resource

from gateways.api_fake.api_sale_gateway import fetch_and_store_products

api_gateway_controller = Blueprint('api_gateway', __name__)


@api_gateway_controller.route('/fetch-products')
class FetchExternalProducts(Resource):
    def get(self):
        try:
            return fetch_and_store_products()
        except Exception as e:
            return {"error": str(e)}, 500
