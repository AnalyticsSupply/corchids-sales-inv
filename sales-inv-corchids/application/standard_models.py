'''
Created on Apr 12, 2017

@author: jason
'''
from google.appengine.ext import ndb

from werkzeug.security import generate_password_hash

class DBEntry(ndb.Model):
    conn_name = ndb.StringProperty(required=True)
    conn_string = ndb.StringProperty(required=True)
    conn_user = ndb.StringProperty(required=True)
    conn_pass = ndb.StringProperty(required=True)
    conn_host = ndb.StringProperty(required=True)
    conn_port = ndb.StringProperty(required=True)
    conn_database = ndb.StringProperty(required=True)
    
    def set_password(self, password):
        self.conn_pass = generate_password_hash(password)
    
    @classmethod  
    def get_connection_string(cls,dbtype):
        dbe = DBEntry.query(DBEntry.conn_name == dbtype).get()
        if dbe:
            ##  mysql+mysqldb://<user>:<password>@<host>[:<port>]/<dbname>
            #return dbe.conn_string+dbe.conn_user+":"+dbe.conn_pass+"@"+dbe.conn_host+":"+dbe.conn_port+"/"+dbe.conn_database
            dburl = dbe.conn_string+dbe.conn_user+":{}"+"@"+dbe.conn_host+dbe.conn_port+"/"+dbe.conn_database
            print(dburl)
            return dburl.format(dbe.conn_pass)
        else:
            db = DBEntry()
            db.conn_database = "x"
            db.conn_host = "x"
            db.conn_name = dbtype
            db.conn_pass = "x"
            db.conn_port = "x"
            db.conn_string = "x"
            db.conn_user = "x"
            db.put()
            return db

class UserModel(ndb.Model):
    username = ndb.StringProperty(required=True)
    pw_hash = ndb.StringProperty(required=True)        

class User:
    pw_hash = None
    username = None
    
    def __init__(self, user, pw):
        self.username = user
        self.set_password(pw)

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def get_model(self):
        return UserModel(username=self.username, pw_hash=self.pw_hash)
