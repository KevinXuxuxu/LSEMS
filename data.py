# use UTF-8 #
"""
    THis script is to manage experiment data,
    including record infos for new data pack,
    fetching data for experiments, etc.
"""

__author__ = "Xu Fangzhou"
__email__ = "kevin.xu.fangzhou@gmail.com"

from json import *
from pymongo import *
from pandas import *
import csv
import os
import re

class Data:
    """
        structure of a single data set to manipulate on
    """
    def __init__(self, Database, name):
        self.Database = Database
        self.db = Database.DB[name]
        self.name = name

    def record(self, _id, _dict):
        self.db.update({'id': _id}, {'$set': _dict})

    def show(self, _id):
        return self.db.find_one({'id': _id})

    def find_parent(self):
        info = self.db.find_one({'_id': 'info'})
        if info.has_key('parent') and info['parent'] != "":
            return info['parent']
        return None

    def find_root(self):
        info = self.db.find_one({'_id': 'info'})
        if info.has_key('parent') and info['parent'] != "":
            return self.Database.get_data(info['parent']).find_root()
        return self.name

    def show_all(self):
        rtn = []
        for i in self.db.find():
            rtn.append(i)
        return rtn

class Database:
    """
        structure of a database
    """
    def __init__(self, db="datas", address="10.2.2.137:27017"):
        client = MongoClient(address)
        self.DB = client[db]

    def import_data(self, name, description="", parent="", ignore=[]):
        if self.DB.name != 'datas':
            print "should not import data into db other than 'datas'!"
            return
        t = re.split('\.', name)
        if len(t) == 2 and t[-1] in ['csv','tsv']:
            # it's csv or tsv file
            try:
                coll = self.DB.create_collection(t[0])
                if parent != "" and parent not in self.DB.collection_names():
                    raise Exception("parent data set not in DB!")
                coll.insert({'_id': 'info',
                            'name':t[0],
                            'type':t[-1],
                            'path':'~/sandbox/data/'+name,
                            'description': description,
                            'parent': parent})
                fp = open(name)
                if t[-1]=='csv': r = csv.reader(fp)
                else:
                    r = csv.reader(fp, delimiter='\t', quoting=csv.QUOTE_ALL)
                title = r.next()
                if 'id' not in title:
                    raise Exception("no id attribute!")
                for v in r:
                    if len(v) == 0: break
                    f = {}
                    for i in range(len(title)):
                        if title[i] not in ignore:
                            f[title[i]]=v[i]
                    coll.insert(f)
            except Exception as e:
                print e.message
                print 'Aborting...'
        # other type to be added

    def generate_data(self, name, description="", parent="", ignore=[]):
        if name not in os.listdir('.'):
            print "no such data set to register: "+name
            return
        os.system("cp %s ~/sandbox/data/" %name)
        self.import_data(name, description, parent, ignore)

    def join(self, name, name_list=[], key='_id'):
        rtn = self.get_data(name).show_all()
        for i in range(0,len(rtn)):
            try:
                value = rtn[i][key]
                for n in name_list:
                    b = self.get_data(n).db.find_one({key:value})
                    if b:
                        for p in b.items():
                            if not rtn[i].has_key(p[0]):
                                rtn[i][p[0]] = p[1]
            except Exception as e:
                print e
        return rtn

    def get_data(self, name):
        return Data(self, name)

class View:
    """
        providing joined view for datasets in database.
    """
    def __init__(self, database, name, name_list=[], key="_id"):
        self.database = database
        self.prim_ds = self.database.get_data(name)
        self.name = name
        self.name_list = name_list
        self.key = key

    def get(self, pair):
        rtn = self.prim_ds.db.find_one(pair)
        for name in self.name_list:
            b = self.database.get_data(name).db.find_one({self.key:rtn[self.key]})
            if b:
                for p in b.items():
                    if not rtn.has_key(p[0]):
                        rtn[p[0]] = p[1]
        return rtn

    def dump(self):
        return self.database.join(self.name, self.name_list, self.key)

    def dump_df(self):
        return DataFrame(self.dump()[1:])
