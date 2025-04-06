from sqlalchemy import Column, create_engine, Integer, Boolean
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQL_URL = "sqlite:///./app_sql.db"
engine = create_engine(
    SQL_URL, 
    connect_args={"check_same_thread": False}
    )

class Base(DeclarativeBase): pass

class Person(Base):
    __tablename__="People"

    id = Column(
        Integer, 
        primary_key=True, 
        index=True
        )
    photo = Column(Boolean)

SessionLocal = sessionmaker(autoflush=False,bind=engine)

