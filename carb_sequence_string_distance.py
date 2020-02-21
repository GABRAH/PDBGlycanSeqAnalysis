import os
import csv
import shutil
import re
import privateer
import json
from datetime import datetime
import textdistance
from heapq import nlargest

def GetDirectories(currentdirectory):
    directories = []
    for directory in os.listdir(currentdirectory):
        if os.path.isdir(os.path.join(currentdirectory, directory)):
            directories.append(directory)
    return directories

def CreateFolderAndFile(path, outputfilename):
    if not os.path.exists(path):
        os.makedirs(path)
    # else:
    #     shutil.rmtree(path)           # Removes all the subdirectories!
    #     os.makedirs(path)
    if os.path.exists(os.path.join(path, outputFileName)):
        os.remove(os.path.join(path, outputFileName))

def GetJSON(path):
    if path.endswith(".json"):
        with open(path) as json_file:
            data = json.load(json_file)
            return data

def Find(list, key, value):
    for i, dic in enumerate(list):
        if dic[key] == value:
            return i
    return "Not Found"

def FindClosestMatches(list, value):
    valueListOfDicts = []
    for item in list:
        similarity = textdistance.damerau_levenshtein.normalized_similarity(value, item['Sequence'])
        valueDict = {'GTC_ID': item['AccessionNumber'], 'Sequence': item['Sequence'], "Score": similarity}
        valueListOfDicts.append(valueDict)
    closestMatches = nlargest(3, valueListOfDicts, key=lambda s: s['Score'])
    return closestMatches




rootDir = os.getcwd()
structureListDir = os.path.join(rootDir, "structures")
srcFileDirs = GetDirectories(structureListDir)
resultsDir = os.path.join(rootDir, "results/offline")
dataDir = os.path.join(rootDir, "data")
outputFileName = "closest_strings.csv"

# ignoreDirectoryList = ["cryoem_n_glycosylated", "xray_n_glycosylated", "cryoem_n_glycosylated_failed"]
ignoreDirectoryList = []
dataFileName = "glycosmos_data_2020-02-20.json"

glycosmosData = GetJSON(os.path.join(dataDir, dataFileName))

tock = datetime.now()
for directory in srcFileDirs:
    if directory not in ignoreDirectoryList:
        sourceDir = os.path.join(structureListDir, directory)
        outputDir = os.path.join(resultsDir, directory)
        CreateFolderAndFile(outputDir, outputFileName)
        with open(os.path.join(outputDir, outputFileName), "a", newline="") as csvfile:
            fieldnames = ["pdbID", "Residue", "Chain", "ClientWURCS", "firstClosest", "secondClosest", "thirdClosest", "firstScore", "secondScore", "thirdScore", "firstClosestGTC", "secondClosestGTC", "thirdClosestGTC"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({"pdbID": "PDB_ID", "Residue": "Residue", "Chain": "Chain", "ClientWURCS": "privateerWURCS", "firstClosest": "firstClosest", "secondClosest": "secondClosest", "thirdClosest": "thirdClosest", "firstScore": "firstScore", "secondScore": "secondScore", "thirdScore": "thirdScore", "firstClosestGTC": "firstGTC", "secondClosestGTC": "secondGTC", "thirdClosestGTC": "thirdGTC"})
            for count, pdbFile in enumerate(os.listdir(sourceDir)):
                if pdbFile.endswith(".pdb"):
                    pdbID = os.path.splitext(os.path.basename(pdbFile))[0]
                    print(f'Currently processing: {pdbID}\nProgress: {count+1} out of {len(os.listdir(sourceDir))}\t Progress - {int((count/len(os.listdir(sourceDir))*100))}%')
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
                        
                        indexMatch = Find(glycosmosData, "Sequence", privateerWURCS)
                        if(indexMatch != "Not Found"):
                                glytoucanID = glycosmosData[indexMatch]["AccessionNumber"]
                                glycosmosWURCS = glycosmosData[indexMatch]["Sequence"]
                        else: 
                                possibleHits = FindClosestMatches(glycosmosData, privateerWURCS)
                                writer.writerow({"pdbID": pdbID, "Residue": residueInfo, "Chain": chainInfo, "ClientWURCS": privateerWURCS, "firstClosest": possibleHits[0]['Sequence'], "secondClosest": possibleHits[1]['Sequence'], "thirdClosest": possibleHits[2]['Sequence'], "firstScore": possibleHits[0]['Score'], "secondScore": possibleHits[1]['Score'], "thirdScore": possibleHits[2]['Score'], "firstClosestGTC": possibleHits[0]['GTC_ID'], "secondClosestGTC": possibleHits[1]['GTC_ID'], "thirdClosestGTC": possibleHits[2]['GTC_ID']})


                        # stringMatch = "TRUE" if privateerWURCS == glycosmosWURCS else "FALSE"
                        
                        # writer.writerow({"pdbID": pdbID, "Residue": residueInfo, "Chain": chainInfo, "ClientWURCS": privateerWURCS, "ServerWURCS": glycosmosWURCS, "stringMatch": stringMatch, "glytoucanID": glytoucanID})

                        temporaryListOfStrings = temporaryListOfStrings[2:]
tick = datetime.now()
diff = tick - tock
print(f'\nFinished analysing Glycan sequences of all models in root/structures directory!\nTime elapsed: {diff.total_seconds()} seconds')
            
