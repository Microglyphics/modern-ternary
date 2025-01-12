# src/database/db.py
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import os

def get_db_connection():
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')
    
    connection_string = f'mysql+pymysql://{db_user}:{quote_plus(db_pass)}@{db_host}:{db_port}/{db_name}'
    return create_engine(connection_string)