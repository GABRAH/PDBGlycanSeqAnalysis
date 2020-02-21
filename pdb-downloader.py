import os
import csv
import shutil
import pypdb as pdb
import privateer

# function to create/delete existing folders
def CreateFolder(path):
    if not os.path.exists(path):
        os.makedirs(path)
    # else:
    #     shutil.rmtree(path)           # Removes all the subdirectories!
    #     os.makedirs(path)

def WriteFile(directory, filename, content):
    with open(os.path.join(directory,filename), "w") as file:
        file.write(content)

# function that generates an array of pdb ids from input file
def GenerateListOfStructures(filepath, filename):
    structureList = []
    with open(os.path.join(filepath, filename)) as csv_file:
        next(csv_file) # skip header line
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            structureList.append(row[1])
    return structureList


ignoreFileList = ["cryoem_n_glycosylated.csv", "xray_n_glycosylated.csv"]

rootDir = os.getcwd()
structureListDir = os.path.join(rootDir, "structures")


for structureListFile in os.listdir(structureListDir):
    if structureListFile.endswith(".csv") and structureListFile not in ignoreFileList:
        print(structureListFile)
        structureListFileName = os.path.splitext(os.path.basename(structureListFile))[0]
        outputDir = os.path.join(structureListDir, structureListFileName)
        CreateFolder(outputDir)
        currentStructureList = GenerateListOfStructures(structureListDir, structureListFile)
        for count, pdbID in enumerate(currentStructureList):
            print(f'Currently downloading: {pdbID}\nProgress: {count} out of {len(currentStructureList)}\t Progress - {int((count/len(currentStructureList)*100))}%')
            newFileName = pdbID + '.pdb'
            currentPDB = pdb.get_pdb_file(pdbID, filetype='pdb', compression=False)
            WriteFile(outputDir, newFileName, currentPDB)
       







