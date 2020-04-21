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


# Gets leaderboard data
def getLeaderboard(page, monthly=False):
    pages = {1: 5, 2: 10, 3: 15, 4: 20, 5: 25, 6: 30, 7: 35, 8: 40, 9: 45, 10: 50}

    style = "topUsers"
    if monthly:
        style = "topUsersMonthly"

    response = requests.get(f"{root_url}/api/leaderboards")
    data = json.loads(response.text)[style]
    num = pages[page] - 5

    users = []

    for e, i in enumerate(data[num:pages[page]]):
        users.append({
            'username': i["username"],
            'avatar': i["avatar"],
            'points': i["points"],
            'monthlyPoints': i["monthlyPoints"]
        })

    return users
