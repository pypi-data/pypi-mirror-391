from os import listdir, path, makedirs
from shutil import copy

imgExtension = [".jpeg", ".jpg", ".png", ".bmp"]


def Yolo2Classify(datasetDir: str, exportDir: str):
    
    errorCount = 0
    errorList = []

    imagesDir = path.join(datasetDir, "images")
    labelsDir = path.join(datasetDir, "labels")

    processedCount = 0
    totalLabel = len(listdir(labelsDir))
    print(f"Found {totalLabel} files.")

    if(path.exists(imagesDir) == False):
        raise Exception("Images directory does not exits in dataset directory.")
    if(path.exists(labelsDir) == False):
        raise Exception("Labels directory does not exits in dataset directory.")
    if(path.exists(exportDir == False)):
        print("Export directory does not exits, try create new one!")
        makedirs(exportDir, exist_ok= True)
    
    for labelFileName in listdir(labelsDir):
        
        imgFilePath = ""
        for ext in imgExtension:
            
            if( path.exists( path.join(imagesDir, labelFileName[:-4] + ext))):
                imgFilePath = path.join(imagesDir, labelFileName[:-4] + ext)
                break
        
        if(imgFilePath == ""):
            errorCount += 1
            errorList.append(labelFileName)
            print(f"Image path: {imgFilePath} not found!")

        else:
            
            imgFileName = path.basename(imgFilePath)
            rawImgPath = path.join(imagesDir, imgFileName)
            with open(path.join(labelsDir, labelFileName)) as file:

                lines = file.readlines()
                
                if(len(lines) == 0):
                    exportImageDir = path.join(exportDir, "Background")
                    exportImagePath = path.join(exportImageDir, imgFileName)

                    if(path.exists(exportImageDir == False)):
                        makedirs(exportImageDir, exist_ok= True)

                    copy(rawImgPath, exportImagePath)

                else:

                    try:

                        for line in lines:
                            
                            indexLabel = line.split(' ')[0]
                            exportImageDir = path.join(exportDir, indexLabel)
                            exportImagePath = path.join(exportImageDir, imgFileName)

                            if(path.exists(exportImageDir == False)):
                                makedirs(exportImageDir, exist_ok= True)

                            if(path.exists(exportImagePath)):
                                continue
                            else:
                                copy(rawImgPath, exportImagePath)
                    
                    except Exception as ex:
                        print(f"Error in extract label format: {labelFileName}. Msg: {ex}")
                        errorCount +=1
                        errorList.append(labelFileName)
        
        processedCount +=1
        print(f"Processed {processedCount}/{totalLabel}")
    print(f"Process Done! Error Count: {errorCount}")
    print(f"Label Error: ")
    if(errorCount > 0 ):
        for labelError in errorList :
            print(labelError)
        