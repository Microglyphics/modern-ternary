from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import text
from contextlib import contextmanager
import logging
import urllib.parse
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        load_dotenv()
        
        self.db_config = {
            'host': os.getenv('DB_HOST', '127.0.0.1'),
            'user': os.getenv('DB_USER', 'app_user'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'modernity_survey'),
            'port': int(os.getenv('DB_PORT', '3306'))
        }
        
        self._engine = None
        self._SessionLocal = None
        self._initialize()

    def _initialize(self):
        try:
            env = os.getenv('ENV', 'development')
            logger.info(f"Initializing database in {env} environment")
            
            encoded_password = urllib.parse.quote_plus(self.db_config['password'])
            
            if env == 'production':
                # Production: Use Unix socket
                connection_string = (
                    f"mysql+pymysql://{self.db_config['user']}:{encoded_password}"
                    f"@/{self.db_config['database']}?"
                    f"unix_socket=/cloudsql/modernity-worldview:us-central1:modernity-db"
                )
            else:
                # Development: Use TCP connection
                connection_string = (
                    f"mysql+pymysql://{self.db_config['user']}:{encoded_password}"
                    f"@{self.db_config['host']}:{self.db_config['port']}"
                    f"/{self.db_config['database']}"
                )
            
            logger.info(f"Connecting to MySQL using {env} configuration")
            
            self._engine = create_engine(
                connection_string,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            self._SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )
            
            # Test connection
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("Database connection successful")

        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise

    @contextmanager
    def get_session(self) -> Session:
        if not self._SessionLocal:
            raise RuntimeError("Database session factory not initialized")
            
        session = self._SessionLocal()
        try:
            yield session
        except Exception as e:
            session.rollback()
            logger.error(f"Session error: {str(e)}")
            raise
        finally:
            session.close()