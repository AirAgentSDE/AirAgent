from smolagents import tool
import airsim
import numpy as np
import cv2
import base64
from typing import Tuple
from openai import OpenAI
import math
import time



# 地图对象字典
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


# 载入视觉语言模型
vlm_client = OpenAI(
    base_url = 'http://localhost:11434/v1',
    api_key = 'ollama', # required, but unused
)


_client = None

def get_airsim_client():
    global _client
    if _client is None:
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                _client = airsim.MultirotorClient()
                _client.confirmConnection()
                print("成功连接到AirSim")
                break
            except Exception as e:
                print(f"AirSim连接尝试 {attempt + 1} 失败: {e}")
                if attempt < max_retries - 1:
                    print(f"{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                else:
                    raise RuntimeError(f"经过 {max_retries} 次尝试后连接AirSim失败")
    
    return _client


@tool
def take_off_vehicle(vehicle_name:str="Drone1") -> str:
    """
    起飞无人机。返回成功状态信息，表示动作是否成功。

    Args:
        vehicle_name: 无人机名称，默认为"Drone1"
    """
    try:
        airsim_client = get_airsim_client()
        airsim_client.enableApiControl(True, vehicle_name=vehicle_name)
        airsim_client.armDisarm(True, vehicle_name=vehicle_name)
        airsim_client.takeoffAsync(vehicle_name=vehicle_name).join()
        return "success" 
    except Exception:
        return "failed"

@tool
def land_vehicle(vehicle_name:str="Drone1") -> str:
    """
    降落无人机。返回成功状态信息，表示动作是否成功。

    Args:
        vehicle_name: 无人机名称，默认为"Drone1"
    """
    try:
        airsim_client = get_airsim_client()
        airsim_client.landAsync(vehicle_name=vehicle_name).join()
        airsim_client.armDisarm(False, vehicle_name=vehicle_name)
        airsim_client.enableApiControl(False, vehicle_name=vehicle_name)
        return "success"
    except Exception:
        return "failed"

@tool
def move_vehicle_to(point: Tuple[float,float,float], vehicle_name:str="Drone1") -> None:
    """
    将无人机移动到指定的三维坐标点。
    
    Args:
        point: 目标点, 包含三维坐标(x/y/z)的元组
        vehicle_name: 无人机名称, 默认为"Drone1"
    """
    try:
        airsim_client = get_airsim_client()
        if point[2] > 0:
            airsim_client.moveToPositionAsync(point[0], point[1], -point[2], 5, vehicle_name=vehicle_name).join()
        else:
            airsim_client.moveToPositionAsync(point[0], point[1], point[2], 5, vehicle_name=vehicle_name).join()
    except Exception:
        return "failed"

@tool
def turn_to(yaw: float, vehicle_name: str = "Drone1") -> float:
    """
    使无人机转向指定的偏航角。

    Args:
        yaw: 偏航角，单位为弧度
        vehicle_name: 无人机名称，默认为"Drone1"
    """
    airsim_client = get_airsim_client()
    airsim_client.rotateToYawAsync(yaw, 5, vehicle_name=vehicle_name).join()
    return yaw


def cv2_to_base64(image, format='.png'):
    """将OpenCV图像转换为Base64编码的字符串"""
    success, buffer = cv2.imencode(format, image)
    if not success:
        raise ValueError("图片编码失败，请检查格式参数")
    
    img_bytes = buffer.tobytes()
    return base64.b64encode(img_bytes).decode('utf-8')


def get_image(image_type=airsim.ImageType.Scene, camera_name='front_center', vehicle_name='Drone1'):
    """获得前置摄像头渲染图像"""
    airsim_client = get_airsim_client()
    response = airsim_client.simGetImage(camera_name, image_type, vehicle_name)
    img_bgr = cv2.imdecode(np.array(bytearray(response), dtype='uint8'), cv2.IMREAD_UNCHANGED) # BGR格式
    img = cv2.cvtColor(img_bgr, cv2.COLOR_RGBA2RGB) # 转换为RGB格式
    return img


@tool
def inspect(visual_query:str, vehicle_name:str="Drone1", camera_name:str="front_center") -> str:
    """
    向视觉语言模型提问以获得更多环境信息或对象细节。
    
    Args:
        visual_query: 提问内容
        vehicle_name: 无人机名称，默认为"Drone1"
        camera_name: 摄像头名称，默认为'front_center' （前置中心摄像头）, 可选值包括'front_center', 'front_left', 'front_right', 'back_center', 'bottom_center'.
    """
   # 读取图像
    rgb_image = get_image(vehicle_name=vehicle_name, camera_name=camera_name)
    
    # 转换为base64格式的PNG图片
    base64_image = cv2_to_base64(rgb_image, ".png")

    # 视觉理解处理
    completion = vlm_client.chat.completions.create(
            model="qwen2.5vl:7b",
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
def get_position(object_name: str)-> Tuple[float,float,float,float]:
    """
    获取特定对象的位置
    
    Args:
        object_name: 对象名称
        
    Returns: 
        Tuple[float,float,float,float]: 对象位置，包含三维坐标 (x, y, z)和偏航角（角度制）的元组
    """
    airsim_client = get_airsim_client()
    # 构建查询字符串
    query_string = objects_dict[object_name] + ".*"
    object_names_ue = []
    # 循环查找对象直到找到为止
    while len(object_names_ue) == 0:
        object_names_ue = airsim_client.simListSceneObjects(query_string)
    try:
        pose = airsim_client.simGetObjectPose(object_names_ue[0])
    except Exception:
        return "找不到该对象，如果确认对象存在，请尝试使用同义词"
    orientation_quat = pose.orientation
    yaw = airsim.to_eularian_angles(orientation_quat)[2] # 获取偏航角
    yaw_degree = math.degrees(yaw) # 转换为角度制
    
    return [pose.position.x_val, pose.position.y_val, pose.position.z_val, yaw_degree]


def reset():
    '''重置环境'''
    airsim_client = get_airsim_client()
    airsim_client.reset()
    time.sleep(3)
    print("系统已重置，请开始下一轮调试")
