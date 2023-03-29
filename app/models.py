from sqlalchemy import Column, Integer, String, Float, DateTime
from app.db import Base


class Users(Base):
    __tablename__ = "users"
    pk = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(String(100))
    pw = Column(String(100))
    email = Column(String(100))


class Books(Base):
    __tablename__ = "books"
    isbn = Column(String(100), primary_key=True)
    title = Column(String(100))
    authors = Column(String(100))
    contents = Column(String(1000))
    thumbnail = Column(String(1000))
    url = Column(String(1000))
    rate = Column(Float)
    reviewCount = Column(Integer)
    updatetime = Column(DateTime)


class Reviews(Base):
    __tablename__ = "reviews"
    pk = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(String(100))
    rate = Column(Float)
    like = Column(Integer)
    dislike = Column(Integer)
    isbn = Column(String(100))
    contents = Column(String(1000))


class Votes(Base):
    __tablename__ = "votes"
    pk = Column(Integer, primary_key=True, autoincrement=True)
    rK = Column(Integer)
    like = Column(Integer)
    id = Column(String(100))
