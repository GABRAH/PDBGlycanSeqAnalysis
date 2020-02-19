import os
import csv
import shutil
import re
import requests
import privateer
from datetime import datetime

import traceback


def GetDirectories(currentdirectory):
    directories = []
    for directory in os.listdir(currentdirectory):
        if os.path.isdir(os.path.join(currentdirectory, directory)):
            directories.append(directory)
    return directories

def CreateFolder(path):
    if not os.path.exists(path):
        os.makedirs(path)
    else:
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



tock = datetime.now()

rootDir = os.getcwd()
structureListDir = os.path.join(rootDir, "structures")
srcFileDirs = GetDirectories(structureListDir)
resultsDir = os.path.join(rootDir, "results")


for directory in srcFileDirs:
    sourceDir = os.path.join(structureListDir, directory)
    outputDir = os.path.join(resultsDir, directory)
    CreateFolder(outputDir)
    with open(os.path.join(outputDir, "output.csv"), "a", newline="") as csvfile:
        fieldnames = ["pdbID", "Residue", "Chain", "ClientWURCS", "ServerWURCS", "stringMatch", "glytoucanID"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({"pdbID": "PDB_ID", "Residue": "Residue", "Chain": "Chain", "ClientWURCS": "privateerWURCS", "ServerWURCS": "glycosmosWURCS", "stringMatch": "stringMatch", "glytoucanID": "glytoucanID"})
        for count, pdbFile in enumerate(os.listdir(sourceDir)):
            if pdbFile.endswith(".pdb"):
                pdbID = os.path.splitext(os.path.basename(pdbFile))[0]
                print(f'Currently processing: {pdbID}\nProgress: {count} out of {len(os.listdir(sourceDir))}\t Progress - {int((count/len(os.listdir(sourceDir))*100))}%')
                pdbFilePath = os.path.join(sourceDir, pdbFile)
                totalWURCS = privateer.print_wurcs(pdbFilePath)
                
                temporaryString = totalWURCS.split('\n', 1)[0]
                if temporaryString[0:21] == 'Total Glycans Found: ':
                    totalGlycansInModel = int(temporaryString[21:])
                
                temporaryListOfStrings = totalWURCS.splitlines()
                temporaryListOfStrings = temporaryListOfStrings[1:]

                for i in range(totalGlycansInModel):
                    residueInfo = temporaryListOfStrings[0].partition("/")[0]
                    chainInfo = temporaryListOfStrings[0].partition("/")[2]
                    privateerWURCS = temporaryListOfStrings[1]

                    queryLink = 'https://api.glycosmos.org/glytoucan/sparql/wurcs2gtcids?wurcs=' + privateerWURCS
                    serverResponse = return_json(queryLink)
                    for item in serverResponse:
                        try:
                            glytoucanID = item["id"]
                            glycosmosWURCS = item["WURCS"]
                        except Exception as e:
                            glytoucanID = "type error: " + str(e)
                            glycosmosWURCS = traceback.format_exc()


                    stringMatch = "TRUE" if privateerWURCS == glycosmosWURCS else "FALSE"
                    
                    writer.writerow({"pdbID": pdbID, "Residue": residueInfo, "Chain": chainInfo, "ClientWURCS": privateerWURCS, "ServerWURCS": glycosmosWURCS, "stringMatch": stringMatch, "glytoucanID": glytoucanID})
                    # print(pdbID, residueInfo, chainInfo, privateerWURCS, glycosmosWURCS, stringMatch)
                    # "pdbID", "Residue", "Chain", "ClientWURCS", "ServerWURCS", "stringMatch"

                    temporaryListOfStrings = temporaryListOfStrings[2:]
tick = datetime.now()
diff = tick - tock
print(f'\nFinished analysing Glycan sequences of all models in root/structures directory!\nTime elapsed: {diff.total_seconds()} seconds')

            
