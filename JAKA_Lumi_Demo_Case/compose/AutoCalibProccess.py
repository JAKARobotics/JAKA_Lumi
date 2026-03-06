
'''
标定：眼在手外
'''

from utilfs.handToEyeCalibration import *
import cv2
from OrbbecSDK.orbbecCamera import Camera
import getch
from utilfs.jaka import *
from utilfs.tools import loadJsonFile,findCorners

PI=3.1415926



mapJsonData = loadJsonFile('./conf/userCmdControl.json')

boardRowNums=mapJsonData["calibrateParams"]["boardRowNums"]
boardCowNums = mapJsonData["calibrateParams"]["boardCowNums"]
boardLength = mapJsonData["calibrateParams"]["boardLength"]

CalibrateImageSaveDir = mapJsonData["calibrateParams"]["CalibrateImageSaveDir"]
if not os.path.exists(CalibrateImageSaveDir):
    os.makedirs(CalibrateImageSaveDir)

save_path = os.path.join(CalibrateImageSaveDir, 'robotTcpPos.txt')
print('------:',save_path)

tcp = JAKA(mapJsonData["calibrateParams"]["robotIP"])
oberrecCamera = Camera()

startIndex=0
robotPoses = []
calibrateImages = []
print('--------------请按下k进行数据采集-------')
while True:
    key = getch.getch()  # 读取按键
    keystr = key
    print(keystr)

    if keystr == 'k':
        print("开始采集数据...")
        currentTcpPos = tcp.get_tcp_pos()
        print("currentTcpPos: ",currentTcpPos)

        color_image = oberrecCamera.getColorImage()
        print("get color_image  success.")

        if findCorners(color_image,boardRowNums,boardCowNums):
            robotPoses.append(currentTcpPos)
            calibrateImages.append(color_image)
            cv2.imwrite(os.path.join(CalibrateImageSaveDir, "{:04d}.png".format(int(startIndex))), color_image)
            startIndex+=1
            print("本次数据采集成功")
        else:
            print("舍弃本次采集...")

    if keystr == 'p':
        print("开始标定...")
        if len(calibrateImages)==len(robotPoses):
            print("数据一致,开始标定")
            np.savetxt(save_path,robotPoses, fmt='%f', delimiter=',')
            print("位姿保存成功...")
            calibrator = Calibration(boardRowNums, boardCowNums, boardLength)
            calibrator.process(calibrateImages, robotPoses)
        else:
            print("图像和位姿数量不一致...")

    if keystr == 'q':
        break












