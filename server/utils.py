import requests
import config
import math
import json

def dead_response(message="Invalid Request", rid=config.rid):
    return {"error": {"code": 404, "message": message}, "id": rid}

def response(result, error=None, rid=config.rid):
    return {"error": error, "id": rid, "result": result}

def make_request(method, params=[]):
    headers = {"content-type": "text/plain;"}
    data = json.dumps({"id": config.rid, "method": method, "params": params})

    try:
        return requests.post(config.endpoint, headers=headers, data=data).json()
    except Exception:
        return dead_response()

# def reward(height):

#     reward = 2.5e11
#     supply = 0
#     y = 210000  # reward changes all y blocks
#     while height > y - 1:
#         supply = supply + y * reward
#         reward = int(reward / 2.0)
#         height = height - y
#     supply = supply + height * reward
#     return (supply + reward) / 1e8

def satoshis(value):
    return int(value * math.pow(10, 8))

def amount(value):
    return round(value / math.pow(10, 8), 8)
