import os
import csv
import shutil
import pandas as pd
from privateer import privateer_core as pvt

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


def generateDataFrame(path):
    dataFrame = pd.read_csv(path)
    return dataFrame 

def generateChainLengthColumn(dataframe):
    wurcsColumn = dataframe['privateerWURCS']
    for index, row in dataframe.iterrows():
        splitString = wurcsColumn[index].split(',', 2)
        numResidues = splitString[1]
        dataframe.loc[index, 'TotalResidues'] = numResidues
    return dataframe


rootDir = os.getcwd()
resultsDir = os.path.join(rootDir, "results/offline")
outputFileName = "placeholder.csv"

# ignoreDirectoryList = ["cryoem_n_glycosylated", "xray_n_glycosylated", "cryoem_n_glycosylated_failed"]
ignoreDirectoryList = []
ignoreFileList = []

for resultsListDirectories in os.listdir(resultsDir):
    techniqueDirectory = os.path.join(resultsDir, resultsListDirectories)
    for resultsFile in os.listdir(techniqueDirectory):
        if resultsFile.endswith(".csv") and resultsFile not in ignoreFileList:
            df = generateDataFrame(os.path.join(techniqueDirectory, resultsFile))
            cleanDataFrame = df.loc[:, ['PDB_ID', 'privateerWURCS', 'GTCIDFOUND', 'GLYCONNECTIDFOUND']]
            chainLengthDataFrame = generateChainLengthColumn(cleanDataFrame)
            print(chainLengthDataFrame.head())
            
        
        
        
        
        
        
        #    print(f'GlyTouCan ID found for {resultsListDirectories}: {len(df[df["GTCIDFOUND"] == True])}')
        #    print(f'GlyTouCan ID NOT found for {resultsListDirectories}: {len(df[df["GTCIDFOUND"] == False])}')
        #    print(f'GlyConnect ID found for {resultsListDirectories}: {len(df[df["GLYCONNECTIDFOUND"] == True])}')
        #    print(f'GlyConnect ID NOT found for {resultsListDirectories}: {len(df[df["GLYCONNECTIDFOUND"] == False])}')

