import json

def transfer(name):
    f = open(name, "r")
    so = open(name+".txt", "w")
    jo = open(name+".json", "w")
    jo.write('{"result":[')
    i = 0
    for line in f.readlines():
        line = line.strip("\n")
        if line.startswith("{"):
            if i != 0:
                jo.write(',')
            d = eval(line)
            print d
            json.dump(d, jo, indent=4)
            i += 1
        else:
            print line
            so.write(line + "\n")
    jo.write(']}')
