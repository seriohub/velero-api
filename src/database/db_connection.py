from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from configs.config_boot import config_app

from utils.logger_boot import logger

from database.base import Base

# Base.metadata.create_all creates tables based on the defined models
from models.db.user import User
from models.db.project_versions import ProjectsVersion
from models.db.refresh_token import RefreshToken

path_db = config_app.security.database_path

# SQLite database initialization
DATABASE_URL = f"sqlite:///./{path_db}/data.db"
logger.info(f"Users database {DATABASE_URL}")

engine = create_engine(
    DATABASE_URL,
    connect_args={'check_same_thread': False}
)

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Get DB for User CRUD operations
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
