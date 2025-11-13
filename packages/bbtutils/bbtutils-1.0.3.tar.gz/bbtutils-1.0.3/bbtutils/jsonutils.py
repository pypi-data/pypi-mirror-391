import os
import json
import pickle
from .basicutils import mkdir
from json import JSONEncoder

class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

def objequals(o1:object, o2:object) -> bool:
    return json.dumps(o1, cls=MyEncoder) == json.dumps(o2, cls=MyEncoder)

def objtojson(o:object) -> str:
    return json.dumps(o, cls=MyEncoder)


def loadjsonfile(path):
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)

def writejsonfile(path, obj, automkdir=True):
    if automkdir:
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            mkdir(dir)
    with open(path, "w+") as f:
        return json.dump(obj, f)

def loadpicklefile(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)
    
def writepicklefile(path, obj):
    with open(path, "wb+") as f:
        return pickle.dump(obj, f)
