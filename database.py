from sqlalchemy import Column, create_engine, Integer, Boolean,String,Float
from sqlalchemy import Column, create_engine, Integer, Boolean
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.orm import Session

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
    gender = Column(String ) #Пол
    height = Column(Integer) #Рост
    chest = Column(Integer ) #Обхват груди
    waist = Column(Integer) #Талия
    hips = Column(Integer ) #Бёдра
    shoulder_width = Column(Integer) #ширина плучь
    len_arm = Column(Integer ) #Длинна рук


SessionLocal = sessionmaker(autoflush=False,bind=engine)

def get_db():
    db:Session = SessionLocal()
    return db