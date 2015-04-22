# use UTF-8#
"""
    This is an API for experiment codes in Python
    to generate formated output file for the system.
"""

__author__ = "Xu Fangzhou"
__enail__ = "kevin.xu.fangzhou@gmail.com"

import json
import re
import sys
import os

class Outer:
    lines = []
    dicts_dp = []
    dict_exp = {}

    def __init__(self, file_name = "output"):
        self.fn = file_name

    def nout(self, content):
        """
            non json outputs, takes plain string.
        """
        if type(content) == str:
            self.lines.append(content)
        else:
            raise Exception( "str object required!")

    def jout_dp(self, d):
        """
            json outputs for individual data point, takes dictionary.
        """
        if type(d) == dict:
            self.dicts_dp.append(d)
        else:
            raise Exception( "dict object required!")

    def jout_exp(self, d):
        """
            json outputs for whole experiment, takes dictionary(appending).
        """
        if type(d) == dict:
            self.dict_exp.update(d)
        else:
            raise Exception( "dict object required!")

    def jout_expS(self, a,b):
        """
            json outputs for whole experiment, takes key-value pair.
        """
        self.jout_exp({a:b})

    def generate(self):
        """
            generates output file according to put in data
        """
        outd = {'dp':self.dicts_dp, 'exp':self.dict_exp}

        os.system('touch '+self.fn+".json")
        fp1 = open(self.fn+".json", 'w')
        json.dump(outd, fp1)
        fp1.close()

        os.system('touch '+self.fn+".txt")
        fp2 = open(self.fn+".txt", 'w')
        #fp.write('\n')
        for l in self.lines:
            fp2.write(l+'\n')
        fp2.close()
