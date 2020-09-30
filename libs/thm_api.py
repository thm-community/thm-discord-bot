import json

import requests

import libs.config as config

####################
# Config variables #
####################

c_api_rank = config.get_config("url")["api"]["user"]
c_api_token = config.get_config("url")["api"]["token"]
c_api_leaderboard = config.get_config("url")["api"]["leaderboard"]
c_url_userprofile = config.get_config("url")["user_profile"]
c_url_hacktivities = config.get_config("url")["api"]["hacktivities"]

###################
# Other variables #
###################

pages = {1: 5, 2: 10, 3: 15, 4: 20, 5: 25, 6: 30, 7: 35, 8: 40, 9: 45, 10: 50}

#############
# Functions #
#############


def get_user_data(username):
    """Fetches the user's data."""

    response = requests.get(
        c_api_rank.format(username))
    data = response.text
    return json.loads(data)


def get_sub_status(username):
    """Fetches the user's sub status."""

    url = c_url_userprofile.format(username)
    check = "No!"
    try:
        response = requests.get(url)
    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        if "<span>Subscribed</span>" in response.text:
            check = "Yes!"
        else:
            check = "No!"
    return check


def get_leaderboard_data(**kwargs):
    """Fetches leaderboard data (all-time/monthly)"""
    if len(kwargs) > 0:
        query = "?"
        for key, val in kwargs.items():
            if val is None:
                continue
            query += f'{key}={str(val).lower()}&'

    response = requests.get(c_api_leaderboard + query)
    data = response.text
    data = json.loads(data)['ranks']

    return data


def get_public_rooms(filter_type: str = None) -> list:
    """Fetches all public rooms"""
    if filter_type:
        query = f'?type={filter_type}'
    else:
        query = ''

    response = requests.get(c_url_hacktivities + query)

    return json.loads(response.text)
