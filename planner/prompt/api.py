from typing import Tuple


# Here are all the available action API you can use to create a valid plan
def takeOffVehicle(vehicle_name:str) -> bool:
    '''
    无人机起飞至离地面3米的位置
    起飞后才能执行其他动作
    '''

def landVehicle(vehicle_name:str) -> bool:
    '''
    无人机降落至地面
    降落后不能执行其他动作
    '''

def moveVehicleTo(vehicle_name:str, position:Tuple[float,float,float]) -> None:
    '''
    移动无人机到指定坐标，坐标基于NED坐标系
    如果takeOffVehicle不为True，则需先起飞再移动
    '''

def rotateVehicleTo(vehicle_name:str, yaw:float) -> float:
    '''
    旋转无人机到指定角度
    如果takeOffVehicle不为True，则需先起飞再旋转
    返回旋转后的角度
    '''

def inspect(vehicle_name:str, visual_query:str) -> str:
    '''
    向视觉语言模型提问以获得更多环境信息或目标细节
    返回视觉语言模型的回答
    '''

def lookFor(vehicle_name:str, object_name:str) -> Tuple[float,float,float]:
    '''
    无人机查找指定目标
    返回目标的坐标
    '''

def get_objecct_position(object_name:str) -> Tuple[float,float,float]:
    '''
    获取环境地图中物体的坐标
    返回物体的坐标
    '''