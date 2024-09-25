import os

from flask.cli import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

db_engine = os.getenv('DB_ENGINE')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

# connection_db_url = f'{db_engine}://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
connection_db_url = 'postgresql://postgres:root@appstore-db:5432/sale'

engine = create_engine(connection_db_url, pool_pre_ping=True, echo=False, pool_size=50, max_overflow=100, pool_timeout=60)

Session = sessionmaker(bind=engine)
session = Session()
