import logging
from sqlalchemy.exc import SQLAlchemyError
from domain.entity.entities import Product
from gateways.databases.connection import session


def create_products(product_id, title, price, description, category, image, rating_rate, rating_count):
    if read_products_by_id(product_id):
        logging.info(f'Produto {title} já existe no banco.')
        return False

    new_product = Product(
        title=title,
        price=price,
        description=description,
        category=category,
        image=image,
        rating_rate=rating_rate,
        rating_count=rating_count,
        active=True
    )
    session.add(new_product)
    session.commit()
    return True


def read_all_products():
    return session.query(Product).all()


def read_active_products():
    return session.query(Product).filter(Product.active.is_(True)).all()


def read_products_by_id(product_id):
    return session.query(Product).filter(Product.id == product_id, Product.active.is_(True)).first()


def update_products(product_id, **kwargs):
    product = session.query(Product).get(product_id)
    if not product:
        logging.warning(f'Produto {product_id} não encontrado para atualização.')
        return False

    for key, value in kwargs.items():
        setattr(product, key, value)

    session.commit()
    return True


def update_product_price(product_id, price):
    product = session.query(Product).get(product_id)
    if not product:
        logging.warning(f'Produto {product_id} não encontrado para atualização.')
        return False

    product.price = float(price)
    session.commit()
    return True


def delete_products(product_id):
    product = session.query(Product).get(product_id)
    if not product:
        logging.warning(f'Produto {product_id} não encontrado para exclusão.')
        return False

    product.active = False
    session.commit()
    return True


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
                    title=product_data['title'],
                    price=product_data['price'],
                    description=product_data['description'],
                    category=product_data['category'],
                    image=product_data['image'],
                    rating_rate=product_data['rating']['rate'],
                    rating_count=product_data['rating']['count'],
                    active=True
                )
                session.add(new_product)
        session.commit()
        logging.info("Produtos persistidos com sucesso.")
    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f"Ocorreu um erro ao persistir os produtos: {e}")
        return False
    finally:
        session.close()


def initialize_products_if_empty(products):
    existing_product = session.query(Product).first()
    logging.info("Verificando se existem produtos no banco de dados.")

    if existing_product is None:
        logging.info("Nenhum produto encontrado no banco de dados. Persistindo os produtos da API.")
        if not products:
            logging.warning("Nenhum produto retornado da API para persistir.")
            return
        persist_products(products)
    else:
        logging.info("Produtos já existem no banco de dados. Nenhuma ação necessária.")

