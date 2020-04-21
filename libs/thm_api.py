import json
import requests

root_url = "https://tryhackme.com"


# Gets user data
def getUserData(username):
    res = requests.get(f"{root_url}/api/user/{username}")
    return json.loads(res.text)


# Check subscription status
def isSubscribed(username):
    subscribed = "No!"

    try:
        res = requests.get(f"{root_url}/p/{username}")
    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        if "<span>Subscribed</span>" in res.text:
            subscribed = "Yes!"

    return subscribed
