from smolagents import tool
import airsim
import numpy as np
import cv2
import base64
from typing import List, Tuple
from openai import OpenAI
import time



# 目标物体名称-UE mesh name 对应词典
objects_dict = {
    "turbine1": "BP_Wind_Turbines_C_1",
    "turbine2": "StaticMeshActor_2",
    "solarpanels": "StaticMeshActor_146",
    "crowd": "StaticMeshActor_6",
    "car": "StaticMeshActor_10",
    "tower1": "SM_Electric_trellis_179",
    "tower2": "SM_Electric_trellis_7",
    "tower3": "SM_Electric_trellis_8",
}


# 载入VLM模型
vlm_client = OpenAI(
    base_url = 'http://localhost:11434/v1',
    api_key = 'ollama', # required, but unused
)


# 连接到AirSim客户端
drone_list = ['Drone1', 'Drone2', 'Drone3', 'Drone4']
for drone in drone_list:
    client = airsim.MultirotorClient()
    client.confirmConnection()
    client.enableApiControl(True, vehicle_name=drone)
    client.armDisarm(True, vehicle_name=drone)



@tool
def takeOffVehicle(vehicle_name:str="Drone1") -> str:
    """
    起飞无人机。返回为字符串，表示动作是否成功。

    Args:
        vehicle_name: 无人机名称，默认为"Drone1"
    
    """
    try:
        client.takeoffAsync(vehicle_name=vehicle_name).join()
    except Exception as e:
        return f"起飞失败：{e}"
    return "成功起飞"
    

@tool
def landVehicle(vehicle_name:str="Drone1") -> str:
    """
    降落无人机。返回为字符串，表示动作是否成功。

    Args:
        vehicle_name: 无人机名称，默认为"Drone1"
   
    """
    try:
        client.landAsync(vehicle_name=vehicle_name).join()
    except Exception as e:
        return f"降落失败：{e}"
    return "成功降落"


@tool
def moveVehicleTo(point: Tuple[float,float,float], vehicle_name:str="Drone1") -> str:
    """
    飞到某个坐标点。
    
    Args:
        point: 目标点，包含三维坐标（x/y/z）的元组
        vehicle_name: 无人机名称，默认为"Drone1"
   
    """
    try:
        if point[2] > 0:
            client.moveToPositionAsync(point[0], point[1], -point[2], 5, vehicle_name=vehicle_name).join()
        else:
            client.moveToPositionAsync(point[0], point[1], point[2], 5, vehicle_name=vehicle_name).join()
    except Exception as e:
        return f"飞到目标点失败：{e}"
    return "成功抵达点{x: " + str(point[0]) + ", y: " + str(point[1]) + ", z: " + str(point[2]) + "}"


@tool
def fly_by_path(points: List[List[float]], vehicle_name: str = "Drone1") -> str:
    """
    执行指定路径的飞行

    Args:
        points: 待飞行的路径，每个元素是一个包含三维坐标（x/y/z）的数组
        vehicle_name: 无人机名称, 默认为 "Drone1"

    """
    try:
        airsim_points = []
        for point in points:
            if point[2] > 0:
                airsim_points.append(airsim.Vector3r(point[0], point[1], -point[2]))
            else:
                airsim_points.append(airsim.Vector3r(point[0], point[1], point[2]))
        client.moveOnPathAsync(airsim_points, 5, 120, airsim.DrivetrainType.ForwardOnly, airsim.YawMode(False, 0), 20, 1, vehicle_name).join()
    except Exception as e:
        return f"航点追踪错误：{e}"
    return f"成功飞过指定路径{points}"


def cv2_to_base64(image, format='.png'):
    """ 将OpenCV图像转换为Base64编码的字符串"""
    # 编码为字节流
    success, buffer = cv2.imencode(format, image)
    if not success:
        raise ValueError("图片编码失败，请检查格式参数")
    
    # 转换为 Base64
    img_bytes = buffer.tobytes()
    return base64.b64encode(img_bytes).decode('utf-8')


def get_image(image_type=airsim.ImageType.Scene, camera_name='front_center', vehicle_name='Drone1'):
    """
    获得前置摄像头渲染图像

    Args:
        image_type: 图像类型，默认为airsim.ImageType.Scene
        camera_name: 摄像头名称，默认为'front_center' （前置中心摄像头），可选值包括'front_center', 'front_left', 'front_right', 'back_center', 'bottom_center'.
        vehicle_name: 无人机名称，默认为'Drone1'
    
    """
    response = client.simGetImage(camera_name, image_type, vehicle_name)
    img_bgr = cv2.imdecode(np.array(bytearray(response), dtype='uint8'), cv2.IMREAD_UNCHANGED) # BGR
    img = cv2.cvtColor(img_bgr, cv2.COLOR_RGBA2RGB) # RGB
    return img

@tool
def inspect(visual_query:str, vehicle_name:str="Drone1", camera_name:str="front_center") -> str:
    """
    获得前置摄像头渲染图像，并查询视觉语言模型。
    
    Args:
        visual_query: 提问以获取环境信息或对象细节
        vehicle_name: 无人机名称，默认为"Drone1"
        camera_name: 摄像头名称，默认为'front_center' （前置中心摄像头）, 可选值包括'front_center', 'front_left', 'front_right', 'back_center', 'bottom_center'.
    
    """
   # 读取图像
    rgb_image = get_image(vehicle_name=vehicle_name, camera_name=camera_name)
    
    # 转成base64格式的png图片
    base64_image = cv2_to_base64(rgb_image, ".png")

    # 视觉理解
    completion = vlm_client.chat.completions.create(
            model="qwen2.5vl:32b",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                        },
                        {"type": "text", "text": f"{visual_query}"}
                    ]
                }
            ]
        )
    return completion.choices[0].message.content


@tool
def get_object_position(object_name:str) -> Tuple[float, float, float]:
    '''
    get object postion from UE simulation
    replace by object detection algo(such as YOLO, Grounding DINO) in real world

    Args:
        object_name: 目标物体名称，必须是英文，如果是中文请翻译成英文
    
    '''
    object_name = object_name.lower()
    query_string = objects_dict[object_name] + ".*"
    object_names_ue =[]
    while len(object_names_ue) == 0:
        object_names_ue = client.simListSceneObjects(query_string)
    pose = client.simGetObjectPose(object_names_ue[0])
    return [pose.position.x_val, pose.position.y_val, pose.position.z_val]


@tool
def turn_to(yaw: float, vehicle_name: str = "Drone1") -> str:
    """
    无人机调整朝向角度

    Args:
        yaw: 偏航角，单位为弧度
        vehicle_name: 无人机名称，默认为"Drone1"
    
    """
    try:
        client.rotateToYawAsync(yaw, 5, vehicle_name=vehicle_name).join()
    except Exception as e:
        return f"偏航角设置错误: {e}"
    return f"成功设置偏航角为{yaw}"
