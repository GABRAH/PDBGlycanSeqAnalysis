import os
import csv
import shutil
import re
from privateer import privateer_core as pvt
import json
from datetime import datetime

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


rootDir = os.getcwd()
structureListDir = os.path.join(rootDir, "structures")
srcFileDirs = GetDirectories(structureListDir)
resultsDir = os.path.join(rootDir, "results/offline")
dataDir = os.path.join(rootDir, "data")
outputFileName = "all_chains.csv"

# ignoreDirectoryList = ["cryoem_n_glycosylated", "xray_n_glycosylated", "cryoem_n_glycosylated_failed"]
ignoreDirectoryList = []
dataFileName = "glycosmos_data_2020-05-05.json"

glycosmosData = GetJSON(os.path.join(dataDir, dataFileName))
print(type(glycosmosData))

tock = datetime.now()
for directory in srcFileDirs:
    if directory not in ignoreDirectoryList:
        sourceDir = os.path.join(structureListDir, directory)
        outputDir = os.path.join(resultsDir, directory)
        CreateFolderAndFile(outputDir, outputFileName)
        with open(os.path.join(outputDir, outputFileName), "a", newline="") as csvfile:
            fieldnames = ["pdbID", "Residue", "Chain", "ClientWURCS", "ServerWURCS", "stringMatch", "glytoucanID"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({"pdbID": "PDB_ID", "Residue": "Residue", "Chain": "Chain", "ClientWURCS": "privateerWURCS", "ServerWURCS": "glycosmosWURCS", "stringMatch": "stringMatch", "glytoucanID": "glytoucanID"})
            for count, pdbFile in enumerate(os.listdir(sourceDir)):
                if pdbFile.endswith(".pdb"):
                    pdbID = os.path.splitext(os.path.basename(pdbFile))[0]
                    print(f'Currently processing: {pdbID}\nProgress: {count+1} out of {len(os.listdir(sourceDir))}\t Progress - {int((count/len(os.listdir(sourceDir))*100))}%')
                    pdbFilePath = os.path.join(sourceDir, pdbFile)
                    totalWURCS = pvt.print_wurcs(pdbFilePath)
                    
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
                                glytoucanID = "N/A"
                                glycosmosWURCS = "Not Found"
                                # stringMatch = "TRUE" if privateerWURCS == glycosmosWURCS else "FALSE"
                                # writer.writerow({"pdbID": pdbID, "Residue": residueInfo, "Chain": chainInfo, "ClientWURCS": privateerWURCS, "ServerWURCS": glycosmosWURCS, "stringMatch": stringMatch, "glytoucanID": glytoucanID})
                        stringMatch = "TRUE" if privateerWURCS == glycosmosWURCS else "FALSE"
                        writer.writerow({"pdbID": pdbID, "Residue": residueInfo, "Chain": chainInfo, "ClientWURCS": privateerWURCS, "ServerWURCS": glycosmosWURCS, "stringMatch": stringMatch, "glytoucanID": glytoucanID})

                        temporaryListOfStrings = temporaryListOfStrings[2:]
tick = datetime.now()
diff = tick - tock
print(f'\nFinished analysing Glycan sequences of all models in root/structures directory!\nTime elapsed: {diff.total_seconds()} seconds')
            
