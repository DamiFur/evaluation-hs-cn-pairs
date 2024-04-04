import os
from glob import glob
import requests
import json

ENDPOINT = "http://localhost:8080/"
ACCESS_TOKEN = "65aa5ec1f1d822b1fecada16c311d59e21b5250a"

if not os.path.exists("output"):
    os.makedirs("output")
response = requests.get(ENDPOINT + "api/projects/", headers={"Authorization": f"Token {ACCESS_TOKEN}"})
project_ids = [pjct["id"] for pjct in json.loads(response.content.decode('utf-8'))["results"]]
for pjct_id in project_ids:
    with requests.get(ENDPOINT + f"api/projects/{pjct_id}/export?exportType=JSON&download_all_tasks=true", headers = {"Authorization": f"Token {ACCESS_TOKEN}"}, stream=True) as r:
        with open(f"output/output_{pjct_id}.json", 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
            f.close()
    # curl -X GET https://localhost:8080/api/projects/{id}/export?exportType=JSON&download_all_tasks=true -H 'Authorization: Token abc123' --output 'annotations.json'