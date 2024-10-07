import os, random, string, requests
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()



development = os.getenv("DEV_env")
event_date = "2024-10-07"
db = MongoClient(os.getenv("MONGO_URI"))["Database"]
tokendb = db.get_collection("tickets")
userdb =db.get_collection("users")
configdbc = db.get_collection("config").find_one({"id":87})
authToken = os.getenv("AUTH_TOKEN")
erl = configdbc.get("erl")



def delete_unused_tickets():
    tokendb.delete_many({"status": "valid"})

def delete_used_tickets():
    tokendb.delete_many({"status": "used"})

def delete_all_tickets():
    tokendb.delete_many({})
    
def log(message:str):
    obj = {"content" : message}
    requests.post(erl, json=obj)




class Ticket:
    def __init__(self, obj:dict) -> None:
        self.name = obj.get("name")
        self.email = obj.get("email")
        self.token = obj.get("token") or self.get_token()
        self.status = obj.get("status") or "valid"


    def get_token(self):
        token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        if not tokendb.find_one({"token": token}):
            return token
        return self.get_token()


    def save(self):
        ticket = Ticket(self.json)
        tokendb.insert_one(self.json)
        print("Updated ticket: ", ticket.token)
        return self


    @property
    def json(self):
        return {
            "name": self.name,
            "email": self.email,
            "token": self.token,
            "status": self.status
        }

class Event:
    def __init__(self) -> None:
        self.date = event_date
        self._tickets = []

    
    @property
    def tickets(self):
        if self._tickets:
            return self._tickets
        ticks = tokendb.find({})
        self._tickets = [Ticket(t) for t in ticks]
        return self._tickets
    

    def add_ticket(self, ticket:Ticket):
        ticket.save()
        return self
    
    @property
    def tickSold(self):
        return len(self.tickets)
    

class Admin:
    def __init__(self, obj:dict) -> None:
        self.username = obj.get("name")
        self.password = obj.get("password")
        self.email = obj.get("email")
        self.token = obj.get("token") or "invalid"

    def to_dict(self):
        return {
            "name": self.username,
            "email": self.email,
            "password": self.password,
            "token": self.token
        }

def is_manager(token:str=None) -> bool | Admin:
    data = userdb.find_one({"token": token or "invalid"})
    if data:return Admin(data)
    return False
