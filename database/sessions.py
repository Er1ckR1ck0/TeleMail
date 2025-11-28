from sqlmodel import Session, SQLModel, create_engine
from typing import Generator
from contextlib import contextmanager


class MySession:
    database: str = "database.db"
    driver: str = "sqlite"
    engine = None
    
    @classmethod
    def _init_engine(cls):
        if cls.engine is None:
            cls.engine = create_engine(
                f"{cls.driver}:///{cls.database}",
                echo=False,  
                connect_args={"check_same_thread": False}  # For SQLite
            )
        return cls.engine
    
    @classmethod
    @contextmanager
    def get_session(cls) -> Generator[Session, None, None]:
        cls._init_engine()
        session = Session(cls.engine)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
        
    @classmethod
    def create_db(cls):
        cls._init_engine()
        SQLModel.metadata.create_all(cls.engine)
    
    @classmethod
    @contextmanager
    def session_scope(cls) -> Generator[Session, None, None]:
        with cls.get_session() as session:
            yield session
        
    @classmethod
    def commit(cls, *args):
        with cls.get_session() as session:
            for obj in args:
                session.add(obj)
    
    @classmethod
    def execute(cls, query):
        with cls.get_session() as session:
            return session.exec(query).first()
    
    @classmethod
    def execute_all(cls, query):
        with cls.get_session() as session:
            return list(session.exec(query).all())


MySession._init_engine()