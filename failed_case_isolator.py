import os
import pandas as pd



def GetDirectories(currentdirectory):
    directories = []
    for directory in os.listdir(currentdirectory):
        if os.path.isdir(os.path.join(currentdirectory, directory)):
            directories.append(directory)
    return directories




rootDir = os.getcwd()

structureListDir = os.path.join(rootDir, "structures")
resultsDir = os.path.join(rootDir, "results/offline")
srcFileDirs = GetDirectories(resultsDir)

ignoreDirectoryList = ["cryoem_n_glycosylated", "xray_n_glycosylated"]

for directory in srcFileDirs:
    if directory not in ignoreDirectoryList:
        sourceDir = os.path.join(resultsDir, directory)
        filename = directory + "_final.csv"
        for outputFile in os.listdir(sourceDir):
            if outputFile.endswith(".csv"):
                data = pd.read_csv(os.path.join(sourceDir, outputFile))
                df = pd.DataFrame(data, columns=["PDB_ID", "stringMatch"])
                is_False = df.loc[df["stringMatch"] == False]
                pdbIDs = is_False.drop(columns=["stringMatch"])
                pdbIDs = pdbIDs.drop_duplicates()
                pdbIDs.reset_index(drop=True, inplace=True)
                pdbIDs["index"] = pdbIDs.index
                outputDataFrame = pdbIDs[["index", "PDB_ID"]]
                outputDataFrame.to_csv(os.path.join(structureListDir, filename), encoding="utf-8", index=False)