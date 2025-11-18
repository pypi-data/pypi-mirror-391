# session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()


class DB:
    engine = None
    Session = None
    session = None


db = DB()   # ВСЕ модули будут использовать ОДИН ОБЪЕКТ


def init_db(cfg: dict):
    engine = cfg.get("engine", "sqlite")

    # --- SQLite ---
    if engine == "sqlite":
        path = cfg.get("path", "pycells.db")
        url = f"sqlite:///{path}"

    # --- Postgres ---
    elif engine == "postgres":
        user = cfg.get("user", "")
        password = cfg.get("password", "")
        host = cfg.get("host", "localhost")
        port = cfg.get("port", 5432)
        dbname = cfg.get("dbname", "postgres")
        url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

    else:
        raise ValueError(f"Unsupported engine: {engine}")

    # создаём движок
    db.engine = create_engine(url, echo=False)

    # создаём таблицы
    Base.metadata.create_all(db.engine)

    # создаём фабрику сессий
    db.Session = sessionmaker(bind=db.engine)

    # создаём первую сессию
    db.session = db.Session()

    return db.session
