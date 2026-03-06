import time
import cv2
from OrbbecSDK.orbbecCamera import Camera
from utilfs.jaka import *
from utilfs.tools import loadJsonFile, saveOriginImg, generatorNearPoints, pixel_to_world,vl_ali


step_flag = None # -1：catch 1：put
IO_TOOL = 1 # Grab IO
PI=3.1415926

def kine_caculate(robot, ref_pos,base_loc,world_loc,mapJsonData,step_type):   
    base2objup_pos=None
    objup2obj_pos =None
    grasp_flag =None 
    mv_type = -1 

    grip_loc = tuple(world_loc.tolist() + list(base_loc[3:]))  # A
    # obj cartesian_pose
    grip_loc = list(grip_loc)
    grip_loc[0] += mapJsonData["robotParams"]["RelativeOffset-X"]
    grip_loc[1] += mapJsonData["robotParams"]["RelativeOffset-Y"]

    if step_type == -1:
        # catch
        grip_loc[2] += mapJsonData["robotParams"]["RelativeOffset-Z"]

    elif step_type == 1:
        # put
        grip_loc[2] += mapJsonData["robotParams"]["RelativeOffset-Zput"]

    # obj-up cartesian_pose
    grip_loc_up = grip_loc[:]
    grip_loc_up[2] = grip_loc_up[2] + mapJsonData["robotParams"]["relativeUpMotionHeight"]
    
    grip_loc = tuple(grip_loc)
    grip_loc_up = tuple(grip_loc_up)  

    # base 2 obj 
    # Check which method to use based on what's available in the robot object
    if hasattr(robot, 'kine_inverse_origin'):
        base2obj_pos = robot.kine_inverse_origin(ref_pos, grip_loc)
    else:
        base2obj_pos = robot.kine_inverse(ref_pos, grip_loc)
    
    # base 2 obj-up
    if hasattr(robot, 'kine_inverse_origin'):
        base2objup_pos = robot.kine_inverse_origin(ref_pos, grip_loc_up)
    else:
        base2objup_pos = robot.kine_inverse(ref_pos, grip_loc_up)
   
    # if base2obj-up faluire, turn to base2a
    if base2objup_pos[0]!=0:
        grasp_flag= base2obj_pos[0]
        mv_type = 1
    
    # if base2obj-up success, turn to obj-up2obj
    elif  base2objup_pos[0]==0:
        if hasattr(robot, 'kine_inverse_origin'):
            objup2obj_pos = robot.kine_inverse_origin(base2objup_pos[1], grip_loc)
        else:
            objup2obj_pos = robot.kine_inverse(base2objup_pos[1], grip_loc)
            
        if objup2obj_pos[0]==0:
            grasp_flag= objup2obj_pos[0]
            mv_type = 2
        else:
            grasp_flag = base2obj_pos[0] 
            mv_type = 1
    return mv_type,grip_loc,grip_loc_up,base2obj_pos,base2objup_pos,objup2obj_pos,grasp_flag 


def jointMove(robot, mv_type,base2obj_pos,base2objup_pos,objup2obj_pos,grab_status):
    # base move 2 obj-up 2 obj 
    if mv_type == 2: # base move 2 obj-up
        # Check which method to use based on what's available in the robot object
        if hasattr(robot, 'joint_move_origin'):
            ret_base2objup = robot.joint_move_origin(base2objup_pos[1], 1, 0)
        else:
            ret_base2objup = robot.joint_move(joint_pos=base2objup_pos[1], move_mode=0, is_block=True, speed=30)
            
        if ret_base2objup == 0 or (isinstance(ret_base2objup, tuple) and ret_base2objup[0] == 0):
            time.sleep(1)
            
            if hasattr(robot, 'joint_move_origin'):
                ret_move2obj = robot.joint_move_origin(objup2obj_pos[1], 1, 0)
            else:
                ret_move2obj = robot.joint_move(joint_pos=objup2obj_pos[1], move_mode=0, is_block=True, speed=30)
                
            if ret_move2obj == 0 or (isinstance(ret_move2obj, tuple) and ret_move2obj[0] == 0):
                robot.grab_action(grab_status)
                time.sleep(3)
                
                if hasattr(robot, 'joint_move_origin'):
                    moveRet = robot.joint_move_origin(base2objup_pos[1], 1, 0)
                else:
                    moveRet = robot.joint_move(joint_pos=base2objup_pos[1], move_mode=0, is_block=True, speed=30)
                    
                if moveRet == 0 or (isinstance(moveRet, tuple) and moveRet[0] == 0):
                    print("obj move 2 obj-up success")
                else:
                    print("obj move 2 obj-up failure")
                time.sleep(1)

            else:
                print("obj-up move 2 obj failure")    
        else:
            print("base move 2 obj-up failure")   
    # base 2 obj
    if mv_type == 1:
        if hasattr(robot, 'joint_move_origin'):
            ret_move2obj = robot.joint_move_origin(base2obj_pos[1], 1, 0)
        else:
            ret_move2obj = robot.joint_move(joint_pos=base2obj_pos[1], move_mode=0, is_block=True, speed=30)
            
        if ret_move2obj == 0 or (isinstance(ret_move2obj, tuple) and ret_move2obj[0] == 0):
            time.sleep(1)
            robot.grab_action(grab_status)
            time.sleep(3)
            print('next: obj move 2 put-up')
        else:
            print("base move 2 obj failure")
    return 

def show_unreachable_warning(image, status_text, auto_execute=False):
    """显示不可达警告窗口"""
    print('Warning: Position unreachable!')
    print(f"STATUS: {status_text}")
    
    # 如果不是自动执行模式，显示窗口等待用户确认
    if not auto_execute:
        # 在显示窗口中添加状态文本
        cv2.putText(image, f"STATUS: {status_text}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
        cv2.namedWindow("Object Detection - UNREACHABLE", cv2.WINDOW_NORMAL)
        cv2.imshow("Object Detection - UNREACHABLE", image)
        print("Press any key to continue...")
        cv2.waitKey(0)  # 等待任意按键
        cv2.destroyAllWindows()
    
    print('Continuing to next detection cycle...')

def run_detection(robot=None, auto_execute=False, camera_serial_number=None):
    """
    运行视觉检测和抓取任务
    :param robot: 可选，JAKA机器人控制对象。如果提供，将使用此对象而不是创建新对象
    :param auto_execute: 是否自动执行机器人动作，不等待用户点击图像。True表示自动执行，False表示等待用户确认
    :param camera_serial_number: 可选，相机的序列号，用于指定使用特定的相机
    """
    mapJsonData = loadJsonFile('./conf/userCmdControl.json')
    calibParams = loadJsonFile('./conf/CalibParams-lumi-hand.json')

    # 使用传入的机器人控制对象或创建新的
    if robot is None:
        robot = JAKA(mapJsonData["calibrateParams"]["robotIP"], connect=True)
        robot._login()

    # robot move to basepose
    base_loc = mapJsonData["robotParams"]["basePose"] 
    print("base_loc: ",base_loc)

    
    # 检查是否有joint_move_origin方法，没有则使用joint_move
    if hasattr(robot, 'joint_move_origin'):
        robot.joint_move_origin(base_loc, 1, 0)
    else:
        robot.joint_move(joint_pos=base_loc, move_mode=0, is_block=True, speed=30)
   
    # open grab
    robot.grab_action(0)
    time.sleep(2)

    mv_obj = mapJsonData["objects"]["moveObjects"]
    put_obj = mapJsonData["objects"]["putObject"]
    
    # 根据操作模式确定需要检测的物体
    if "operationMode" not in mapJsonData:
        operation_mode = "both"  # 默认模式：抓取和放置都必须可达
    else:
        operation_mode = mapJsonData["operationMode"]
    
    # 显示当前操作模式
    print(f"当前操作模式: {operation_mode}")
    print("可选模式: 'both'(抓取和放置都必须可达), 'grasp_only'(仅执行抓取), 'put_only'(仅执行放置), 'grasp_priority'(优先抓取，不要求放置可达)")

    # 根据操作模式确定需要检测的物体
    if operation_mode == "grasp_only":
        tags = [mv_obj]  # 只检测抓取物体
        print(f"仅抓取模式：只检测 '{mv_obj}'")
    elif operation_mode == "put_only":
        tags = [put_obj]  # 只检测放置位置
        print(f"仅放置模式：只检测 '{put_obj}'")
    else:
        tags = [mv_obj, put_obj]  # 检测两种物体
        print(f"检测所有物体: '{mv_obj}' 和 '{put_obj}'")

    detect_continue = True # Repeated detection and grabbing

    # 如果指定了相机序列号，先列出所有相机
    if camera_serial_number:
        # 临时创建一个相机对象以列出所有相机
        try:
            temp_cam = Camera()
            devices = temp_cam.list_connected_devices()
            temp_cam.close()
            
            print("\n可用的Orbbec相机:")
            for device in devices:
                print(f"索引: {device['index']}, 名称: {device['name']}, 序列号: {device['serial_number']}")
            
            # 检查指定的序列号是否存在
            sn_exists = any(device['serial_number'] == camera_serial_number for device in devices)
            if not sn_exists and devices:
                print(f"警告: 未找到序列号为 {camera_serial_number} 的相机，将使用默认相机")
        except Exception as e:
            print(f"列出相机时出错: {e}")
            print("将尝试直接使用指定的相机序列号")

    while detect_continue:
        mv_objs = []  # Allow multiple similar items
        put_objs = []  # Only one target location.
        mv_centers, put_center = [],[]

        # 尝试获取相机图像，处理可能的错误
        try:
            # Get image
            cam = Camera(serial_number=camera_serial_number)
            color_img, depth_data, _ = cam.getColorDepthData()
            cam.close()
            
            # 检查获取的图像是否有效
            if color_img is None or len(color_img) == 0 or depth_data is None or len(depth_data) == 0:
                print("无法获取有效的相机图像，跳过此次检测")
                time.sleep(1)  # 等待一秒再试
                continue
                
            # Save originimg
            img_path = saveOriginImg(color_img, mapJsonData["cameraParams"]["saveImgPath"])
            
            # Objects Detection
            obj_labels, obj_locs = vl_ali(tags, img_path)
            
        except Exception as e:
            print(f"获取相机数据时出错: {e}")
            print("等待1秒后重试...")
            time.sleep(1)
            continue

        if len(obj_labels) == 0 or len(obj_locs) == 0:
            print("未检测到任何物体，继续下一次检测...")
            continue

        if len(obj_labels) != len(obj_locs):
            if put_obj not in obj_labels:
                black_name = len(obj_locs) - len(obj_labels)
                for i in range(black_name - 1):
                    obj_labels.append(obj_labels[0])
                obj_labels.append(put_obj)
            else:
                obj_labels = [mv_obj for _ in range(len(obj_locs) - 1)]
                obj_labels.append(put_obj)

        for i in range(len(obj_labels)):
            # print('objPos:',objPos)
            center_x = (int(obj_locs[i][0]) + int(obj_locs[i][2])) / 2
            center_y = (int(obj_locs[i][1]) + int(obj_locs[i][3])) / 2
            if obj_labels[i]==mv_obj:
                mv_objs.append(obj_locs[i])
                mv_centers.append([int(center_x), int(center_y)])
            if obj_labels[i]==put_obj:
                put_objs.append(obj_locs[i])
                put_center.append([int(center_x), int(center_y)])
        print("mv_objs,mv_centers: ",mv_objs,mv_centers)
        print("put_objs,put_center: ",put_objs,put_center)

        # 检查是否检测到了必要的物体
        if len(mv_objs) == 0 and operation_mode != "put_only":
            print(f"未检测到移动物体({mv_obj})，继续下一次检测...")
            continue
            
        if len(put_objs) == 0 and operation_mode != "grasp_only":
            print(f"未检测到放置位置({put_obj})，继续下一次检测...")
            continue

        # 处理移动物体 - 只在非仅放置模式下处理
        grasp_flag = 0  # 默认可达
        if operation_mode != "put_only":
            for i in range(len(mv_objs)):
                cur_obj_pos = mv_objs[i]
                cur_center_pos = mv_centers[i]
                cv2.rectangle(color_img, (cur_obj_pos[0], cur_obj_pos[1]),
                                (cur_obj_pos[2], cur_obj_pos[3]), (0, 0, 255), 2)

                mv_obj_depth = depth_data[cur_center_pos[1], cur_center_pos[0]]

                # Current point gets depth of 0, search for the depth of the surrounding point
                if int(mv_obj_depth) == 0:
                    gen_center_points = generatorNearPoints(put_center,
                                                            mapJsonData["genNearPointParams"][
                                                                "nearPointInterval"],
                                                            mapJsonData["genNearPointParams"][
                                                                "nearPointTimes"])

                    for i, point in enumerate(gen_center_points):
                        # 修复点的索引方式，确保正确访问点的坐标
                        try:
                            # 如果point是嵌套列表
                            mv_obj_depth = depth_data[point[0][1], point[0][0]]
                        except (TypeError, IndexError):
                            # 如果point是单个坐标点
                            mv_obj_depth = depth_data[point[1], point[0]]
                        
                        if int(mv_obj_depth) != 0 or i == len(gen_center_points):
                            break
                print("【{} depth is: {} (mm)】".format(mv_obj,mv_obj_depth))
                obj_world_loc = pixel_to_world(cur_center_pos, mv_obj_depth, calibParams["CameraMatrix"],
                    calibParams["RotationMat"],
                    calibParams["TranslationMat"])
                
                # Display coordinates on image
                text_pixel = f"Pixel: ({cur_center_pos[0]}, {cur_center_pos[1]})"
                text_world = f"World: ({obj_world_loc[0]:.2f}, {obj_world_loc[1]:.2f}, {obj_world_loc[2]:.2f})"
                cv2.putText(color_img, text_pixel, (cur_obj_pos[0], cur_obj_pos[1]-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(color_img, text_world, (cur_obj_pos[0], cur_obj_pos[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                ref_pos = robot.getjoints()
                base_loc= robot.get_tcp_pos()

                print('Calculate whether the position of the item to be captured is reachable')
                mv_type,grip_loc,grip_up_loc,base2obj_pos,base2objup_pos,objup2obj_pos,grasp_flag = kine_caculate(robot, ref_pos,base_loc,obj_world_loc,mapJsonData,step_type=-1)    
        else:
            # 在仅放置模式下，设置默认值以便程序正常运行
            ref_pos = robot.getjoints()
            base_loc = robot.get_tcp_pos()
            mv_type = 1  # 设置默认移动类型
            grip_up_loc = base_loc  # 使用当前位置
            base2obj_pos = [0, base_loc]  # 假设可达
            base2objup_pos = [0, base_loc]
            objup2obj_pos = [0, base_loc]

        # 处理放置物体 - 只在非仅抓取模式下处理
        put_flag = 0  # 默认可达
        if operation_mode != "grasp_only" and len(put_objs) > 0:
            put_obj_depth = depth_data[put_center[0][1], put_center[0][0]] 
            put_obj_pos = put_objs[0]  
            put_center = put_center[0]  
            cv2.rectangle(color_img, (put_obj_pos[0], put_obj_pos[1]),
                            (put_obj_pos[2], put_obj_pos[3]), (0, 0, 255), 2) 
         
            if int(put_obj_depth) == 0:
                gen_center_points=generatorNearPoints(put_center,mapJsonData["genNearPointParams"]["nearPointInterval"],mapJsonData["genNearPointParams"]["nearPointTimes"])

                for i,point in enumerate(gen_center_points):
                    # 修复点的索引方式，确保正确访问点的坐标
                    try:
                        # 如果point是嵌套列表
                        put_obj_depth = depth_data[point[0][1], point[0][0]]
                    except (TypeError, IndexError):
                        # 如果point是单个坐标点
                        put_obj_depth = depth_data[point[1], point[0]]
                    
                    if int(put_obj_depth) != 0 or i==len(gen_center_points):
                        break
            print("【{} depth is: {} (mm)】".format(put_obj,put_obj_depth))
            put_world_loc = pixel_to_world(put_center, put_obj_depth, calibParams["CameraMatrix"],
                    calibParams["RotationMat"],
                    calibParams["TranslationMat"])

            # Display put object coordinates on image
            text_pixel = f"Pixel: ({put_center[0]}, {put_center[1]})"
            text_world = f"World: ({put_world_loc[0]:.2f}, {put_world_loc[1]:.2f}, {put_world_loc[2]:.2f})"
            cv2.putText(color_img, text_pixel, (put_obj_pos[0], put_obj_pos[1]-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            cv2.putText(color_img, text_world, (put_obj_pos[0], put_obj_pos[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            # 计算放置位置可达性
            print('Calculate whether the location of the item to be placed is reachable')
            if mv_type == 2:
                ref_pos_d = base2objup_pos[1]
            elif mv_type == 1:
                ref_pos_d = base2obj_pos[1]
            put_type,put_loc,put_loc_up,objup2put_pos,objup2putup_pos,putup2put_pos,put_flag = kine_caculate(robot, ref_pos_d,grip_up_loc,put_world_loc,mapJsonData,step_type=1)
        else:
            # 在仅抓取模式下，设置默认值
            put_type = 1
            put_loc = base_loc
            put_loc_up = base_loc
            objup2put_pos = [0, base_loc]
            objup2putup_pos = [0, base_loc]
            putup2put_pos = [0, base_loc]

        # Display detection results in window
        cv2.namedWindow("Object Detection", cv2.WINDOW_NORMAL)
        cv2.imshow("Object Detection", color_img)
        
        # 根据auto_execute参数决定是否等待用户点击
        if not auto_execute:
            print("Press any key to continue with robot movement...")
            cv2.waitKey(0)  # Wait for any key press
        else:
            print("Auto executing robot movement...")
            cv2.waitKey(1)  # Just refresh the window without waiting
        
        # 保存检测结果图片
        cv2.imwrite(img_path,color_img)
        
        # 根据操作模式判断是否执行机器人动作
        execute_grasp = False
        execute_put = False
        
        # 检查各种操作模式并决定执行哪些操作
        if operation_mode == "both":
            # 抓取和放置都必须可达
            if grasp_flag == 0 and put_flag == 0:
                execute_grasp = True
                execute_put = True
            else:
                status_message = "不可达: "
                if grasp_flag != 0: status_message += "抓取位置 "
                if put_flag != 0: status_message += "放置位置"
                show_unreachable_warning(color_img, status_message, auto_execute)
                continue
                
        elif operation_mode == "grasp_only":
            # 只执行抓取，不执行放置
            if grasp_flag == 0:
                execute_grasp = True
            else:
                show_unreachable_warning(color_img, "抓取位置不可达", auto_execute)
                continue
                
        elif operation_mode == "put_only":
            # 只执行放置(假设物体已被抓取)
            if put_flag == 0:
                execute_put = True
            else:
                show_unreachable_warning(color_img, "放置位置不可达", auto_execute)
                continue
                
        elif operation_mode == "grasp_priority":
            # 只要抓取可达就执行，不管放置是否可达
            if grasp_flag == 0:
                execute_grasp = True
                # 如果放置也可达，则执行放置
                execute_put = (put_flag == 0)
            else:
                show_unreachable_warning(color_img, "抓取位置不可达", auto_execute)
                continue
        
        # 执行抓取操作
        if execute_grasp:
            print('---开始抓取---')
            jointMove(robot, mv_type, base2obj_pos, base2objup_pos, objup2obj_pos, grab_status=1)
        
        # 执行放置操作
        if execute_put:
            print('---开始放置---')
            jointMove(robot, mv_type, objup2put_pos, objup2putup_pos, putup2put_pos, grab_status=0)
        
        # 移动到基准位置
        if hasattr(robot, 'joint_move_origin'):
            robot.joint_move_origin(base_loc, 1, 0)
        else:
            robot.joint_move(joint_pos=base_loc, move_mode=0, is_block=True, speed=30)
        # robot.grab_action(0)

        # Destroy all OpenCV windows
        cv2.destroyAllWindows()
        
        # 如果成功执行了动作，退出循环
        if execute_grasp or execute_put:
            print("动作执行完成，退出检测循环")
            detect_continue = False
        else:
            print("准备下一次检测...")


if __name__=='__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='运行视觉检测和抓取任务')
    parser.add_argument('--auto', action='store_true', help='自动执行模式，不等待用户确认')
    parser.add_argument('--camera-sn', type=str, default=None, help='指定要使用的相机序列号')
    parser.add_argument('--list-cameras', action='store_true', help='列出所有可用的相机')
    
    args = parser.parse_args()
    
    # 如果指定了--list-cameras参数，列出所有相机后退出
    if args.list_cameras:
        try:
            print("正在搜索连接的Orbbec相机...")
            temp_cam = Camera()
            devices = temp_cam.list_connected_devices()
            temp_cam.close()
            
            if not devices:
                print("没有找到连接的Orbbec相机")
            else:
                print("\n可用的Orbbec相机:")
                for device in devices:
                    print(f"索引: {device['index']}, 名称: {device['name']}, 序列号: {device['serial_number']}")
                print("\n使用方法: python visualDetect_ali.py --camera-sn <序列号>")
                
                # 如果命令行没有指定相机序列号，则使用第一个找到的相机
                if args.camera_sn is None and devices:
                    args.camera_sn = devices[0]["serial_number"]
                    print(f"\n自动选择第一个相机: {args.camera_sn}")
        except Exception as e:
            print(f"列出相机时出错: {e}")
            import traceback
            traceback.print_exc()
        exit(0)
    
    # 执行检测
    try:
        print(f"使用相机序列号: {args.camera_sn if args.camera_sn else '默认'}")
        run_detection(auto_execute=args.auto, camera_serial_number=args.camera_sn)
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"运行过程中出错: {e}")
        import traceback
        traceback.print_exc()


        

 