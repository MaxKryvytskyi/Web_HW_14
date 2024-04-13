from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decouple import config

engine = create_engine(config('SQLALCHEMY_DATABASE_URL_F'))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
