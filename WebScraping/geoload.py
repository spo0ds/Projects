import sqlite3
import json
import time
import ssl
import urllib.parse,urllib.request,urllib.error
import http
import sys

api_key = False
# If you have a Google Places API key, enter it here
# api_key = 'AIzaSy___IDByT70'

if api_key is False:
    api_key = 42
    serviceurl = "http://py4e-data.dr-chuck.net/json?"
else :
    serviceurl = "https://maps.googleapis.com/maps/api/geocode/json?"

# Additional detail for urllib
# http.client.HTTPConnection.debuglevel = 1

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


conn = sqlite3.connect('geodata.sqlite')
cur = conn.cursor()

cur.execute('Create table if not exists Locations(address text,geodata text)')

fh = open("where.data")
count = 0
for line in fh:
    if count > 200:
        print('200 data retrived restart it to retrived more')
        break

    address = line.strip()
    cur.execute('Select geodata from Locations where address = ?',(memoryview(address.encode()),))

    try:
        data = cur.fetchone()[0]
        print('Data found in database',address)
        continue
    except: pass

    parms = dict()
    parms["address"] = address
    if api_key is not False: parms['key'] = api_key
    url = serviceurl+urllib.parse.urlencode(parms)

    print('Retrieving',url)
    uh = urllib.request.urlopen(url,context = ctx)
    data = uh.read().decode()
    print('Retrieved',len(data),'characters',data[:20].replace('\n',''))
    count = count+1

    try:
        js = json.loads(data)
    except:
        print(data)
        continue

    if 'status' not in js or js['status'] != 'OK' and js['status'] != 'ZERO_RESULTS':
        print('Failed to Retrieve data')
        print(data)
        break

    cur.execute('Insert into Locations(address,geodata) values(?,?)',
        (memoryview(address.encode()),memoryview(data.encode())))

    conn.commit()

    if count % 10 == 0:
        print('Pausing for a bit')
        #time.sleep(5)

print("Run geodump.py to read the data from the database so you can vizualize it on a map.")
