from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config import DB_OPTION

DB_URL = f"mysql+pymysql://{DB_OPTION['user']}:{DB_OPTION['pw']}@{DB_OPTION['url']}/{DB_OPTION['database']}?charset=utf8"
engine = create_engine(DB_URL, pool_recycle=3600, pool_size=10, encoding="utf-8")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
