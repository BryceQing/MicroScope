import cv2
import cv2.aruco as aruco
import numpy as np
import glob
import sys


class MicroScope:

    def __init__(self, micro_w, micro_h, micro_posX, micro_posY, dic_specimen_id ):
        """[Init the microscope 初始化显微镜对象]
        
        Arguments:
            micro_w {[Number]} -- [The width of microscope 显微镜视口宽度]
            micro_h {[Number]} -- [The height of microsocpe 显微镜视口高度]
            micro_posX {[Number]} -- [The x postion of microscope 显微镜视口x坐标]
            micro_posY {[Number]} -- [The y position of microscope 显微镜视口y坐标]
            dic_specimen_id {[dict]} -- [The key-value : id: specimen 键值对: 图片id和标本路径]
        
        """ 
        
        # Init opencv configuration 配置opencv相关信息
        self.cap = cv2.VideoCapture(0)
        
        # Detect the id and show the correspongding specimen photo 检测mark id并显示对应标本图片
        self.dic_specimen_id = dic_specimen_id
                
        # The size of viewport of microscope. 显微镜视口大小
        self.microscope_w, self.microscope_h = micro_w, micro_h
        # Setting the name of window 设置窗口名称
        cv2.namedWindow('MicroScope', cv2.WINDOW_NORMAL)
        # Setting the window size 设置窗口大小
        cv2.resizeWindow('MicroScope', self.microscope_w, self.microscope_h)
        # Setting the window position 设置窗口位置
        cv2.moveWindow('MicroScope', micro_posX, micro_posY)
        
        
        # self.initViewPort()
        
    
    def loadImage(self, specimen_id):
        """[Load the speciment 加载标本]
        
        Arguments:
            specimen_id {[Number]} -- [Specimen id]
        """
        
        self.originImg = cv2.imread(self.dic_specimen_id[specimen_id])
        self.specimen_id = specimen_id
        self.imgHeight, self.imgWidth = self.originImg.shape[:2]
        self.initViewPort()
        
    
    
    def initViewPort(self):
        """[Init microscope viewport configuration 配置显示视口相关信息]
        """
        # self.imgTopX, self.imgTopY = 0, 0  # Original image top-left position. 原始图片左上角坐标
        # self.imgBottomX, self.imgBottomY = self.imgWidth, self.imgHeight # Original image bottom-right position. 原始图片右下角坐标
        self.viewTopX, self.viewTopY, self.viewBottomX, self.viewBottomY = None, None, None, None
        self.viewWidth, self.viewHeight = None, None  # Now viewport size. 当前视口大小

        if self.imgWidth > self.imgHeight:
            img_viewport_scale = self.microscope_w / self.imgWidth
            self.viewTopX, self.viewTopY = 0, (self.microscope_h - int(self.imgHeight * img_viewport_scale)) // 2
            self.viewBottomX, self.viewBottomY = self.microscope_w, ( self.microscope_h + int(self.imgHeight * img_viewport_scale)) // 2
            self.viewWidth, self.viewHeight = self.microscope_w // 2, self.imgHeight * (self.microscope_w // 2) / self.imgWidth
        else:
            img_viewport_scale = self.microscope_h / self.imgHeight
            self.viewTopX, self.viewTopY = (self.microscope_w - int(self.imgWidth * img_viewport_scale)) // 2, 0
            self.viewBottomX, self.viewBottomY = ( self.microscope_w + int(self.imgWidth * img_viewport_scale)) // 2, self.microscope_h
            self.viewWidth, self.viewHeight = self.imgWidth *  (self.microscope_h // 2) / self.imgHeight, self.microscope_h // 2


        self.result_img = np.zeros((self.microscope_w, self.microscope_h, 3), np.uint8) + 255
        self.update, self.First = False, True
        self.nowScale = 0

    def FindMark(self, img, marktype = aruco.DICT_6X6_250):
        
        """[Find mark corners]

        Arguments:
            img {[numpy.array]} -- [The input image 摄像头输入图像]
            marktype {[any]} -- [The dict of aurco mark Aruco mark的字典参数]
        Returns:
            (centerX, centerY) {[tuple]} --[The center position of mark 标记mark中心位置]
            markId {[Number]} --[id of mark 标记Mark的id]
            isFind {[Boolean]} --[Wheather find the mark 是否找到mark]

        """

        aruco_dict = aruco.Dictionary_get(marktype)
        parameters = aruco.DetectorParameters_create()
        parameters.adaptiveThreshConstant = True

        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters = parameters)
        centerX, centerY, markId, isFind = None, None, None, False
        if ids is not None and corners is not None:
            ids = ids.flatten()
            for i in range(len(ids)):
                if ids[i] in self.dic_specimen_id:
                    aruco.drawDetectedMarkers(img, corners)
                    centerX = int(corners[i][0][0][0] + corners[i][0][1][0] + corners[i][0][3][0] + corners[i][0][2][0]) / 4
                    centerY = int(corners[i][0][0][1] + corners[i][0][1][1] + corners[i][0][3][1] + corners[i][0][2][1]) / 4
                    markId, isFind = ids[i], True
        cv2.imshow('Find mark image:', img)
        return (centerX, centerY), markId, isFind


    # FIXME Calibrate the mark detection rate
    def drawSpeimens(self, imgId, *offset, scale):
        """[Draw the viewport of microscope 画出显微镜显示的图像]
        
        Arguments:
            imgId {[Number]} -- [The id of marker 标记的id]
            *offset{[tuple]} -- [The offset of mark Mark移动位移]
            scale {[Number]} -- [Scale time 放缩的倍数]
        """
        
        imgTopX, imgTopY, imgBottomX, imgBottomY = 0, 0, self.imgWidth, self.imgHeight
        
        # Fault tolerance rate， when the mark idle, it always has litte offset, so we should‘t update viewport.
        # 容错率 当图片静止不动的时候识别mark依然会出现微小移动， 所以不进行更新.
        if abs(offset[0]) > 4.0 or abs(offset[1]) > 4.0:
            self.update = True
        else:
            self.update = False

        if self.First:
            self.First, self.update = False, True

        self.viewTopX -= offset[0]  # offsetX
        self.viewBottomX -= offset[0]  # offsetX
        self.viewTopY -= offset[1]  # offsetY
        self.viewBottomY -= offset[1]  # offsetY

        # Scale the image, note: You can only shrink to 1 scale . 进行放缩 注意图片不能无限制缩小，仅能缩小到最开始图像
        if scale != 0 and self.nowScale + scale >= 0:
            self.nowScale += scale
            self.viewTopX -= scale * self.viewWidth
            self.viewBottomX += scale * self.viewWidth
            self.viewTopY -= scale * self.viewHeight
            self.viewBottomY += scale * self.viewHeight
            self.update = True

        showTopX, showTopY, showBottomX, showBottomY = map(int, (self.viewTopX, self.viewTopY, self.viewBottomX, self.viewBottomY))

        if self.imgWidth > self.imgHeight:
            view_port_scale = self.imgWidth / (self.viewBottomX - self.viewTopX)
        else:
            view_port_scale = self.imgHeight / (self.viewBottomY - self.viewTopY)

        if self.viewTopX < 0:
            imgTopX = int(abs(self.viewTopX) * view_port_scale)
            showTopX = 0
        if self.viewTopY < 0:
            imgTopY = int(abs(self.viewTopY) * view_port_scale)
            showTopY = 0
        if self.viewBottomX >= self.microscope_w:
            imgBottomX -= int((self.viewBottomX - self.microscope_w) * view_port_scale)
            showBottomX = self.microscope_w
        if self.viewBottomY >= self.microscope_h:
            imgBottomY -= int((self.viewBottomY - self.microscope_h) * view_port_scale)
            showBottomY = self.microscope_h

        if self.update:
            # Get the region of original image
            roi = self.originImg[imgTopY: imgBottomY, imgTopX: imgBottomX]
            # Resize to view_port size
            view_roi = cv2.resize(roi, (showBottomX - showTopX, showBottomY - showTopY))
            self.result_img = np.zeros((self.microscope_w, self.microscope_h, 3), np.uint8) + 255
            self.result_img[showTopY: showBottomY, showTopX: showBottomX] = view_roi
        cv2.imshow('MicroScope', self.result_img)



    def run(self, dic_scale_scope):
        """[Loop 运行]
        
        Arguments:
            dic_scale_scope {[dict]]} -- [key-value of keyboard 键盘操作键值对]
        """
        
        lastCenter = None  # Center position of mark 记录找到mark中心位置
        Confirm = False  # Confirm mark position 确定mark中心位置为当前位置
        loadedImg = False # Wheather the image has been loaded 图片是否已经被加载
        
        while True:
            _, frame = self.cap.read()
            center, tempIds, isFind = self.FindMark(frame)
            keyBoard = cv2.waitKey(5)
            if keyBoard == dic_scale_scope['confirm'] and not Confirm:
                Confirm = True  # Confim. 确定当前位置为mark的起始位置
                lastCenter = center  # Record. 记录当前mark中心位置
                print('Confirm the mark')
                self.loadImage(tempIds)
                loadedImg = True
            if Confirm and isFind and loadedImg:
                # When you confirm the mark and the mark is found in current frame you can move and scale the scope.
                # 如果你已经确定mark初始位置而且当前帧也要找到mark则进行移动、放缩操作
                if keyBoard in dic_scale_scope:  # If you press scale key. 按下缩放键进行缩放
                    self.drawSpeimens(tempIds, lastCenter[0] - center[0], lastCenter[1] - center[1], scale=dic_scale_scope[keyBoard])
                else:
                    self.drawSpeimens(tempIds, lastCenter[0] - center[0], lastCenter[1] - center[1], scale=0)
                lastCenter = center
            if keyBoard == dic_scale_scope['quit']:
                break
        self.cap.release()
        cv2.destroyAllWindows()





if __name__ == '__main__':
    
    dic_scale_scope = {  # The key-value scale of microscope 调节显微镜的键值对
        'confirm': ord('='), # Confirm mark 确认mark位置
        'quit': ord('q'), # quit the program 退出 程序
        ord('w'): 1, # magnify 1 time 视野放大一倍
        ord('s'): -1,# shrink 1 time 视野缩小一倍
        ord('e'): 4, # magnify 4 time 视野放大四倍
        ord('d'): -4,# shrink 4 time 视野缩小四倍
        ord('r'): 10,# magnify 10 time 视野放大十倍
        ord('f'): -10,# shrink 10 time 视野缩小十倍
        
    }

    micro_w, micro_h = 240, 240 # The width and height of microscope 显微镜视口宽度和高度
    micro_posX, micro_posY  = 500, 500 # The x postion of microscope 显微镜视口x、y坐标
    
    dic_specimen_id = { # The key-value : id - specimen photo 索引和标本对应
        1 : 'JointPhoto/Onion.jpg', # Onion 洋葱切片
        2 : 'JointPhoto/Paramecium.jpg', # Paramecium.jpg 草履虫标本
        3 : 'JointPhoto/SpinalCord.jpg' # SpinalCord.jpg 脊髓切片
    }
    while True:    
        microScope =  MicroScope(micro_w, micro_h, micro_posX, micro_posY, dic_specimen_id)
        microScope.run(dic_scale_scope)
        del microScope