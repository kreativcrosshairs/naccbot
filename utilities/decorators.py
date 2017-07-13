def sync_db(func):
    def wrapper(self, bot, update):
        user_id = update.message.from_user.id
        user = self.db.read_user(user_id)
        if not user:
            user_body = {
                'user_id': user_id,
                'first_name': update.message.from_user.first_name,
                'last_name': update.message.from_user.last_name,
                'username': update.message.from_user.username
            }
            self.db.create_user(user_body)
        func(self, bot, update)

    return wrapper
