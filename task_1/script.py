from enum import Enum
import json
from time import sleep
import requests
import pydantic as pd

IN_PROGRESS = "in_progress"

class TokenType(Enum):
    Bearer = "Bearer"


class Authorization(pd.BaseModel):
    token_type: TokenType
    trip_creation_token: str


def get_authorization() -> Authorization:
    url = "https://api.gordiansoftware.com/v2.2/authorize"
    headers = {
        "accept": "application/json",
        "authorization": "Basic c2FuZGJveF8zVzRaUHJqSWhtU005S0lGbnRSOU9IQzhHT2h2dTZLYjhKc2FIMGV4UEZUUk1OMTZGRXNXb0ltejo="
    }
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    response = response.json()
    response_auth = Authorization(
        token_type=response["token_type"],
        trip_creation_token=response["trip_creation_token"]
    )
    return response_auth


def create_trip(data: dict) -> dict:

    auth = get_authorization()
    url = "https://api.gordiansoftware.com/v2.2/trip"    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"{auth.token_type.value} {auth.trip_creation_token}"
    }

    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()


def get_trip_seat_map(trip: dict) -> dict:

    search_id = _get_search_id(trip)
    return _get_search_results(trip, search_id)


def _get_search_id(trip: dict):
    url = f"https://api.gordiansoftware.com/v2.2/trip/{trip['trip_id']}/search"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {trip['trip_access_token']}"
    }
    payload = {
        "seat": {
            "search": True
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["search_id"]


def _get_search_results(trip: dict, search_id: str) -> dict:
    url = f"https://api.gordiansoftware.com/v2.2/trip/{trip['trip_id']}/search/{search_id}"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {trip['trip_access_token']}"
    }
    attempts = 10
    while(attempts > 0):
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response = response.json()
        if response["status"] == IN_PROGRESS:
            attempts -= 1
            sleep(1)
        else:
            break
    return response


def proccess_file(file_name: str):
    with open(file_name, "r") as f:
        data = json.load(f)
        trip_created = create_trip(data)
        trip_searched = get_trip_seat_map(trip_created)
    with open(file_name.replace("input", "output"), 'w') as f:
        json.dump(trip_searched, f, indent=4)


for i in range(1, 5):
    proccess_file(f'task_1/input/trip_{i}.json')
