from sqlalchemy.sql.sqltypes import Date
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Boolean, URL, t

Base = declarative_base()

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(40), nullable=False)
    last_name = Column(String(40), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    phone = Column(String(20), nullable=False, unique=True)
    birthday = Column(Date)
    data =  Column(String(250))
    created_at = Column('created_at', DateTime, default=func.now(), nullable=True)
    updated_at = Column('updated_at', DateTime, default=func.now(), onupdate=func.now(), nullable=True)
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    user = relationship('User', backref="contacts")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column('created_at', DateTime, default=func.now(), nullable=True)
    updated_at = Column('updated_at', DateTime, default=func.now(), onupdate=func.now(), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    avatar = Column(String, nullable=True)
    confirmed = Column(Boolean, default=False)






class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    avatar = Column(String, nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(Integer, default=3)
    refresh_token = Column(String(255), nullable=True)
    created_at = Column('created_at', DateTime, default=func.now(), nullable=True)
    updated_at = Column('updated_at', DateTime, default=func.now(), onupdate=func.now(), nullable=True)


class Ban(Base):
    __tablename__ = "bans"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    created_ban = Column('created_ban', DateTime, default=func.now(), nullable=True)
    end_of_the_ban = Column('end_of_the_ban', DateTime, default=None, nullable=True)


class Photo(Base):
    __tablename__ = "photos"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    created_at = Column('created_at', DateTime, default=func.now(), nullable=True)
    updated_at = Column('updated_at', DateTime, default=func.now(), onupdate=func.now(), nullable=True)
    photo = Column(URL)
    description = Column(String, nullable=True)


class Comments(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    photo_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    comment = Column(String(255), nullable=False)