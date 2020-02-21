import requests
import shutil
import os
import json
from datetime import datetime

def CreateFolder(path):
    if not os.path.exists(path):
        print(f"\n...{path} does not exist. Creating directory...\n")
        os.makedirs(path)
    else:
        print(f"\n...{path} already exists. Removing old directory to create a new directory...\n")
        shutil.rmtree(path)           # Removes all the subdirectories!
        os.makedirs(path)

def return_json(URL):
    response = requests.get(URL)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # Whoops it wasn't a 200
        return "Error: " + str(e)

    # Must have been a 200 status code
    json_obj = response.json()
    return json_obj


date = datetime.now()
date = date.strftime('%Y-%m-%d')
filename = "glycosmos_data_" + date + ".json"

rootDir = os.getcwd()
dataDir = os.path.join(rootDir, "data")

CreateFolder(dataDir)

print(f"Downloading GlyTouCan data as: {filename} in {dataDir}\n")

jsonObject = return_json("https://api.glycosmos.org/glytoucan/sparql/glytoucan-data")


with open(os.path.join(dataDir, filename), 'w', encoding='utf-8') as file:
    json.dump(jsonObject, file, ensure_ascii=False, indent=4)

print(f"Finished downloading GlyTouCan data.\nAbsolute path of the output: {os.path.join(dataDir, filename)}")
