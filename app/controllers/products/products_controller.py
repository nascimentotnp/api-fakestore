from flask import Blueprint, request, jsonify, render_template
from app import login_manager

from domain.repository.product_repository import (
    read_products_by_id, update_products, create_products,
    read_active_products, delete_products
)
from flask import Blueprint

products_blueprint = Blueprint('products_blueprint', __name__, url_prefix='/products')


@products_blueprint.route('/<int:products_id>', methods=['GET'])
def get_product(products_id):
    product = read_products_by_id(products_id)
    if product:
        return jsonify(product), 200
    else:
        return jsonify({'message': 'Produto não encontrado ou descontinuado'}), 404


@products_blueprint.route('/<int:products_id>', methods=['PUT'])
def update_product(products_id):
    data = request.get_json()
    update_products(products_id, **data)
    return jsonify({'message': 'Produto atualizado com sucesso'}), 200


@products_blueprint.route('/<int:products_id>', methods=['DELETE'])
def delete_product(products_id):
    delete_products(products_id)
    return jsonify({'message': 'Produto excluído com sucesso'}), 200


@products_blueprint.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    create_products(**data)
    return jsonify({'message': 'Produto criado com sucesso'}), 201


@products_blueprint.route('/products', methods=['GET'])
def get_all_products():
    products = read_active_products()
    products_list = [product.to_dict() for product in products]
    return jsonify(products_list), 200


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403
