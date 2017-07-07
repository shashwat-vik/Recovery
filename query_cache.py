import json, pickle
from hashlib import md5

cache_file = 'cache/Karnataka.csv_cache.dat'
CACHE = pickle.load(open(cache_file, 'rb'))

address = 'k.b.s.no 2 bailhongal, karnataka'
hid = md5(address.encode()).hexdigest()
resp = CACHE[hid]

print(json.dumps(resp, indent=4))
