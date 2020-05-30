import requests
import shutil
import os
import json
from datetime import datetime


def return_response_from_glyconnect_api(glytoucanID):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = f'{{ "glytoucan_id": "{glytoucanID}"}}'
    response = requests.post('https://glyconnect.expasy.org/api/structures/search/glytoucan', headers=headers, data=data)
    return response
   

def parse_json_file(path):
    with open(path) as json_file:
        data = json.load(json_file)

    return data

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError as e:
    return False
  return True


rootDir = os.getcwd()
dataDir = os.path.join(rootDir, "data")

json_file_to_append = "glycosmos_data_glyconncet_appended.json"
json_file_to_append_path = os.path.join(dataDir, json_file_to_append)

jsonObj = parse_json_file(json_file_to_append_path)
jsonObjNew = []

filename = "glycosmos_data_glyconncet_finalized.json"
substring = "Error:"
for count, line in enumerate(jsonObj):
    print(f'Currently processing: {line["AccessionNumber"]}\nProgress: {count} out of {len(jsonObj)}\t Progress - {int((count/len(jsonObj)*100))}%')
    if substring in line['glyconnect']:
        glytoucanID = line['AccessionNumber']
        responseGlyConnect = return_response_from_glyconnect_api(glytoucanID)
        print("Current HTTP response: " + str(responseGlyConnect.status_code))
        if responseGlyConnect.status_code == 200:
            line['glyconnect'] = responseGlyConnect.json()
        elif responseGlyConnect.status_code == 404: 
            line['glyconnect'] = "NotFound"
        else: 
            try:
                responseGlyConnect.raise_for_status()
            except requests.exceptions.HTTPError as e:
                line['glyconnect'] = "Error: " + str(e)
    jsonObjNew.append(line)



with open(os.path.join(dataDir, filename), 'w', encoding='utf-8') as file:
    json.dump(jsonObjNew, file, ensure_ascii=False, indent=4)
print(f"Finished downloading and appending GlyConnect data. \nAbsolute path of the output: {os.path.join(dataDir, filename)}")
