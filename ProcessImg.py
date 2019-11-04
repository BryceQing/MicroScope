import cv2
import glob

imgFiles = glob.glob('Specimens/' + '*.jpg')
for imgFile in imgFiles:
    fileName = imgFile[imgFile.rfind('\\'):].replace('\\', '')
    print('imgFile', fileName)
    
    img = cv2.imread(imgFile)
    # cv2.imshow('debug file', img)
    # cv2.waitKey(0)
    imgH, imgW = img.shape[:2]
    if imgW == 512:
        newImgH = 80
        newImgW = int( imgH * 80 / 512)
    else:
        newImgW = 80
        newImgH = int( imgW * 80 / 512)
        
    processImg = cv2.resize(img, (newImgH, newImgW), interpolation = cv2.INTER_AREA)
    cv2.imwrite('SpecimensProcessed/' + fileName, processImg )
        