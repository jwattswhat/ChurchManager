import requests

def check_internetconnection(timeout):
    while True:
        try:
            requests.head("http://www.google.com/", timeout=timeout)
            return True
        except requests.ConnectionError:
            pass

print (check_internetconnection(timeout=1))