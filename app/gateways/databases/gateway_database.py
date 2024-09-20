from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base

from gateways.databases.connection import session

Base = declarative_base()


def save(entity: Base):
    if not isinstance(entity, Base):
        raise TypeError("entity must be an instance of Base")

    try:
        session.add(entity)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error saving entity: {e}")
        raise


def update(entity: Base):
    if not isinstance(entity, Base):
        raise TypeError("entity must be an instance of Base")

    try:
        session.merge(entity)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error updating entity: {e}")
        raise


def save_all(entities):
    if not isinstance(entities, list):
        entities = [entities]

    if not all(isinstance(entity, Base) for entity in entities):
        raise TypeError("all entities must be instances of Base")

    try:
        for entity in entities:
            session.add(entity)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error saving entities: {e}")
        raise
