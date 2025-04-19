import os
import pymongo
from pymongo import MongoClient

from dotenv import load_dotenv
load_dotenv()

cluster = MongoClient(os.getenv("MONGO_URI"))

cluster = cluster.SupportBot
staff_db: pymongo.collection.Collection = cluster.Staff_db  # бд для стаффа
feedback_db: pymongo.collection.Collection = cluster.FeedBack_db  # отзывы
feedback_history: pymongo.collection.Collection = cluster.FeedBack_history  # истории отзывов для людей(в будущем)
not_verify: pymongo.collection.Collection = cluster.not_verify  # недопуск
vacation_db: pymongo.collection.Collection = cluster.vacation_db  # отпуска

support_db: pymongo.collection.Collection = cluster.Supports  # сапп статистика




