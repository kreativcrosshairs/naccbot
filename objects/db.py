from pymongo import MongoClient


class DBHelper(object):
    def __init__(self, db_uri):
        client = MongoClient(db_uri)
        self.db = client.naccbot

    def create_user(self, user_body):
        self.db.users.insert_one(user_body)

    def read_user(self, user_id):
        return self.db.users.find_one({
            'user_id': user_id
        })

    def update_user(self, user_id, update_body):
        self.db.users.find_one_and_update({
            'user_id': user_id
        }, {
            '$set': update_body
        })
