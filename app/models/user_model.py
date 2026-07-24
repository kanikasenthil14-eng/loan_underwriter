from bson import ObjectId
from flask_login import UserMixin
from app import mongo, login_manager

class UserModel(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.name = user_data.get('name', '')
        self.email = user_data.get('email', '')
        self.role = user_data.get('role', 'customer')
        self.mobile = user_data.get('mobile', '')

    def is_admin(self):
        return self.role == 'admin'

@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return UserModel(user_data)
    except Exception:
        pass
    return None
