from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash

from authentication.jwt_auth import hash_password
from gateways.databases.gateway_database import Base


class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column('id', Integer, primary_key=True, nullable=False)
    email = Column('email', String, nullable=False)
    username = Column('username', String, nullable=False)
    password = Column('password', String, nullable=False)
    firstname = Column('nome', String, nullable=False)
    lastname = Column('sobrenome', String, nullable=False)
    address = Column('endereco', JSON)
    phone = Column('telefone', String)
    gender = Column('gender', String)
    api_token = Column('api_token', String)
    api_token_ts = Column('api_token_ts', Integer)
    created_at = Column('data_criacao', DateTime, server_default=func.now())
    active = Column('ativo', Boolean, default=True, nullable=False)
    user_type = Column('user_type', String(), default=False, nullable=False)

    carts = relationship("Cart", back_populates="user")

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value = value[0]
            if property == 'password':
                value = generate_password_hash(value)
            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column('titulo', String(500), nullable=False)
    price = Column('preco', Float, nullable=False)
    description = Column('descricao', String(1000), nullable=False)
    category = Column('categoria', String(100), nullable=False)
    image = Column('imagem', String(500), nullable=False)
    rating_rate = Column('media_avaliacao', Float, nullable=False)
    rating_count = Column('quantidade_avaliacao', Integer, nullable=False)
    active = Column('ativo', Boolean, default=True, nullable=False)
    created_at = Column('data_criacao', DateTime, server_default=func.now())

    def __init__(self, product_id, title, price, description, category, image, rating_rate, rating_count, active=True):
        self.id = product_id
        self.title = title
        self.price = price
        self.description = description
        self.category = category
        self.image = image
        self.rating_rate = rating_rate
        self.rating_count = rating_count
        self.active = active

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'description': self.description,
            'category': self.category,
            'image': self.image,
            'rating': {
                'rate': self.rating_rate,
                'count': self.rating_count
            },
            'active': self.active,
            'created_at': self.created_at
        }


class Cart(Base):
    __tablename__ = 'carts'

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column('id_usuario', Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column('data_criacao', DateTime, server_default=func.now())

    user = relationship("User", back_populates="carts")
    products = relationship("CartProduct", back_populates="cart")

    def __init__(self, id, user_id, created_at=None):
        self.id = id
        self.user_id = user_id
        self.created_at = created_at or func.now()

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at,
            'products': [product.serialize() for product in self.products]
        }


class CartProduct(Base):
    __tablename__ = 'cart_products'

    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey('carts.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)

    product = relationship("Product")
    cart = relationship("Cart", back_populates="products")

    def __init__(self, cart_id, product_id, quantity):
        self.cart_id = cart_id
        self.product_id = product_id
        self.quantity = quantity

    def serialize(self):
        return {
            'product': self.product.serialize(),
            'quantity': self.quantity
        }
