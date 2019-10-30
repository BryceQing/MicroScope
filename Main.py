import cv2
import glob
import re




class MicroScope:
    
    def __init__(self, dir, changeLevel = 5):
        """[Constructor]        
        Arguments:
            dir {[string]} -- [specimen direction (标本路径)]
            changeLevel {[int]} --[change level (每个图片放大到几倍时用下张照片)]
        """
        
        self.dicLeaves = {}
        self.dicScale = {}        
        self.nowLevel = 1
        self.changeLevel = changeLevel
        self._readPhotos(dir)
        self._initCV()
        
        

    def _readPhotos(self, dir):
        """[Read specimen photos from direction (从标本路径中读取照片)]
        
        Arguments:
            dir {[string]} -- [specimen direction(标本路径)]
        """
        #Put all files in the corresponding directories.
        LeavesFiles = glob.glob(dir + '*.jpg')
        pattern = re.compile(r'.*?leaves\\(\d+).jpg')

        #Level from 1 to N
        for leaf in LeavesFiles:
            level = int(re.match(pattern, leaf).group(1))
            self.dicLeaves[level] = cv2.imread(leaf)
            self.dicScale[level] = 1


    def _initCV(self):
        """[Init opencv configuration (初始化opencv配置)]
        """
        self.winHeight, self.winWidth = self.dicLeaves[self.nowLevel].shape[:2]
        cv2.namedWindow('MicroScope', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('MicroScope', self.winWidth, self.winHeight)
        self.centerX, self.centerY = self.winWidth // 2, self.winHeight // 2        


    def run(self):
        """[Main loop]
        """
        while True:    
            k = cv2.waitKey(30) & 0xFF
            if k == ord('q'): 
                # Press q to quit.
                break
            elif k == ord('='):
                 # Press '= +' to add 1 scale 按键盘上的'=+'键放大1倍当前样本
                if self.dicScale[self.nowLevel] + 1 > self.changeLevel:
                    if self.nowLevel < len(self.dicLeaves):
                            self.nowLevel += 1 #Update the leaf level
                            self.dicScale[self.nowLevel] = 1
                else:
                    self.dicScale[self.nowLevel] += 1
            elif k == ord('-'):
                # Press '-' to minus scale 按键盘上的'-'键缩小1倍当前样本
                if self.dicScale[self.nowLevel] - 1 < 1:
                    if self.nowLevel > 1:
                        self.nowLevel -= 1
                        self.dicScale[self.nowLevel] = self.changeLevel
                        
                else:
                    self.dicScale[self.nowLevel] -= 1
            elif k == ord('+'): 
                #Press shift '=+' to add 10 scale 按键盘上的shift + '=+'键放大10倍当前样本
                if self.nowLevel < len(self.dicLeaves):
                    self.nowLevel += 1
                    self.dicScale[self.nowLevel] = 1
            elif k == ord('_'):
                # Press shift + '-' to minus 10 scale 按键盘上的shift + '-'键缩小10倍当前样本
                if self.nowLevel > 1:
                    self.nowLevel -= 1
                    self.dicScale[self.nowLevel] = self.changeLevel
            
                
            self.showImage(self.nowLevel)            
        cv2.destroyAllWindows()
        
    
    def showImage(self, level):
        width, height = int(self.winWidth / self.dicScale[level] / 2), int(self.winHeight / self.dicScale[level] / 2)
        roiImage = self.dicLeaves[level][self.centerY - height : self.centerY + height, self.centerX - width: self.centerX + width]
        cv2.imshow('MicroScope', roiImage)



if __name__ == '__main__':    
    
    microScope = MicroScope(dir = './leaves/', changeLevel = 5)
    microScope.run()
