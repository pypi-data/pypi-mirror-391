import time
import subprocess
import random
import os
import hashlib
import getpass
import mimetypes
import struct
from urllib.parse import urljoin, quote, urlparse
from datetime import datetime
import argparse

def run_shell_async(shell):
    # shell = f"{shell} > /dev/null 2>&1"
    subprocess.Popen(shell,stdout=subprocess.DEVNULL,shell=True)

def run_shell(shell):
    cmd = subprocess.Popen(shell,stdout=subprocess.PIPE,shell=True)
    output = cmd.stdout.read().decode() if cmd.stdout else None
    return output

def ask(prompt, candidates=None):
    if(candidates):
        r = input(f"{prompt} [{'/'.join(candidates)}]: ")
        r = r.strip()
        if(r not in candidates):
            return ask(prompt, candidates)
        return r
    else:
        r = input(f"{prompt}")
        r = r.strip()
        if not r:
            return ask(prompt, candidates)
        return r

def parse_arg(config, description = "process something"):
    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')

    # 创建解析步骤
    parser = argparse.ArgumentParser(description=description)

    for name, item in config.items():
        if isinstance(item, dict):
            t = item["type"]
            c = item["class"] if "class" in item else str
            if t == "pos":
                parser.add_argument(f'{name}', type=c)
                continue
            defaultvalue = item["default"]
        else:
            defaultvalue = item
        required = False
        if defaultvalue is None:
            required = True
            parser.add_argument(f'--{name}', dest=name, type=str, required=required)
            continue
        
        if isinstance(defaultvalue, type):
            required = True
            parser.add_argument(f'--{name}', dest=name, type=defaultvalue, required=required)
            continue

        if isinstance(defaultvalue, bool):
            parser.add_argument(f'--{name}', dest=name, type=str2bool, required=required, default=defaultvalue)
        else:
            parser.add_argument(f'--{name}', dest=name, type=type(defaultvalue), required=required, default=defaultvalue)

    args = parser.parse_args()
    return args

def mcontains(s, l):
    return any([i in s for i in l])

def long2bytes(num):
    return struct.pack('>Q', num)
            
def bytes2long(bs):
    return int.from_bytes(bs, byteorder="big")

def urlencode(url):
    return quote(url, safe='')

def GMT2timestamp(s):
    if not s:
        return 0
    dt = datetime.strptime(s, '%a, %d %b %Y %H:%M:%S GMT')
    timestamp = dt.timestamp()
    return int(timestamp)

def exists(path):
    return os.path.exists(path)

def readfile(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r") as f:
        return f.read()

def writefile(path, content):
    with open(path, "w+") as f:
        return f.write(content)
    
def trimstrlist(l):
    return [s.strip() for s in l if s and s.strip()]

def _listdir(dirname, prefix=None, suffix=None):
    filenames:list[str] = os.listdir(dirname)
    if prefix:
        filenames = [filename for filename in filenames if filename.startswith(prefix)]
    if suffix:
        filenames = [filename for filename in filenames if filename.endswith(suffix)]
    filenames.sort()
    return filenames, [os.path.join(dirname, filename) for filename in filenames]

def listdir2(dirname, prefix=None, suffix=None):
    filenames, paths = _listdir(dirname, prefix=prefix, suffix=suffix)
    return list(zip(filenames, paths))

def mkdir(dirname):
    os.makedirs(dirname, exist_ok=True)

def chunck_func(batch_size:int):
    return lambda a:map(lambda b:a[b:b+batch_size],range(0,len(a),batch_size))

