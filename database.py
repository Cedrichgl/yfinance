from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

#url
DATABASE_URL = "postgresql://postgres:MonMotDePasse@localhost:5432/yfinance"

#moteur
engine = create_engine(DATABASE_URL)


#Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#La class declarative
class Base(DeclarativeBase):
    pass


#fonction de session
def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()

