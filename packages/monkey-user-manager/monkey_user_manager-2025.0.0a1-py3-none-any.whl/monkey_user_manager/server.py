import sqlite3 as sql
import json
from bottle import Bottle,request,response,run
import base64
import os
import uuid

def getid(length=16):
    unique_id = uuid.uuid4()
    random_bytes = os.urandom(8)
    combined_data = unique_id.bytes + random_bytes
    encoded = base64.urlsafe_b64encode(combined_data).decode('utf-8')
    return encoded.rstrip('=')[:length]
class UsersManager:
    NT=Bottle()
    def __init__(self,port,quiet=False,debug=True):
        self.quiet=True
        self.debug=debug
        self.port=port
        self.user_db=sql.connect('users.db')
        self.cursor = self.user_db.cursor()
        try:
            self.cursor.execute('''
            CREATE TABLE users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            getid TEXT,
            userfile TEXT UNIQUE NOT NULL
            )''')
        except:
            pass
    def Post_json(self,json):
        print(json)
    def Get_json(self,json):
        print(json)
    @NT.get("/")
    def GET_handle(self):
        response.content_type = 'application/json'
        return_=self.Get_json(dict(request.params))
        return return_
    def POST_handle(self):
        response.content_type = 'application/json'
        return_=self.Post_json(request.json)
        return return_
    def __call__(self):
        @self.NT.get("/")
        def GET():
            return self.GET_handle()
        @self.NT.post("/")
        def POST():
            return self.POST_handle()
        run(app=self.NT,port=self.port,host="0.0.0.0",quiet=self.quiet)
if __name__=='__main__':
    test=UsersManager(5000)
    test()
