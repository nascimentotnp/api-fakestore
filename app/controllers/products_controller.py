import logging
import os
from datetime import datetime

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename

from app import login_manager
from authentication.auth_middleware import token_required
from domain.repository.product_repository import (
    read_products_by_id, update_products, create_products,
    read_active_products, delete_products, update_product_price
)

product_blueprint = Blueprint('product_blueprint', __name__, url_prefix='/produtos')

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
            return redirect(url_for('product_blueprint.display_products'))
        else:
            return jsonify({'message': 'Produto não encontrado'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 400


@product_blueprint.route('/<int:product_id>/alterar-preco', methods=['POST'])
def change_product_price(product_id):
    try:
        data = request.get_json()
        product_price = data.get('price')
        change_price = update_product_price(product_id, product_price)
        if change_price:
            return jsonify({'message': 'Preço atualizado com sucesso!'}), 200
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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in os.getenv('ALLOWED_EXTENSIONS')


@product_blueprint.route('/criar', methods=['GET', 'POST'])
def create_product():
    if request.method == 'POST':
        # Pega os dados do formulário
        title = request.form['title']
        price = request.form['price']
        description = request.form['description']
        category = request.form['category']
        rating_rate = request.form['rating_rate']
        rating_count = request.form['rating_count']
        active = request.form['active'] == 'true'  # Converte para booleano

        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Monta o objeto do produto
            product_data = {
                'title': title,
                'price': price,
                'description': description,
                'category': category,
                'image': filename,
                'rating_rate': rating_rate,
                'rating_count': rating_count,
                'active': active,
                'created_at': datetime.now().strftime('%Y-%m-%d')
            }

            # Chama a função que cria o produto no repositório
            try:
                create_products(**product_data)
                flash('Produto criado com sucesso!', 'success')
                return redirect(url_for('product_blueprint.display_products'))
            except Exception as e:
                flash(f'Ocorreu um erro: {str(e)}', 'danger')

    return render_template('home/create_product.html')


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403
