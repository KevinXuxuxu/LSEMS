import web
import os
import run
import json
import re
import sys
import threading as thd
from time import asctime

urls = (
        '/', 'index'
        )

block = {}
lock = thd.RLock()

class index:
    def GET(self):
        return "This is LSEMS."
    def POST(self):
        global block
        data = json.loads(web.data())
        name = data['user_name']
        flag = False

        no_run = True
        for commit in data['commits']:
            if "run Forest run" in commit['message'] or "Bazinga" in commit['message']:
                no_run = False
        if no_run:
            return

        lock.acquire()
        if ( not block.has_key(name) ) or len(block[name]) == 0:
            block[name] = {asctime(): data}
            flag = True
        else:
            block[name][asctime()] = data
        lock.release()

        while flag and len(block[name]) != 0:
            data = block[name][sorted(block[name].keys())[0]]
            print '\033[1;32m'
            print "start"
            print '\033[0m'
            os.system("python exp.py -i '%s'" %json.dumps(data))
            print '\033[1;31m'
            print "end"
            print '\033[0m'
            block[name].pop(sorted(block[name].keys())[0])

    # not in use, moved to exp.py
    def exp(self, data):
        print data
        repo_url = data['repository']['url']
        repo_name = re.split('/', data['repository']['homepage'])[-1:][0]
        print "current dir: "+os.getcwd()
        os.chdir('repos')
        if repo_name in os.listdir('.'):
            print("found repo existing.")
            os.system("rm -r -f "+repo_name)
            print("deleted.")
        os.system("git clone "+repo_url)
        os.chdir(repo_name)
        file_names = os.listdir('.')
        try:
            if 'exp.json' not in file_names:
                raise Exception("Cannot find file exp.json!\nAborting...")
            run.read('exp.json',
                {"commit_id": data['commits'][0]['id'],
                'repo_name': data['repository']['name'],
                'name': data['user_name'] },)
        except Exception as e:
            print e.message
        os.chdir('../..')

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
