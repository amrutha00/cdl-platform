import time
from app.db import get_db
from app.models.mongo import Mongo

class Goals(Mongo):
	def __init__(self):
		cdl_db = get_db()
		self.collection = cdl_db.goals

	def convert(self, goal_db):
		return Goal(
			goal_db["user_id"],
			goal_db["submission_id"],
			goal_db["extracted_goals"],
			last_updated=goal_db["last_updated"],
			id=goal_db["_id"]
		)

	def insert(self, goal):
		goal = self.collection.insert_one({
			"user_id": goal.user_id,
			"submission_id": goal.submission_id,
			"extracted_goals": goal.extracted_goals,
			"last_updated": goal.last_updated,
		})
		return goal.inserted_id


class Goal:
	def __init__(self, user_id, submission_id, extracted_goals, last_updated=time.time(), id=None):
		self.id = id
		self.user_id = user_id
		self.submission_id = submission_id
		self.extracted_goals = extracted_goals
		self.last_updated = last_updated
