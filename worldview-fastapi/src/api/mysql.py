# src/lib/db/mysql.py
import mysql.connector
from mysql.connector import Error
import logging

def get_db_config():
    try:
        config = {
            'unix_socket': '/cloudsql/modernity-worldview:us-central1:modernity-db',
            'user': 'app_user',
            'password': '9pQK?fJF.9Lm]nv;',
            'database': 'modernity_survey'
        }
        return config
    except Exception as e:
        logging.error(f"Error in database configuration: {e}")
        raise