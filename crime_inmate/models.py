from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

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
    data_source_url = Column(String)