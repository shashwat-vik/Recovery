# Python 3.x

from hashlib import md5
import requests, os, json, sys, pickle

API_KEYS = [
        'AIzaSyB-o_BigZi-jvjKqNXiyyTb8GKBriiI06c', #Rohit
        'AIzaSyCgs8C71RqvWoeO69XBXVPQH006i7v4IkM', #Ananth's
        'AIzaSyCcijQW6eCvvt1ToSkjaGA4R22qBdZ0XsI', #Aakash's
        'AIzaSyA-sGk-2Qg_yQAoJtQ1YUPKEYPCQ5scf5A', #Shubhankar's
        'AIzaSyBVmpXHCROnVWDWQKSqZwgnGFyRAilvIc4',  #Shashwat's
        'AIzaSyAD58vGvx1OdgRq-XdYFZW8cyKhODkg6lc',   #Sisodia
        'AIzaSyDs9N58rJ1n-C7qQ0B1qnhAP8DSzzLd1sU',    #Singh
        'AIzaSyC5-mD5yfBlyy1K7H_HKhCk-05d9kF02_k',  #Akarsh
        'AIzaSyCq7QLuMkfcm-68JL95Au5x9Vc_0qCp8iU'   #Shardul
]
key_index = 0
CACHE = {}

cache_file = ''

def update_file_name(fname):
    global cache_file
    cache_file = 'cache/{0}_cache.dat'.format(fname)

def CACHE_LOAD():
    global CACHE, cache_file
    if os.path.exists(cache_file):
        CACHE = pickle.load(open(cache_file, 'rb'))

def CACHE_SAVE():
    global CACHE, cache_file
    pickle.dump(CACHE, open(cache_file, 'wb'))

def graceful_request(address):
    global API_KEYS, key_index, CACHE
    # CACHE CHECK
    hid = md5(address.encode()).hexdigest()
    if hid in CACHE:
        data = CACHE[hid]
        return (201, data)
    else:
        url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query='+address+'&types=establishment&key='
        chain_count = 0
        while True:
            resp = requests.get(url+API_KEYS[key_index]).json()
            if resp['status'] == 'OK':
                CACHE[hid]=resp          # CACHE-UPDATE
                return (201, resp)
            elif resp['status'] == 'ZERO_RESULTS':
                CACHE[hid]={"results":[]}
                return (205, None)
            elif resp['status'] == 'NOT_FOUND':
                return (205, None)
            key_index = (key_index+1)%len(API_KEYS)
            chain_count += 1
            if chain_count == len(API_KEYS):
                print('KEYS EXHAUSTED')
                raise KeyboardInterrupt
                return (500, None)          # BEWARE. KEYS EXHAUSTED
