from time import sleep
from datetime import datetime

import requests
import json

prefix = "api/v1/"
backend_url = "http://127.0.0.1:8001/"
login_data = {'username': 'admin', 'password': 'admin'}

print(f"connect to:{backend_url}")
print(f"request session")
session = requests.Session()
response = session.post(backend_url + prefix + "token", login_data)
response = json.loads(response.content.decode('utf-8'))
print(f"response: {response}")
if 'access_token' in response:
    session.headers.update({"Authorization": 'Bearer ' + response['access_token']})
else:
    print(f"error")
# try to read the information about user logged
a = session.get(backend_url + prefix + "users/me/info")
response2 = json.loads(a.content.decode('utf-8'))
print(f"me:{response2}")

# try to read the info endpoint (no login is required)
b = session.get(backend_url + "api/v1/info")
response3 = json.loads(b.content.decode('utf-8'))
print(f"info:{response3}")
nLoop = 0
while True:
    nLoop += 1
    b = session.get(backend_url + prefix + "users/me/info")
    response3 = json.loads(b.content.decode('utf-8'))
    auth = False
    print(f"===>{b.text}")
    print(f"===>{b.headers}")
    print(f"===>{b.content}")
    print(f"===>{b.ok}")
    print(f"===>{b.reason}")
    print(f"===>{b.status_code}")

    print(f"[{nLoop}] {datetime.now()} {response3} {b} {auth}")

    if b is not None:
        if b.status_code == 200:
            auth = True
        elif b.status_code == 401:
            print(f"Try to renew the token")
            response = session.post(backend_url + prefix + "token", login_data)
            print(f"response:{response}")
            response4 = json.loads(response.content.decode('utf-8'))
            print(f"response decode=>:{response4}")
            if 'access_token' in response4:
                session.headers.update({"Authorization": 'Bearer ' + response4['access_token']})
            else:
                print(f"error")

    sleep(10)

    c = session.get(backend_url + "api/v1/utils/health/")
    response4 = json.loads(c.content.decode('utf-8'))
    print(f"[{nLoop}] {datetime.now()} {response4} {c}")
    print(f"*****")
    sleep(10)
