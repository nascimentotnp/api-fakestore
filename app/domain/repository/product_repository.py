import logging

from sqlalchemy.exc import SQLAlchemyError

from domain.entity.entities import Product
from gateways.databases.connection import session


def create_products(product_id, title, price, description, category, image, rating_rate, rating_count):
    if read_products_by_id(product_id):
        logging.info(f'Produto {product_id} já existe no banco.')
        return
    new_product = Product(
        title=title,
        price=price,
        description=description,
        category=category,
        image=image,
        rating_rate=rating_rate,
        rating_count=rating_count
    )
    session.add(new_product)
    session.commit()


def read_all_products():
    return session.query(Product).all()


def read_active_products():
    products = session.query(Product).filter(Product.active).all()
    return products


def read_products_by_id(product_id):
    return session.query(Product).filter(Product.id == product_id, Product.active == True).first()


def update_products(product_id, **kwargs):
    product = session.query(Product).get(product_id)
    for key, value in kwargs.items():
        setattr(product, key, value)
    session.commit()


def delete_products(product_id):
    product = session.query(Product).get(product_id)
    product.active = False
    session.commit()


def persist_products(products):
    try:
        for product_data in products:
            product = session.query(Product).filter_by(id=product_data['id']).first()

            if product:
                product.title = product_data['title']
                product.price = product_data['price']
                product.description = product_data['description']
                product.category = product_data['category']
                product.image = product_data['image']
                product.rating_rate = product_data['rating']['rate']
                product.rating_count = product_data['rating']['count']
            else:
                new_product = Product(
                    product_id=product_data['id'],
                    title=product_data['title'],
                    price=product_data['price'],
                    description=product_data['description'],
                    category=product_data['category'],
                    image=product_data['image'],
                    rating_rate=product_data['rating']['rate'],
                    rating_count=product_data['rating']['count']
                )
                session.add(new_product)

        session.commit()
        logging.info("Produtos persistidos com sucesso.")
    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f"Ocorreu um erro ao persistir os produtos: {e}")
    finally:
        session.close()


def initialize_products_if_empty(products):
    existing_product = session.query(Product).first()

    if existing_product is None:
        logging.info("Nenhum produto encontrado no banco de dados. Persistindo os produtos da API.")
        persist_products(products)
    else:
        logging.info("Produtos já existem no banco de dados. Nenhuma ação necessária.")
