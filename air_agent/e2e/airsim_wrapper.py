from smolagents import tool
import airsim
import numpy as np
import cv2
import base64
from typing import List, Tuple
from openai import OpenAI
import math
import time



# 已知地图
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


# AirSim client - initialized lazily to ensure AirSim is running first
_client = None

def get_airsim_client():
    """Get or create AirSim client with proper connection handling"""
    global _client
    if _client is None:
        max_retries = 10
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                _client = airsim.MultirotorClient()
                _client.confirmConnection()
                print("Successfully connected to AirSim")
                break
            except Exception as e:
                print(f"AirSim connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise RuntimeError(f"Failed to connect to AirSim after {max_retries} attempts")
    
    return _client

# Use a property-like approach for backward compatibility
client = property(lambda self: get_airsim_client())


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
    img_bgr = cv2.imdecode(np.array(bytearray(response), dtype='uint8'), cv2.IMREAD_UNCHANGED) # BGR
    img = cv2.cvtColor(img_bgr, cv2.COLOR_RGBA2RGB) # RGB
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
    
    # 转成base64格式的png图片
    base64_image = cv2_to_base64(rgb_image, ".png")

    # 视觉理解
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


# 物体检测, 使用Airsim自带的检测器
@tool
def detect(object_name: str, camera_name: str = "front_center", vehicle_name: str = "Drone1") -> dict:
    """
    查找指定目标物体的位置。

    Args:
        object_name: 目标物体名称
        camera_name: 相机位置，默认为"front_center"
        vehicle_name: 无人机名称，默认为"Drone1"
        
    """
    airsim_client = get_airsim_client()
    image_type = airsim.ImageType.Scene
    try:
        airsim_client.simSetDetectionFilterRadius(camera_name, image_type, radius_cm=20000, vehicle_name=vehicle_name)
        airsim_client.simClearDetectionMeshNames(camera_name, image_type, vehicle_name)
        airsim_client.simAddDetectionFilterMeshName(camera_name, image_type, mesh_name=f"*{object_name}*", vehicle_name=vehicle_name)
        
        objects = airsim_client.simGetDetections(camera_name, image_type, vehicle_name=vehicle_name)
        
        if objects:
            # 取第一个检测到的对象
            object = objects[0]
            
            relative_position = {
                "x": object.relative_pose.position.x_val,
                "y": object.relative_pose.position.y_val,
                "z": object.relative_pose.position.z_val
            }
            
            # 计算绝对位置
            drone_state = airsim_client.getMultirotorState(vehicle_name=vehicle_name)
            drone_position = drone_state.kinematics_estimated.position
            position = {
                "x": drone_position.x_val + relative_position["x"],
                "y": drone_position.y_val + relative_position["y"],
                "z": drone_position.z_val + relative_position["z"]
            }
            return position

    finally:
        # 清理检测过滤器，防止资源累积
        airsim_client.simClearDetectionMeshNames(camera_name, image_type, vehicle_name)
        time.sleep(2)

    return f"cannot find {object_name}, try change to synonyms or inspect the object"


@tool
def get_position(object_name: str)-> Tuple[float,float,float,float]:
    """
    get the position of a specific object
    
    Args:
        object_name: the name of the object
        
    Returns: 
        Tuple[float,float,float,float]: position, the position of the object,点为三维坐标 (x, y, z)和偏航角（角度制）的元组
    """
    airsim_client = get_airsim_client()
    query_string = objects_dict[object_name] + ".*"
    object_names_ue = []
    while len(object_names_ue) == 0:
        object_names_ue = airsim_client.simListSceneObjects(query_string)
    try:
        pose = airsim_client.simGetObjectPose(object_names_ue[0])
    except Exception:
        return "no such object, if you confirm the presence of the object, please try synonyms"
    orientation_quat = pose.orientation
    yaw = airsim.to_eularian_angles(orientation_quat)[2] # get the yaw angle
    yaw_degree = math.degrees(yaw)

    
    return [pose.position.x_val, pose.position.y_val, pose.position.z_val, yaw_degree]
