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
import csv
import os
import re

class Data:
    """
        structure of a single data pack to manipulate on
    """
    def __init__(self, DB, name):
        self.db = DB[name]

    def record(self, _id, _dict):
        self.db.update({'id': _id}, {'$set': _dict})

    def show(self, _id):
        return self.db.find_one({'id', _id})

class Db:
    """
        structure of a database
    """
    def __init__(self, address="10.2.2.39:27017"):
        client = MongoClient(address)
        self.DB = client['datas']

    def import_data(self, name, description=""):
        t = re.split('\.', name)
        if len(t) == 2 and t[-1] in ['csv','tsv']:
            # it's csv file

            try:
                coll = self.DB.create_collection(t[0])
                coll.insert({'_id': 'info', 'name':t[0], 'path':'~/data/'+name, 'description': description})
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
                        f[title[i]]=v[i]
                    coll.insert(f)
            except Exception as e:
                print e.message
                print 'Aborting...'

