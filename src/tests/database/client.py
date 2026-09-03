from pymongo import MongoClient

from conftest import TEST_MONGO_URI

client = MongoClient(TEST_MONGO_URI, serverSelectionTimeoutMS=1000)
