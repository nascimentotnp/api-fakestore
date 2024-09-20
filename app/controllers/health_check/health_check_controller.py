from flask import Flask, jsonify, Blueprint
from flask_restx import Namespace, Resource, Api

from flask import Blueprint

health_blueprint = Blueprint('health_blueprint', __name__, url_prefix='/health')


class HealthCheck(Resource):
    @health_blueprint.route('/health_check')
    def get(self):
        response = {
            "status": "healthy",
            "message": "Service is up and running"
        }
        return response, 200
