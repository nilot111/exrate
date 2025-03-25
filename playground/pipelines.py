# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId


class PlaygroundPipeline:
    def process_item(self, item, spider):
        return item


class MongoDBPipeline:
    def __init__(self, mongo_uri, mongo_db, mongo_collection):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection
        self.client = None
        self.db = None
        self.dolar_id = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'exchange_rates'),
            mongo_collection=crawler.settings.get('MONGO_COLLECTION', 'rates')
        )

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        # Check if the dolar document exists
        dolar_doc = self.db[self.mongo_collection].find_one({"repmodel": "dolar"})
        if not dolar_doc:
            # Create initial document if it doesn't exist
            initial_doc = {
                "repmodel": "dolar",
                "brand": "dolar",
                "images": {
                    "urls": ["/img/dolar.png"]
                },
                "categories": {
                    "level1": "dolar",
                    "level2": "dolar",
                    "level3": "dolar"
                },
                "skus": []
            }
            result = self.db[self.mongo_collection].insert_one(initial_doc)
            self.dolar_id = result.inserted_id
        else:
            self.dolar_id = dolar_doc["_id"]

    def close_spider(self, spider):
        # Get all SKUs and sort them by price_card in descending order
        doc = self.db[self.mongo_collection].find_one({"_id": self.dolar_id})
        if doc and "skus" in doc:
            # Sort SKUs by price_card in descending order
            sorted_skus = sorted(doc["skus"], key=lambda x: x["price_card"], reverse=True)
            # Update the document with sorted SKUs
            self.db[self.mongo_collection].update_one(
                {"_id": self.dolar_id},
                {"$set": {"skus": sorted_skus}}
            )
        self.client.close()

    def process_item(self, item, spider):
        # Create new SKU
        new_sku = {
            "store": item['name'],
            "price_card": item['buy_rate'],
            "price": item['sell_rate'],
            "updated": item['timestamp'],
            "url": item['link']
        }

        # First, remove any existing SKU with the same store
        self.db[self.mongo_collection].update_one(
            {"_id": self.dolar_id},
            {"$pull": {"skus": {"store": item['name']}}}
        )

        # Then, add the new SKU
        self.db[self.mongo_collection].update_one(
            {"_id": self.dolar_id},
            {"$push": {"skus": new_sku}}
        )

        return item
