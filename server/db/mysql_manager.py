# server/db/mysql_manager.py
from typing import Optional, Dict, Any
import os
from contextlib import contextmanager
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
from dotenv import load_dotenv
import urllib.parse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    _instance = None
    _engine = None
    _SessionLocal = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize database connection and session factory."""
        load_dotenv()
        
        # Basic configuration
        self.db_config = {
            'host': os.getenv('DB_HOST', '35.222.251.0'),
            'user': os.getenv('DB_USER', 'app_user'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'modernity_survey'),
            'port': int(os.getenv('DB_PORT', '3306'))
        }

        logger.info(f"Initializing database connection to {self.db_config['host']}")
        self._create_engine()

    def _create_engine(self) -> None:
        """Create SQLAlchemy engine with direct connection."""
        try:
            encoded_password = urllib.parse.quote_plus(self.db_config['password'])
            
            connection_string = (
                f"mysql+pymysql://{self.db_config['user']}:{encoded_password}"
                f"@{self.db_config['host']}:{self.db_config['port']}"
                f"/{self.db_config['database']}"
                "?charset=utf8mb4"
            )
            
            # Log connection info (without password)
            logger.info(f"Connecting to MySQL at {self.db_config['host']}:{self.db_config['port']}")
            
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
                result = conn.execute(text("SELECT 1"))
                logger.info("Database connection successful")
                
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise

    @contextmanager
    def get_session(self) -> Session:
        """Get a database session using context manager."""
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

# Global instance
db_manager = DatabaseManager()