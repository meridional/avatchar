__author__ = 'ye'

from pymongo import MongoClient, ASCENDING, DESCENDING
import identicon
import datetime
import gridfs

client = None
db = None
user_collection = None
msg_collection = None
public_file_sys = None
secret_file_sys = None

def init_db(path):
  global client, db, user_collection, msg_collection, public_file_sys, secret_file_sys
  client = MongoClient(path)
  db = client.acdatabase
  user_collection = db.user_collection
  msg_collection = db.msg_collection
  msg_collection.ensure_index("datetime")
  public_file_sys = gridfs.GridFS(db, 'pf')
  secret_file_sys = gridfs.GridFS(db, 'sf')

#API

class User:
  def __init__(self, idx, name, secret_url=None, img_url = None):
    self.name = name
    self.secret_url = secret_url
    self.idx = idx
    self.img_url = img_url

  def getAvatar(self):
    return self.img_url

  @classmethod
  def from_record_id(cls, idx):
    r = user_collection.find_one({"_id":idx})
    return User(idx, r["name"], r["secret_id"], r["public_id"])


class Message:
  def __init__(self, idx, datetime, text, user):
    self.text = text
    self.user = user
    self.idx = idx
    self.datetime = datetime

  @classmethod
  def from_record_id(cls, idx):
    r = msg_collection.find_one({"_id":idx})
    return Message(idx, r["datetime"], r["content"], User.from_record_id(r["user_id"]))

  @classmethod
  def from_record(cls, r):
    return Message(r["_id"], r["datetime"], r["content"], User.from_record_id(r["user_id"]))





def insert_user(name):
  sf = secret_file_sys.new_file()
  identicon.genIdenticonFromStringIntoFile(sf, name, True, 180, 180)
  sf.close()

  pf = public_file_sys.new_file()
  identicon.genIdenticonFromStringIntoFile(pf, name, False, 60, 60)
  pf.close()
  idx = user_collection.insert({"name":name,
                                "secret_id":sf._id,
                                "public_id":pf._id})
  return User(idx, name, sf._id, pf._id)


def find_user(name):
  record = user_collection.find_one({"name" : name})
  if record:
    return User(record["_id"], name, record["secret_id"], record["public_id"])
  return None


def user_said_something(name, content):
  user = find_user(name)
  t = datetime.datetime.utcnow()
  record = msg_collection.insert({"user_id":user.idx, "content":content, "datetime":t})
  return Message(record._id, t, content, user)



def get_recent_messages(count=50):
  msgs = msg_collection.find(spec = {}, limit = count).sort("datetime", DESCENDING)
  return map(Message.from_record, msgs)