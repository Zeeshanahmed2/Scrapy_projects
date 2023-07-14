# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from sqlalchemy.orm import sessionmaker
from crime_inmate.crime_inmate.models import InmateModel
from crime_inmate.crime_inmate import engine

class DatabasePipeline:
    def __init__(self):
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()
        inmate_model = InmateModel(**item)
        session.add(inmate_model)
        session.commit()
        session.close()
        return item
