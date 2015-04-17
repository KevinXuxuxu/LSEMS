import web
import os
import run
import json
import re
import sys
import threading as thd

urls = (
        '/', 'index'
        )

class index:
    def GET(self):
        return "This is LSEMS."
    def POST(self):
        data = json.loads(web.data())
        os.system("python exp.py -i '%s'" %json.dumps(data))

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
