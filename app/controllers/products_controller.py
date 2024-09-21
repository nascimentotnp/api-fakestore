import logging

from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from app import login_manager
from authentication.auth_middleware import token_required
from domain.repository.product_repository import (
    read_products_by_id, update_products, create_products,
    read_active_products, delete_products
)

product_blueprint = Blueprint('product_blueprint', __name__, url_prefix='/produtos')

# Modelo de produto (se você não precisar mais de um Namespace, pode remover)
products_model = {
    'id': {'type': 'integer', 'readonly': True, 'description': 'ID do produto'},
    'title': {'type': 'string', 'required': True, 'description': 'Título do produto'},
    'price': {'type': 'number', 'required': True, 'description': 'Preço do produto'},
    'description': {'type': 'string', 'required': True, 'description': 'Descrição do produto'},
    'category': {'type': 'string', 'required': True, 'description': 'Categoria do Produto'},
    'image': {'type': 'string', 'required': True, 'description': 'Imagem do Produto'},
    'rating_rate': {'type': 'number', 'required': True, 'description': 'Taxa de classificação'},
    'rating_count': {'type': 'integer', 'required': True, 'description': 'Contagem de classificação'},
    'active': {'type': 'boolean', 'required': True, 'description': 'Ativo'},
    'created_at': {'type': 'string', 'format': 'date', 'required': True, 'description': 'Data de criação'}
}


@product_blueprint.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    if request.method == 'GET':
        product = read_products_by_id(product_id)
        if product:
            return jsonify(product)
        else:
            return jsonify({'message': 'Produto não encontrado ou descontinuado, favor verificar com o suporte'}), 404


@product_blueprint.route('/<int:product_id>', methods=['PUT'])
def edit_product(product_id):
    if request.method == 'PUT':
        data = request.json
        try:
            updated = update_products(product_id, **data)
            if updated:
                return {'message': 'Produto atualizado com sucesso'}, 200
            else:
                return jsonify({'message': 'Produto não encontrado'}), 404
        except Exception as e:
            return jsonify({'message': str(e)}), 400


@product_blueprint.route('/<int:product_id>/excluir', methods=['POST'])
def delete_product(product_id):
    try:
        deleted = delete_products(product_id)
        if deleted:
            return redirect(url_for('product_blueprint.display_products'))  # Redireciona para a lista de produtos
        else:
            return jsonify({'message': 'Produto não encontrado'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 400


@product_blueprint.route('', methods=['POST'])
def products_list():
    if request.method == 'POST':
        data = request.json
        try:
            create_products(**data)
            return {'message': 'Produto criado com sucesso'}, 201
        except Exception as e:
            return {'message': 'Erro ao criar produto', 'error': str(e)}, 400


@product_blueprint.route('', methods=['GET'])
def display_products():
    try:
        products = read_active_products()
        if not products:
            logging.error("No active products found")
        return render_template('home/products.html', products=products)
    except Exception as e:
        return f"Erro ao carregar produtos: {str(e)}", 500


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403
