import os
import psutil
import random
import string
import requests
from flask import  request, Request
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()


development = os.getenv("DEV_env")
db = MongoClient(os.getenv("MONGO_URI"))["Database"]
tokendb = db.get_collection("tickets")
userdb =db.get_collection("users")
configdb = db.get_collection("config")
configdbc = dict(configdb.find_one({"id":87}))
authToken = os.getenv("AUTH_TOKEN")
erl = configdbc.get("erl")
def log(message:str, *args):
    obj = {"content" : message}
    requests.post(erl, json=obj)


def event_date(date:str=None):
    if date:configdb.update_one({"id": 87}, {"$set": {"event_date": date}})
    else:date = configdb.find_one({"id":87}).get("event_date")
    configdbc["event_date"] = date
    return date

def delete_unused_tickets():
    tokendb.delete_many({"status": "valid"})
    log("Deleted all unused tickets")

def delete_used_tickets():
    tokendb.delete_many({"status": "used"})
    log("Deleted all used tickets")

def delete_all_tickets():
    tokendb.delete_many({})
    log("Deleted all tickets")

def get_ip(req:Request=request):
    return req.headers.get("X-Forwarded-For", request.remote_addr)

class Ticket:
    def __init__(self, obj:dict) -> None:
        self.name = obj.get("name")
        self.gender = obj.get("gender")
        self.email = obj.get("email")
        self.token = obj.get("token") or self.get_token()
        self.status = obj.get("status") or "valid"
        self.valid = self.status == "valid"


    def get_token(self):
        token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        if not tokendb.find_one({"token": token}):
            return token
        return self.get_token()


    def save(self):
        ticket = Ticket(self.json)
        tokendb.insert_one(self.json)
        if event: event.add_ticket(ticket)
        
        return self


    @property
    def json(self):
        return {
            "name": self.name,
            "email": self.email,
            "gender": self.gender,
            "token": self.token,
            "status": self.status
        }

class Event:
    def __init__(self) -> None:
        self._tickets = dict()
        self._date:str = configdbc.get("event_date")


    def total_tickets(self):
        _count =  tokendb.count_documents({})
        return _count


    def date(self, date:str=None):
        return event_date(date)
    

    def tickets(self) -> dict:
        self._tickets = {tick.get("token"): Ticket(tick) for tick in tokendb.find({})} # mo
        self._total_tickets = len(self._tickets)
        return self._tickets
    
    def update_ticket(self, token:str, status:str):
        tokendb.update_one({"token": token}, {"$set": {"status": status}})
        return self

    def add_ticket(self, ticket:Ticket):
        self._tickets[ticket.token] = ticket
        return self

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
    return None

def authorised():
    return is_manager(request.cookies.get("token"))

def system():
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    detail = f"""
    ```
    Total RAM : {memory.total / (1024**3):.2f} GB
    CPU Cores : {psutil.cpu_count(logical=False)}
    CPU Usage : {cpu_usage}%
    RAM Usage : {memory.used//10**6} MB({memory.percent}%) | {psutil.Process(os.getpid()).memory_info().rss//2**20}MB
    Total Disk: {disk.total//10**9} GB
    Disk Usage: {disk.used//10**9} GB({disk.percent}%)
    ```
    """
    return detail


event = Event()


