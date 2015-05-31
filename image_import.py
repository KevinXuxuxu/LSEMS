# use UTP-8 #
"""
    Example of self-defined data import
    iterator. This is for importing image set.
"""

__author__ = "Xu Fangzhou"
__email__ = "kevin.xu.fangzhou@gmail.com"

import os

def random_id():
    from random import randint
    r = randint(0,56**10)
    rtn = ""
    for i in range(0,10):
        ri = r % 56
        r /= 56
        if ri+48>57: ri+=7
        if ri+48>90: ri+=6
        rtn += chr(ri+48)
    return rtn

class ImageSet:

    def __init__(self, name, _type):
        self.name = name
        self.type = _type
        if name not in os.listdir('.'):
            raise Exception("No such image set in dir: "+os.getcwd())
        self.name_list = []
        for name in os.listdir(name):
            if not name.startswith('.'):
                self.name_list.append(name)
        self.i = 0
        self.n = len(self.name_list)


    def __iter__(self):
        return self

    def next(self):
        d = {}
        if self.i < self.n:
            i = self.i
            self.i += 1
            d['name'] = self.name_list[i]
            d['type'] = self.type
            d['id'] = random_id()
            return d
        else:
            raise StopIteration()
