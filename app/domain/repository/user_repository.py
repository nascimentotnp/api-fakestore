import logging
import secrets
import time
from datetime import datetime


from authentication.jwt_auth import hash_password
from domain.entity.entities import User
from gateways.databases.connection import session


def create_user(user_data):
    existing_user = read_user_by_username(user_data['username'])
    if existing_user:
        raise ValueError("Username already registered")

    existing_user = read_user_by_email(user_data['email'])
    if existing_user:
        raise ValueError("Email already registered")

    api_token = secrets.token_urlsafe(32)
    api_token_ts = int(time.time())
    try:
        new_user = User(
            email=user_data['email'],
            username=user_data['username'],
            password=user_data['password'],
            firstname=user_data.get('firstname'),
            lastname=user_data.get('lastname'),
            address=user_data.get('address'),
            phone=user_data.get('phone'),
            gender=user_data.get('gender'),
            api_token=api_token,
            api_token_ts=api_token_ts,
            created_at=datetime.now(),
            active=True
        )

        session.add(new_user)
        session.commit()
        return new_user

    except Exception as e:
        session.rollback()
        logging.error(f'Erro ao criar o usuário: {e}')
        raise


def read_all_users():
    return session.query(User).all()


def read_active_users():
    return session.query(User).filter(User.active).all()


def read_user_by_id(user_id):
    return session.query(User).filter(User.id == user_id).first()


def read_user_by_username(username):
    return session.query(User).filter(User.username == username).first()


def read_user_by_email(email):
    return session.query(User).filter(User.email == email).first()


def update_password(user_id, **kwargs):
    user = session.query(User).get(user_id)
    if not user:
        logging.error(f'Usuário com ID {user_id} não encontrado.')
        return

    for key, value in kwargs.items():
        if key == 'password':
            value = hash_password(value)  # Certifique-se de que isso está chamando seu método de hashing
        setattr(user, key, value)

    try:
        session.commit()
        logging.info(f'Senha do usuário com ID {user_id} atualizada com sucesso.')
    except Exception as e:
        session.rollback()
        logging.error(f'Erro ao atualizar a senha: {e}')


def delete_user(user_id):
    user = session.query(User).get(user_id)
    if not user:
        logging.error(f'Usuário com ID {user_id} não encontrado.')
        return

    user.active = False
    session.commit()
