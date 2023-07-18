from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey

Base = declarative_base()


class InmateModel(Base):
    __tablename__ = 'maine_inmates'

    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    first_name = Column(String)
    middle_name = Column(String)
    last_name = Column(String)
    suffix = Column(String)
    birthdate = Column(String)
    sex = Column(String)
    race = Column(String)
    md5_hash = Column(String)
    data_source_url = Column(String)
    arrests = relationship("ArrestsModel", back_populates="inmate")


class ArrestsModel(Base):
    __tablename__ = 'maine_arrests'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    inmate_id = Column(BigInteger, ForeignKey('maine_inmates.id'))
    status = Column(String(255))
    officer = Column(String(255))
    booking_agency = Column(String(255))
    md5_hash = Column(String)
    data_source_url = Column(String(255))
    inmate = relationship("InmateModel", back_populates="arrests")

