from sqlalchemy import create_engine
from sqlmodel import Session

from app.core.settings import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, echo=False)


def get_session() -> Session:
    return Session(engine)
