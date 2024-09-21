from flask import Blueprint
from flask import request, jsonify, render_template
from flask_restx import Namespace, fields, Resource

from app import login_manager
from authentication.auth_middleware import token_required
from domain.repository.product_repository import (
    read_products_by_id, update_products, create_products,
    read_active_products, delete_products
)

products_ns = Namespace('produtos', description='Operações relacionadas a Produtos')

products_model = products_ns.model('Produtos', {
    'id': fields.Integer(readonly=True, description='ID do produto'),
    'title': fields.String(required=True, description='Título do produto'),
    'price': fields.Float(required=True, description='Preço do produto'),
    'description': fields.String(required=True, description='Descrição do produto'),
    'category': fields.String(required=True, description='Categoria do Produto'),
    'image': fields.String(required=True, description='Imagem do Produto'),
    'rating_rate': fields.Float(required=True, description='Taxa de classificação'),
    'rating_count': fields.Integer(required=True, description='Contagem de classificação'),
    'active': fields.Boolean(required=True, description='ativo'),
    'created_at': fields.Date(required=True, description='data_criacao')
})
products_ns.doc(security='Bearer Auth')


@products_ns.route('/<int:products_id>')
@products_ns.param('products_id', 'ID do produto')
class ProductController(Resource):
    @products_ns.doc('get_products')
    @products_ns.marshal_with(products_model)
    def get(self, products_id):
        product = read_products_by_id(products_id)
        if product:
            return product
        else:
            products_ns.abort(404, message='Produto não encontrado ou descontinuado, favor verificar com o suporte')

    @products_ns.doc('update_products')
    @products_ns.expect(products_model)
    @products_ns.doc(security='Bearer Auth')
    @token_required
    def put(self, products_id):
        data = request.json
        update_products(products_id, **data)
        return {'message': 'Produto atualizado com sucesso'}, 200

    @products_ns.doc('delete_products')
    @products_ns.doc(security='Bearer Auth')
    @token_required
    def delete(self, products_id):
        delete_products(products_id)
        return {'message': 'Produto excluído com sucesso'}, 200


@products_ns.route('')
class ProductsList(Resource):
    @products_ns.doc('create_products')
    @products_ns.expect(products_model)
    @products_ns.doc(security='Bearer Auth')
    @token_required
    def post(self):
        data = products_ns.payload
        create_products(**data)
        return {'message': 'Produto criado com sucesso'}, 201

    @products_ns.doc('get_products')
    @products_ns.marshal_list_with(products_model)
    def get(self):
        products = read_active_products()
        return products


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403
