from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import ConfigHelper

from helpers.logger import ColoredLogger, LEVEL_MAPPING
import logging
from helpers.database.base import Base

from security.models.user import User
from security.models.refresh_token import RefreshToken
from security.models.project_versions import ProjectsVersion

config_app = ConfigHelper()
logger = ColoredLogger.get_logger(__name__, level=LEVEL_MAPPING.get(config_app.get_internal_log_level(), logging.INFO))

path_db = config_app.get_path_db()

# SQLite database initialization
DATABASE_URL = f"sqlite:///./{path_db}/data.db"
logger.info(f"Users database {DATABASE_URL}")

engine = create_engine(
    DATABASE_URL,
    connect_args={'check_same_thread': False}
)

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# User CRUD operations
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
