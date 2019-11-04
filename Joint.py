import cv2
import glob
import numpy as np
let level = 'Level1'
imgFiles = glob.glob('Specimens/'+ level + '/' + '*.jpg')
jointImage = None

def getPos(fileName):
    x, y = fileName.split('x')
    return map(int, (x, y))

dicImage = {}
row, col = 0, 0

for imgFile in imgFiles:
    fileName = imgFile.replace('.jpg', '')
    x, y = getPos(fileName[fileName.rfind('\\') + 1:])
    row, col = max(row, y), max(col, x)
    img = cv2.imread(imgFile)
    dicImage[(x, y)] = img

# print(row, col)
resImg = None
dicCol = {}
for i in range(col + 1):
    tempImg = None
    flag = False
    for j in range(row + 1):
        if not flag:
            tempImg = dicImage[(i, j)]
            flag = True
        else:
            tempImg = np.vstack([tempImg, dicImage[i, j]])
    dicCol[i] = tempImg
    
for i in range(len(dicCol)):
    if resImg is not None:
        resImg = np.hstack([resImg, dicCol[i]])
    else:
        resImg = dicCol[i]

cv2.imwrite('JointPhoto/' + level + '.jpg', resImg)
    
    
    
    
    
    # processImg = cv2.resize(img, (newImgH, newImgW), interpolation = cv2.INTER_AREA)
    # cv2.imwrite('SpecimensProcessed/' + fileName, processImg )
        