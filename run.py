# use UTP-8 #
"""
    This script is to record matadata of user's experiment info including
    parameters and scripts in order to run experiment.
    @iiis.tsinghua.edu.cn
"""

__author__ = "Xu Fangzhou"
__email__ = "kevin.xu.fangzhou@gmail.com"

from json import *
from pymongo import *
from time import asctime
from transferOutput import transfer
import sys
import os
import re
import shutil
import data
import json

def verifyUser(client, name):
    """
        verify or create user for the record
    """

    users = client['users']
    if name not in users.collection_names():
        print("creat new user \""+name+"\"? [y/n]")
        if raw_input() != 'y':
            print("exiting...")
            sys.exit(0)
    return users[name]

def checkKeys(dict, ks):
    missing = []
    for k in ks:
        if k not in dict.keys():
            missing += [k]
    return missing

def random_commit_id():
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

def record(params, git_info = {}):
    """
        this functions takes in a dictionary as parameters
        and record it in the MongoDB before run it.
    """
    print "recording..."
    config = json.load(open("~/sandbox/config.json"))

    try:
        # connect to MongoDB
        try:
            client = MongoClient(config["mongodb_url"])
        except Exception as e:
            raise Exception("fail to connect to given MongoDB address: " + DB_addr)

        # check and run the thing
        missing = checkKeys(params, ['data_set', 'src', 'type', 'param'])
        if len(missing) != 0:
            raise Exception("missing attribute"+('s' if len(missing)!=1 else '')+": "+str(missing))

        params['time'] = asctime()
        params['commit_id'] = git_info['commit_id']
        params['name'] = git_info['name']
        repo_name = git_info['repo_name']
        params['repo_name'] = repo_name
        user = verifyUser(client, git_info['name'])

        exp = user.find_one({'exp_name': repo_name})
        if not exp:
            print 'adding new experiment '+repo_name+'...'
            user.insert({'exp_name': repo_name, 'exp_records':[]})
        old_records = user.find_one({'exp_name': repo_name})['exp_records']
        user.update({'exp_name': repo_name}, {'$set': {'exp_records': old_records + [params]}})

        print params
        #user.insert(params)
        client.close()
        return True,params
    except Exception as e:
        print e.message
        print "Aborting..."
        return False,{}

def save_results(file_name, params):
    fp = open(file_name,'r')
    results = load(fp)
    print "Loaded output file"

    config = json.load(open('~/sandbox/config.json'))

    try:
        client = MongoClient(config['mongodb_url'])
        if results.has_key("exp"):
            user = client['users'][params['name']]
            repo = user.find_one({'exp_name': params['repo_name']})
            er = repo['exp_records']
            if er[-1]['commit_id'] == params['commit_id']:
                er[-1]['result'] = results['exp']
                user.update({'exp_name': params['repo_name']}, {'$set': {'exp_records': er}})
            else:
                raise Exception("Finding experiment error")
        if results.has_key("dp") and len(results["dp"]) > 0:
            print "saving dp results"
            data = client['datas'][re.split('\.', params['data_set'])[0]]
            commit_ids = data.find_one({'_id':'info'})['commit_ids']
            commit_ids.insert(0,params['commit_id'])
            data.update({'_id': 'info'}, {'$set': {'commit_ids': commit_ids }})
            for r in results["dp"]:
                i = r.pop('id')
                dp = data.find_one({'id':i})
                for kv in r.items():
                    if dp.has_key(kv[0]):
                        dp[kv[0]][params['commit_id']] = kv[1]
                    else:
                        dp[kv[0]] = {params["commit_id"]: kv[1]}
                    data.update({'id': i}, {'$set': {kv[0]: dp[kv[0]]}})

                # data.update({'id': r.pop('id')}, {'$set': {params['commit_id']: r }})
    except Exception as e:
        print e.message
        print "Aborting..."

def run(params):
    print "running"
    old_dir = os.getcwd()
    tmp = re.split('/', old_dir)
    sb_dir = "/%s/%s/sandbox" %(tmp[1],tmp[2])
    #sb_dir = "/home/ubuntu/sandbox"
    src = params['src']
    try:
        if src not in os.listdir('src'):
            raise Exception("fail to find source file "+src)
        if params['name'] in os.listdir(sb_dir):
            print "deleting duplication..."
            os.system("rm -r %s/%s/" %(sb_dir, params['name']))
        os.system("cp -r src %s" %sb_dir)
        os.chdir(sb_dir)
        # user name with time stamp as temp directory
        dir_name = "%s-%s" %(params['name'], asctime().replace(' ','_'))
        os.system("mv src %s" %dir_name)
        os.chdir(dir_name)
        command = ""
        if params['type'] == 'python':
            command += 'python'
        command += " "+src
        for p in params['param']:
            command += " --"+p+"="+str(params['param'][p])
        command += ' > output'
        print command
        os.system(command)
        mgdb = data.Database()
        parent = re.split('\.', params['data_set'])[0]
        if params.has_key('out'):
            for out_file in re.split(' ', params['out']):
                mgdb.generate_data(out_file, description="generated data "+out_file, parent=parent)
        print "copying outputs..."
        os.system('cp output.txt ~')
        os.system('cp output.json ~')
        print "recording outputs"
        save_results('output.json', params)
        os.chdir('..')
        os.system('rm -rf '+dir_name)
    except Exception as e:
        print e
        print "Aborting..."
        os.chdir('..')
        os.system('rm -rf '+dir_name)
    print "finished!"
    os.chdir(old_dir)

def read(file_name, git_info):
    print "current dir: "+os.getcwd()
    fp = open(file_name)
    params = load(fp)
    flag, p = record(params, git_info)
    if flag:
        run(p)
def main():
    print("json file as input: ")
    file_name = raw_input()
    read(file_name, {'commit_id':random_commit_id()+random_commit_id()})

if __name__ == "__main__":
    main()
