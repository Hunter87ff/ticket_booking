import os, random, string
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()



development = os.getenv("DEV_env")
event_date = "2024-10-23"
db = MongoClient(os.getenv("MONGO_URI"))["Database"]
tokendb = db.get_collection("tickets")
userdb =db.get_collection("users")
authToken = os.getenv("AUTH_TOKEN")

class Ticket:
    def __init__(self, obj:dict) -> None:
        self.name = obj.get("name")
        self.email = obj.get("email")
        self.token = obj.get("token") or self.get_token()


    def get_token(self):
        token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        if not tokendb.find_one({"token": token}):
            return token
        return self.get_token()


    def save(self) -> bool:
        ticket = Ticket(self.json)
        tokendb.insert_one(self.json)
        print("Updated ticket: ", ticket.token)


    @property
    def json(self):
        return {
            "name": self.name,
            "email": self.email,
            "token": self.token,
            "status": "valid"
        }
    
    
def is_manager(token:str):
    return bool(userdb.find_one({"token": token})) 