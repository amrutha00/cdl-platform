import time
from app.db import get_db
from app.models.mongo import Mongo

class SearchLogs(Mongo):
	def __init__(self):
		db = get_db()
		self.collection = db.search_logs

	def convert(self, sl_db):
		return SearchLog(
			sl_db["user_id"],
			time = sl_db["time"],
			source = sl_db["source"],
			filters = sl_db["filters"],
			context = sl_db["context"],
			intent = sl_db["intent"],
			id=sl_db["_id"]
		)

	def insert(self, searchlog):
		inserted = self.collection.insert_one({
			"user_id": searchlog.user_id,
			"time": searchlog.time,
			"source": searchlog.source,
			"filters": searchlog.filters,
			"context": searchlog.context,
			"intent": searchlog.intent
		})
		return inserted.inserted_id


class SearchLog:
	def __init__(self, user_id, time=time.time(), source={}, context={}, intent={}, filters={}, id=None):
		self.id = id
		self.user_id = user_id
		self.time=time
		self.source=source
		self.filters=filters
		self.context=context
		self.intent=intent
