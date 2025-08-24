# extensions.py
from pymongo import MongoClient
import certifi
from config import Config

db_client = MongoClient(
    Config.MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where()
)
db = db_client["oncoVisionDB"]
