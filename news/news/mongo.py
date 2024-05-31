import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["local"]

dblist = myclient.list_database_names()
collist = mydb.list_collection_names()

if "local" in dblist:
  print("The database exists.")

if "news" in collist:
  print("The collection exists.")