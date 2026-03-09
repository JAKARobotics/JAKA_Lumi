
import cv2
import json
from http import HTTPStatus
import dashscope
import numpy as np
from dashscope import MultiModalConversation
import os


PI=3.1415926
dashscope.api_key=os.getenv('DASHSCOPE_API_KEY')


def loadJsonFile(jsonFile):
    with open(jsonFile,"r",encoding='utf8') as file:
        data=json.load(file)
        return data
    


def simple_multimodal_conversation_call(image_file, text):
    """Simple single round multimodal conversation call.
    """
    messages = [
        {
            "role": "system",
            "content": [
                {"text": "Caption with Grounding"},
            ]

        },
        {
            "role": "user",
            "content": [
                {"image": image_file},  
                {"text": text},
            ]
        }
    ]

    response = MultiModalConversation.call(model='qwen-vl-max',  
                                           # seed=random.randint(1,20000),
                                           messages=messages,
                                           result_format='message',
                                           response_format={'type': 'json_object'})
    # The response status_code is HTTPStatus.OK indicate success,
    # otherwise indicate request is failed, you can get error code
    # and message from code and message.

    if response.status_code == HTTPStatus.OK:
        ans = response.output.choices[0].message.content
    else:
        ans = None
        print(response.code)  # The error code.
        print(response.message)  # The error message.
    return ans

def vl_ali(tags,img_path):
    text = "请帮我将"
    if len(tags) == 1:
        text+=tags[0]
    else:
        for i in range(len(tags)):
            if i==len(tags)-1:
                text+="和"
            elif i>0:
                text+="，"
            text+=tags[i]
    text+="这{}种物体在图中框取出来".format(len(tags))
    print(text)
    image_file = f"file://{img_path}"
    ans=simple_multimodal_conversation_call(image_file,text)

    print("vl检测完成")
    if ans and isinstance(ans, list) and len(ans) > 0:
        ans_text = ans[0].get('text', '')
        try:
            json_data = json.loads(ans_text.strip('```json\n').strip('```'))
            objs = [item['label'] for item in json_data]
            objPos = [[item['bbox_2d'][0], item['bbox_2d'][1], item['bbox_2d'][2], item['bbox_2d'][3]] for item in json_data]

        except json.JSONDecodeError as e:
            print(f"JSON ERROR: {e}")
            objs = []
            objPos = []
    else:
        objs = []
        objPos = [] 

    return objs,objPos

def pixel_to_world(pixel_xy, depth, K, R_camera_to_world, T_camera_to_world):
    u, v = pixel_xy
    #  # Intrinsic parameters
    fx, fy = K[0][0], K[1][1]  
    cx, cy = K[0][2], K[1][2]  

    x_n = (u - cx) / fx
    y_n = (v - cy) / fy

    X_c = depth * x_n
    Y_c = depth * y_n
    Z_c = depth

    P_camera=np.array([X_c,Y_c,Z_c])
    T_camera_to_world=np.array(T_camera_to_world).reshape(3)
    P_world=np.dot(np.array(R_camera_to_world),P_camera)+T_camera_to_world
    print('Pix_to_world:' ,P_world)
    return P_world


def findCorners(img,boardWidth,boardHeight):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (boardWidth, boardHeight), None)
    return ret

def generatorNearPoints(current_pos,near_point_interval=2,nums=2):
    # currentPos = [10, 10]
    points = []
    points.append(current_pos)
    for i in range(1, nums + 1):
        left_top_x = current_pos[0] - near_point_interval * i
        left_top_y = current_pos[1] - near_point_interval * i

        right_bottom_x = current_pos[0] + near_point_interval * i
        right_bottom_y = current_pos[1] + near_point_interval * i

        for i in range(left_top_x, right_bottom_x + near_point_interval, near_point_interval):
            points.append([i, left_top_y])
            points.append([i, right_bottom_y])
        for j in range(left_top_y + near_point_interval, right_bottom_y, near_point_interval):
            points.append([left_top_y, j])
            points.append([right_bottom_y, j])

    return points


def saveOriginImg(color_image,save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 获取目录下已有的文件数量
    files = os.listdir(save_dir)
    img_name = f"{len(files) + 1}.jpg"
    # 构造保存路径
    img_path = os.path.join(save_dir, img_name)
    
    # 保存图像
    cv2.imwrite(img_path, color_image)
    return os.path.abspath(img_path)

