from motor.motor_asyncio import AsyncIOMotorCollection
from models import User, UserCreate
from database import get_database
from bson import ObjectId
from typing import Optional
from password_utils import get_password_hash

class UserRepository:
    def __init__(self):
        self.collection_name = "users"
    
    @property
    def collection(self) -> AsyncIOMotorCollection:
        return get_database()[self.collection_name]
    
    async def create_user(self, user_data: UserCreate) -> User:
        existing_user = await self.collection.find_one({
            "$or": [
                {"username": user_data.username},
                {"email": user_data.email}
            ]
        })
        
        if existing_user:
            raise ValueError("Користувач з таким username або email вже існує")

        hashed_password = get_password_hash(user_data.password)

        user_dict = {
            "username": user_data.username,
            "email": user_data.email,
            "hashed_password": hashed_password,
            "is_active": True
        }
        
        result = await self.collection.insert_one(user_dict)

        created_user = await self.collection.find_one({"_id": result.inserted_id})
        created_user["_id"] = str(created_user["_id"])
        return User(**created_user)
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        user_doc = await self.collection.find_one({"username": username})
        if user_doc:
            user_doc["_id"] = str(user_doc["_id"])
            return User(**user_doc)
        return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        user_doc = await self.collection.find_one({"email": email})
        if user_doc:
            user_doc["_id"] = str(user_doc["_id"])
            return User(**user_doc)
        return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        try:
            user_doc = await self.collection.find_one({"_id": ObjectId(user_id)})
            if user_doc:
                user_doc["_id"] = str(user_doc["_id"])
                return User(**user_doc)
            return None
        except:
            return None

user_repository = UserRepository()