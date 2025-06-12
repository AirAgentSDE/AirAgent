from smolagents import tool
import airsim
import numpy as np
import cv2
import base64
import time
from typing import List, Tuple
from openai import OpenAI




# 载入VLM模型
vlm_client = OpenAI(
    base_url = 'http://localhost:11434/v1',
    api_key='ollama', # required, but unused
)


# 连接到AirSim客户端
client = airsim.MultirotorClient()



@tool
def takeoff(vehicle_name:str) -> str:
    """
    起飞无人机。返回为字符串，表示动作是否成功。

    Args:
        vehicle_name: str: 无人机名称
    Returns:
        str: 成功状态描述
    """
    client.confirmConnection()
    client.enableApiControl(True, vehicle_name=vehicle_name)
    client.armDisarm(True, vehicle_name=vehicle_name)
    client.takeoffAsync(vehicle_name=vehicle_name).join()

    return "起飞成功"
    
@tool
def land(vehicle_name:str) -> str:
    """
    降落无人机。返回为字符串，表示动作是否成功。

    Args:
        vehicle_name: str: 无人机名称
    Returns:
        str: 成功状态描述
    """
    client.landAsync(vehicle_name=vehicle_name).join()

    return "降落成功"

@tool
def fly_to(point: Tuple[float,float,float], vehicle_name:str) -> str:
    """
    飞到指定位置，返回字符串，表示动作是否成功。

    Args:
        point:Tuple[x, y, z]: 目标点，包含三维坐标（x/y/z）的元组
        vehicle_name: str: 无人机名称
    Returns:
        str: 成功状态描述
    """
    if point[2] > 0:
        client.moveToPositionAsync(point[0], point[1], -point[2], 1, vehicle_name=vehicle_name).join()
    else:
        client.moveToPositionAsync(point[0], point[1], point[2], 1, vehicle_name=vehicle_name).join()

    return "成功抵达点{x: " + str(point[0]) + ", y: " + str(point[1]) + ", z: " + str(point[2]) + "}"


def cv2_to_base64(image, format='.png'):
    """将 OpenCV 内存中的 numpy 数组转为 Base64 字符串"""
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
    """
    response = client.simGetImage(camera_name, image_type, vehicle_name)
    img_bgr = cv2.imdecode(np.array(bytearray(response), dtype='uint8'), cv2.IMREAD_UNCHANGED)  # type: ignore
    img = cv2.cvtColor(img_bgr, cv2.COLOR_RGBA2RGB)
    return img

@tool
def look(vehicle_name:str)->str:
    """
    获得前置摄像头渲染图像,并给出图像中主要物体列表。
    
    Args:
        vehicle_name: str: 无人机名称
    Returns:
        str: 目标名称用英文逗号分隔
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
                        {"type": "text", "text": "图片中有哪些目标，请给出名称即可，给出常见的，清晰可见的目标即可，多个目标名称之间用英文逗号分隔，例如：行人, 救护车, 摩托车。"}
                    ]
                }
            ]
        )
    return completion.choices[0].message.content # type: ignore
