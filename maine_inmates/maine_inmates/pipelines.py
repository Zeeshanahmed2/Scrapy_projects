# Define your item pipeline here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
# useful for handling different item types with a single interface

from itemadapter import ItemAdapter
from sqlalchemy.orm import sessionmaker
from maine_inmates.maine_inmates.models import InmateModel, ArrestsModel
from maine_inmates.maine_inmates.database import engine


class DatabasePipeline:
    def __init__(self):
        self.Session = sessionmaker(bind=engine)
        self.last_inserted_id = None
        self.spider = None

    def open_spider(self, spider):
        spider.myPipeline = self

    def close_spider(self, spider):
        pass

    # def process_item(self, item, spider):
    #     session = self.Session()
    #     inmate_model = InmateModel(**item.get('inmates_data_hash'))
    #     session.add(inmate_model)
    #     session.commit()
    #     inmate_id = inmate_model.id
    #     arrests_model = ArrestsModel(**item.get('arrests_data_hash'))
    #     arrests_model.inmate_id = inmate_id
    #     session.add(arrests_model)
    #     session.commit()
    #     session.close()
    #     return item

    def process_item(self, item, spider):
        session = self.Session()
        parent = InmateModel(**item.get('inmates_data_hash'))
        child = ArrestsModel(**item.get('arrests_data_hash'))
        parent.arrests = [child]
        session.add(parent)
        session.commit()
        session.close()
        return item

    def get_last_inserted_id(self):
        return self.last_inserted_id
