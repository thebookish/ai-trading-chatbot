from sqlmodel import SQLModel, create_engine, Session
import os

DB_URL = os.environ.get("DB_URL", "sqlite:///./trading.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

def init_db():
    SQLModel.metadata.create_all(engine)

class DBSession:
    def __enter__(self):
        self.session = Session(engine)
        return self.session
    def __exit__(self, exc_type, exc, tb):
        self.session.close()
