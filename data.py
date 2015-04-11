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
