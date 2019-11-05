import cv2
import glob
import numpy as np


class Joint:
    def __init__(self, input_path, output_path):
        
        imgFiles = glob.glob(input_path)
        dicImage = {}
        row, col = 0, 0
        
        for imgFile in imgFiles:
            fileName = imgFile.replace('.jpg', '')
            x, y = self.getPos(fileName[fileName.rfind('\\') + 1:])
            row, col = max(row, y), max(col, x)
            img = cv2.imread(imgFile)
            dicImage[(x, y)] = img
        
        self.Merge(dicImage, row, col, output_path)
            
    

    
    def getPos(self, fileName):
        x, y = fileName.split('x')
        return map(int, (x, y))
    
    def Merge(self, dicImage, row, col, output_path):
        
        resImg = None
        dicCol = {}
        for i in range(col + 1):
            tempImg = None
            for j in range(row + 1):
                if tempImg is not None:
                    tempImg = np.vstack([tempImg, dicImage[i, j]])
                else:
                    tempImg = dicImage[(i, j)]
                dicCol[i] = tempImg
            
        for i in range(len(dicCol)):
            if resImg is not None:
                resImg = np.hstack([resImg, dicCol[i]])
            else:
                resImg = dicCol[i]

        cv2.imwrite(output_path, resImg)
        
if __name__ == '__main__':
    category = 'SpinalCord'
    input_path = 'Specimens/'+ category + '/' + '*.jpg'
    output_path = 'JointPhoto/' + category + '.jpg'
    joint = Joint(input_path, output_path)
    





    
    # processImg = cv2.resize(img, (newImgH, newImgW), interpolation = cv2.INTER_AREA)
    # cv2.imwrite('SpecimensProcessed/' + fileName, processImg )
        