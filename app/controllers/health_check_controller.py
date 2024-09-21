from flask import Flask, jsonify, Blueprint
from flask_restx import Namespace, Resource, Api


health_ns = Namespace('health', description='Health check do sistema')


@health_ns.route('/')
class HealthCheck(Resource):
    def get(self):
        response = {
            "status": "healthy",
            "message": "Service is up and running"
        }
        return response, 200
