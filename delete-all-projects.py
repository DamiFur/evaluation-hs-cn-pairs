import os
from glob import glob
import requests
import json

ENDPOINT = "http://localhost:8080/"
ACCESS_TOKEN = "65aa5ec1f1d822b1fecada16c311d59e21b5250a"

response = requests.get(ENDPOINT + "api/projects/", headers={"Authorization": f"Token {ACCESS_TOKEN}"})
project_ids = [pjct["id"] for pjct in json.loads(response.content.decode('utf-8'))["results"]]
for pjct_id in project_ids:
    requests.delete(ENDPOINT + f"api/projects/{pjct_id}/", headers = {"Authorization": f"Token {ACCESS_TOKEN}"})
# curl -X GET https://localhost:8080/api/projects/ -H 'Authorization: Token abc123'