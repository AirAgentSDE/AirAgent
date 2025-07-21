from smolagents import tool
import airsim
import numpy as np
import cv2
import base64
from typing import List, Tuple
from openai import OpenAI
import pprint



# 目标物体名称-UE mesh name 对应词典
# 只在airsim inspection场景中生效
objects_dict = {
    "wind_turbine1": "BP_Wind_Turbines_C_1",
    "wind_turbine2": "StaticMeshActor_2",
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
client = airsim.MultirotorClient()
client.confirmConnection()


@tool
def takeOffVehicle(vehicle_name:str="Drone1") -> str:
    """
    起飞无人机。返回成功状态信息，表示动作是否成功。

    Args:
        vehicle_name: 无人机名称，默认为"Drone1"
    
    """
    try:
        client.enableApiControl(True, vehicle_name=vehicle_name)
        client.armDisarm(True, vehicle_name=vehicle_name)
        client.takeoffAsync(vehicle_name=vehicle_name).join()
        return "success" 
    except Exception:
        return "failed"

@tool
def landVehicle(vehicle_name:str="Drone1") -> str:
    """
    降落无人机。返回成功状态信息，表示动作是否成功。

    Args:
        vehicle_name: 无人机名称，默认为"Drone1"
   
    """
    try:
        client.landAsync(vehicle_name=vehicle_name).join()
        return "success"
    except Exception:
        return "failed"

@tool
def moveVehicleTo(point: Tuple[float,float,float], vehicle_name:str="Drone1") -> None:
    """
    飞到某个坐标点。
    
    Args:
        point: 目标点，包含三维坐标（x/y/z）的元组
        vehicle_name: 无人机名称，默认为"Drone1"
   
    """
    if point[2] > 0:
        client.moveToPositionAsync(point[0], point[1], -point[2], 5, vehicle_name=vehicle_name).join()
    else:
        client.moveToPositionAsync(point[0], point[1], point[2], 5, vehicle_name=vehicle_name).join()

@tool
def turn_to(yaw: float, vehicle_name: str = "Drone1") -> float:
    """
    调整无人机朝向角度。

    Args:
        yaw: 偏航角，单位为弧度
        vehicle_name: 无人机名称，默认为"Drone1"
    
    """
    client.rotateToYawAsync(yaw, 5, vehicle_name=vehicle_name).join()
    return yaw


def cv2_to_base64(image, format='.png'):
    """将OpenCV图像转换为Base64编码的字符串"""
    # 编码为字节流
    success, buffer = cv2.imencode(format, image)
    if not success:
        raise ValueError("图片编码失败，请检查格式参数")
    
    # 转换为 Base64
    img_bytes = buffer.tobytes()
    return base64.b64encode(img_bytes).decode('utf-8')


def get_image(image_type=airsim.ImageType.Scene, camera_name='front_center', vehicle_name='Drone1'):
    """获得前置摄像头渲染图像"""
    response = client.simGetImage(camera_name, image_type, vehicle_name)
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
    object_names_ue = []
    while len(object_names_ue) == 0:
        object_names_ue = client.simListSceneObjects(query_string)
    pose = client.simGetObjectPose(object_names_ue[0])
    if pose is None:
        raise ValueError(f"无法获取物体 {object_name} 的位置，请检查地图中是否存在该物体。")
    return [pose.position.x_val, pose.position.y_val, pose.position.z_val]

@tool
def lookFor(object_name: str, camera_name: str, image_type: str, vehicle_name: str) -> Tuple[float, float, float]:
    """
    查找指定目标物体的位置。

    Args:
        object_name: 目标物体名称
        camera_name: 相机位置
        image_type: 图像类型
        vehicle_name: 无人机名称
    """
    client.simSetDetectionFilterRadius(camera_name, image_type, radius_cm = 500*900, vehicle_name=vehicle_name)
    client.simClearDetectionMeshNames(camera_name, image_type, vehicle_name)
    client.simAddDetectionFilterMeshName(camera_name, image_type, mesh_name=f"*{object_name}*", vehicle_name=vehicle_name)
    while True:
        rawImage = get_image(image_type, camera_name, vehicle_name)
        if not rawImage:
            continue
        png = cv2.imdecode(airsim.string_to_uint8_array(rawImage), cv2.IMREAD_UNCHANGED)
        objects = client.simGetDetections(camera_name, image_type)
        if objects:
            for object in objects:
                s = pprint.pformat(object)
                print("detected: %s" %s)

                cv2.rectangle(png,(int(object.box2D.min.x_val),int(object.box2D.min.y_val)),(int(object.box2D.max.x_val),int(object.box2D.max.y_val)),(255,0,0),2)
                cv2.putText(png, object.name, (int(object.box2D.min.x_val), int(object.box2D.min.y_val - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (36,255,12))
        cv2.imshow("AirSim", png)