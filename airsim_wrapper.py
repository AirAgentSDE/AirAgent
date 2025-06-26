from smolagents import tool
import airsim
import numpy as np
import cv2
import base64
import time
from typing import List, Tuple
from openai import OpenAI



# 目标物体名称-UE mesh name对应词典
# 场景必须为airsim inspection，可在release中找到
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
    api_key='ollama', # required, but unused
)


# 连接到AirSim客户端
drone_list = ['Drone1', 'Drone2', 'Drone3', 'Drone4', 'Drone5', 'Drone6', 'Drone7', 'Drone8', 'Drone9']
for drone in drone_list:
    client = airsim.MultirotorClient()



@tool
def takeoff(vehicle_name:str="Drone1") -> str:
    """
    起飞无人机。返回为字符串，表示动作是否成功。

    Args:
        vehicle_name: str: 无人机名称，默认为"Drone1"
    Returns:
        str: 成功状态描述
    """
    client.confirmConnection()
    client.enableApiControl(True, vehicle_name=vehicle_name)
    client.armDisarm(True, vehicle_name=vehicle_name)
    client.takeoffAsync(vehicle_name=vehicle_name).join()

    return "起飞成功"
    
@tool
def land(vehicle_name:str="Drone1") -> str:
    """
    降落无人机。返回为字符串，表示动作是否成功。

    Args:
        vehicle_name: str: 无人机名称，默认为"Drone1"
    Returns:
        str: 成功状态描述
    """
    client.landAsync(vehicle_name=vehicle_name).join()

    return "降落成功"

@tool
def fly_to(point: Tuple[float,float,float], vehicle_name:str="Drone1") -> str:
    """
    飞到某个坐标点。
    
    Args:
        point:Tuple[x, y, z]: 目标点，包含三维坐标（x/y/z）的元组
        vehicle_name: str: 无人机名称，默认为"Drone1"
    Returns:
        str: 成功状态描述
    """
    if point[2] > 0:
        client.moveToPositionAsync(point[0], point[1], -point[2], 1, vehicle_name=vehicle_name).join()
    else:
        client.moveToPositionAsync(point[0], point[1], point[2], 1, vehicle_name=vehicle_name).join()

    return "成功抵达点{x: " + str(point[0]) + ", y: " + str(point[1]) + ", z: " + str(point[2]) + "}"


def cv2_to_base64(image, format='.png'):
    """ 将OpenCV图像转换为Base64编码的字符串"""
    # 编码为字节流
    success, buffer = cv2.imencode(format, image)
    if not success:
        raise ValueError("图片编码失败，请检查格式参数")
    
    # 转换为 Base64
    img_bytes = buffer.tobytes()
    return base64.b64encode(img_bytes).decode('utf-8')


def get_image(image_type=airsim.ImageType.Scene, camera_name='0', vehicle_name='Drone1'):
    """
    获得前置摄像头渲染图像

    Args:
        image_type: 图像类型，默认为airsim.ImageType.Scene
        camera_name: 摄像头名称，默认为'0' （前置中心摄像头）
        vehicle_name: 无人机名称，默认为'Drone1'
    Returns: 
        img: 图像数据
    """
    response = client.simGetImage(camera_name, image_type, vehicle_name)
    img_bgr = cv2.imdecode(np.array(bytearray(response), dtype='uint8'), cv2.IMREAD_UNCHANGED) 
    img = cv2.cvtColor(img_bgr, cv2.COLOR_RGBA2RGB)
    return img

@tool
def inspect(visual_query:str, vehicle_name:str="Drone1")->str:
    """
    获得前置摄像头渲染图像，并使用视觉理解模型进行分析。
    
    Args:
        visual_query: str: 视觉理解查询语句，例如"列出图像中的所有物体", "发电站是否损坏？"
        vehicle_name: str: 无人机名称，默认为"Drone1"
    Returns:
    """
   # 读取图像
    rgb_image = get_image(vehicle_name=vehicle_name)
    
    # 转成base64格式的png图片
    base64_image = cv2_to_base64(rgb_image, ".png")  # png或 '.jpg'

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
        object_name: str: 目标物体名称
    Returns:
        Tuple[x, y, z]: 目标物体的三维坐标元组
    '''
    object_name = object_name.lower()
    query_string = objects_dict[object_name] + ".*"
    object_names_ue =[]
    while len(object_names_ue) == 0:
        object_names_ue = client.simListSceneObjects(query_string)
    pose = client.simGetObjectPose(object_names_ue[0])
    return [pose.position.x_val, pose.position.y_val, pose.position.z_val]
