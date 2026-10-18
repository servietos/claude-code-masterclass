import json


def load_gateway_key(path="config.secrets.json"):
    with open(path) as handle:
        return json.load(handle)["gateway"]["api_key"]
