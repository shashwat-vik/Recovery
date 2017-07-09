# Python 3.x

from hashlib import md5
import requests, os, json, sys, pickle, time

API_KEYS = ['AIzaSyBkqEQ3sdYR_SWHvPYSdTS11Ka9GS1G5t8', #NewOne
        'AIzaSyB-o_BigZi-jvjKqNXiyyTb8GKBriiI06c', #Rohit
        'AIzaSyCgs8C71RqvWoeO69XBXVPQH006i7v4IkM', #Ananth's
        'AIzaSyCcijQW6eCvvt1ToSkjaGA4R22qBdZ0XsI', #Aakash's
        'AIzaSyA-sGk-2Qg_yQAoJtQ1YUPKEYPCQ5scf5A', #Shubhankar's
        'AIzaSyBVmpXHCROnVWDWQKSqZwgnGFyRAilvIc4',  #Shashwat's
        'AIzaSyAD58vGvx1OdgRq-XdYFZW8cyKhODkg6lc',   #Sisodia
        'AIzaSyDs9N58rJ1n-C7qQ0B1qnhAP8DSzzLd1sU',    #Singh
        'AIzaSyC5-mD5yfBlyy1K7H_HKhCk-05d9kF02_k',  #Akarsh
        'AIzaSyCq7QLuMkfcm-68JL95Au5x9Vc_0qCp8iU',   #Shardul
        'AIzaSyCp4DIN0mzmvQxcq0IOMtu48ZmFwr3qyj8',
        'AIzaSyDY-x_LfS0DKo4dADRqQRCpo_axRZFTCrc', #Amit's
        'AIzaSyANGekXBG6b61uGWtMgoBUzDvcZDO8jBAg'  #Amit's
]
key_index = 0
CACHE = {}

cache_file = ''

def update_file_name(fname):
    global cache_file
    if not os.path.exists('cache'): os.mkdir('cache')
    cache_file = 'cache/{0}_cache.dat'.format(fname)

def CACHE_LOAD():
    global CACHE, cache_file
    if os.path.exists(cache_file):
        CACHE = pickle.load(open(cache_file, 'rb'))

def CACHE_SAVE():
    global CACHE, cache_file
    pickle.dump(CACHE, open(cache_file, 'wb'))

def good_night(sleep_time=120):
    update_interval = 2
    t0 = time.time()        # SLEEP TIME COUNT
    t1 = time.time()        # UPDATE TIME COUNT
    while True:
        if time.time() - t1 > update_interval:
            sys.stdout.write("WAKE UP IN: {0:.2f} min\r".format((sleep_time - (time.time()-t0))/60))
            sys.stdout.flush()
            t1 = time.time()
        if time.time() - t0 > sleep_time:
            print()
            break

def hex_clean(x):
    while True:
        pos = repr(x).find(r'\x')
        if pos != -1:
            x = x[:pos-1]+x[pos:]
        else:
            break
    return x

def graceful_request(address):
    global API_KEYS, key_index, CACHE
    # CACHE CHECK
    hid = md5(address.encode('utf-8','ignore')).hexdigest()
    if hid in CACHE:
        data = CACHE[hid]
        return (201, data)
    else:
        url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query='+address+'&types=establishment&key='
        chain_count = 0
        cleaned = False
        while True:
            resp = requests.get(url+API_KEYS[key_index]).json()
            if resp['status'] == 'OK':
                CACHE[hid]=resp                         # CACHE-UPDATE
                return (201, resp)
            elif resp['status'] == 'ZERO_RESULTS':
                CACHE[hid]={"results":[]}               # CACHE-UPDATE
                return (205, None)
            elif resp['status'] == 'INVALID_REQUEST':
                if not cleaned:
                    url = hex_clean(url)
                    cleaned = True
                    continue
                print(resp)
                raise KeyboardInterrupt

            print(key_index, '|', chain_count, '|', resp['status'], '|', resp['error_message'])
            key_index = (key_index+1)%len(API_KEYS)
            chain_count += 1
            if chain_count%len(API_KEYS) == 0:
                print('\n**** KEYS EXHAUSTED *****')
                print('** SLEEPING FOR 2 HRS **\n')
                good_night(7200)
                #raise KeyboardInterrupt         # BEWARE. KEYS EXHAUSTED
