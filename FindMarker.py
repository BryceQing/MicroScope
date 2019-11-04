import cv2
import cv2.aruco as aruco
import numpy as np
import glob


# TODO Refactor the project

cap = cv2.VideoCapture(0)
originImg = cv2.imread('JointPhoto/Level3.jpg')
idsArray = [1]
imgHeight, imgWidth = originImg.shape[:2]

# imgCenterX, imgCenterY = imgWidth // 2, imgHeight // 2
# scaleWidth, scaleHeight = imgWidth // 2, imgHeight // 2

microscope_w, microscope_h = 240, 240 # The size of viewport of microscope. 显微镜视口大小


cv2.namedWindow('MicroScope', cv2.WINDOW_NORMAL) # Setting the name of window 设置窗口名称
cv2.resizeWindow('MicroScope', microscope_w, microscope_h) # Setting the window size 设置窗口大小
cv2.moveWindow('MicroScope', 500, 500); #Setting the window position 设置窗口位置

def FindMark(img, marktype = aruco.DICT_6X6_250):
    
    """[Find mark corners]

    Arguments:
        img {[numpy.array]} -- [The input image 摄像头输入图像]
    
    Returns:
        (centerX, centerY) {[tuple]} --[The center position of mark 标记mark中心位置]
        markId {[Number]} --[id of mark 标记Mark的id]
        isFind {[Boolean]} --[Wheather find the mark 是否找到mark]
        
    """
    
    aruco_dict = aruco.Dictionary_get(marktype)
    parameters = aruco.DetectorParameters_create()
    parameters.adaptiveThreshConstant = True
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, rejectedImgPoints = aruco.detectMarkers( gray, aruco_dict, parameters = parameters)
    centerX, centerY, markId, isFind = None, None, None, False
    if ids is not None and corners is not None:
        ids = ids.flatten()
        for i in range(len(ids)):
            if ids[i] in idsArray:
                aruco.drawDetectedMarkers(img, corners)
                centerX = int(corners[i][0][0][0] + corners[i][0][1][0] + corners[i][0][3][0] + corners[i][0][2][0]) / 4
                centerY = int(corners[i][0][0][1] + corners[i][0][1][1] + corners[i][0][3][1] + corners[i][0][2][1]) / 4
                markId, isFind = ids[i], True
    cv2.imshow('Find mark image:', img)
    return (centerX, centerY), markId, isFind



imgTopX, imgTopY = 0, 0 # Original image top-left position. 原始图片左上角坐标
imgBottomX, imgBottomY = imgWidth, imgHeight # Original image bottom-right position. 原始图片右下角坐标
viewWidth, viewHeight = None, None # Now viewport size. 图片映射视口大小

if imgWidth > imgHeight:
    img_viewport_scale =  microscope_w / imgWidth 
    viewTopX, viewTopY = 0, (microscope_h - int(imgHeight * img_viewport_scale )) // 2
    viewBottomX, viewBottomY = microscope_w, (microscope_h + int(imgHeight * img_viewport_scale)) // 2
    viewWidth, viewHeight = microscope_w // 2, imgHeight * (microscope_w // 2) / imgWidth
else:
    img_viewport_scale =  microscope_h / imgHeight
    viewTopX, viewTopY = (microscope_w - int(imgWidth * img_viewport_scale)) // 2, 0
    viewBottomX, viewBottomY = (microscope_w + int(imgWidth * img_viewport_scale )) // 2, microscope_h
    viewWidth, viewHeight = imgWidth * (microscope_h // 2) / imgHeight, microscope_h // 2


result_img = np.zeros((microscope_w, microscope_h, 3), np.uint8) + 255
update, First = False, True
nowScale = 0




#FIXME Calibrate the mark detection rate
def drawSpeimens(imgId, *offset, scale):
    
    global imgWidth, imgHeight
    global viewWidth, viewHeight
    global viewTopX, viewTopY, viewBottomX, viewBottomY
    global First, update, nowScale, result_img
    
    imgTopX, imgTopY, imgBottomX, imgBottomY = 0, 0, imgWidth, imgHeight
    
    
    if abs(offset[0]) > 4.0 or abs(offset[1]) > 4.0:
     # Fault tolerance rate， when the mark idle, it always has litte offset, so we should‘t update viewport.
     # 容错率 当图片静止不动的时候识别mark依然会出现微小移动， 所以不进行更新.
        update = True
    else:
        update = False
    
    if First: 
        First, update = False, True
        

    viewTopX -= offset[0]  # offsetX
    viewBottomX -= offset[0] #offsetX    
    viewTopY -= offset[1] # offsetY
    viewBottomY -= offset[1] # offsetY
 
  
    if scale != 0 and nowScale + scale >= 0: # Scale the image, note: You can only shrink to 1 scale . 进行放缩 注意图片不能无限制缩小，仅能缩小到最开始图像
            nowScale += scale
            viewTopX -= scale * viewWidth
            viewBottomX += scale * viewWidth
            viewTopY -= scale * viewHeight
            viewBottomY += scale * viewHeight
            update = True
    
    showTopX, showTopY, showBottomX, showBottomY = map(int, (viewTopX, viewTopY, viewBottomX, viewBottomY))
    
    if imgWidth > imgHeight:
        view_port_scale = imgWidth / (viewBottomX - viewTopX)
    else:
        view_port_scale = imgHeight / (viewBottomY - viewTopY)
    
    
    if viewTopX < 0:
        imgTopX = int(abs(viewTopX) * view_port_scale)
        showTopX = 0
    if viewTopY < 0:
        imgTopY = int(abs(viewTopY) * view_port_scale)
        showTopY = 0
    if viewBottomX >= microscope_w:
        imgBottomX -= int((viewBottomX - microscope_w) * view_port_scale)
        showBottomX = microscope_w
    if viewBottomY >= microscope_h:
        imgBottomY -= int((viewBottomY - microscope_h) * view_port_scale)
        showBottomY = microscope_h
    
    if update:
        roi = originImg[imgTopY: imgBottomY, imgTopX: imgBottomX]  # Get the region of original image
        view_roi = cv2.resize(roi, (showBottomX - showTopX, showBottomY - showTopY)) # Resize to view_port size
        result_img = np.zeros((microscope_w, microscope_h, 3), np.uint8) + 255
        result_img[showTopY: showBottomY, showTopX: showBottomX] = view_roi
        
    cv2.imshow('MicroScope', result_img)


lastCenter = None # Center position of mark 记录找到mark中心位置
Confirm = False # Confirm mark position 确定mark中心位置为当前位置
dic_scale_scope = { # The key-value scale of microscope 调节显微镜的键值对
    ord('w'): 1,
    ord('s'): -1,
    ord('e'): 4, 
    ord('d'): -4,
    ord('r'): 10,
    ord('f'): -10,
}

while True:
    _, frame = cap.read()
    center, tempIds, isFind = FindMark(frame)
    keyBoard = cv2.waitKey(5)
    if keyBoard == ord('='):
        Confirm = True # Confim. 确定当前位置为mark的起始位置
        lastCenter = center # Record. 记录当前mark中心位置
        print('Confirm the mark')

    if Confirm and isFind:
        # When you confirm the mark and the mark is found in current frame you can move and scale the scope. 
        # 如果你已经确定mark初始位置而且当前帧也要找到mark则进行移动、放缩操作
        if keyBoard in dic_scale_scope: # If you press scale key. 按下缩放键进行缩放
            drawSpeimens(tempIds, lastCenter[0] - center[0], lastCenter[1] - center[1], scale = dic_scale_scope[keyBoard]) 
        else:
            drawSpeimens(tempIds, lastCenter[0] - center[0], lastCenter[1] - center[1] , scale = 0) 
                   
        lastCenter = center        
    if keyBoard == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()