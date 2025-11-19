from smolagents import CodeAgent, LiteLLMModel
import airsim
from e2e.airsim_wrapper import *
import json
import math
import numpy as np
import time
from typing import Optional, Union


class UAVAgent:
    """用于在AirSim环境中使用自然语言指令控制无人机的UAV代理。"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model_name: str = "ollama/qwen3-coder:latest"):
        """
        初始化UAV代理并配置模型。
        
        Args:
            ollama_url: Ollama API端点的URL
            model_name: 代理使用的模型名称
        """
        self.model = model_name
        self.api_base = ollama_url
        

    def initialize_agent(self) -> CodeAgent:
        """
        初始化并配置CodeAgent，设置工具和指令。
        
        Returns:
            配置好的CodeAgent实例
        """
        model = LiteLLMModel(
            model_id=self.model,
            api_base=self.api_base,
            temperature=0.2,
            max_completion_tokens=2048,
            seed=0
        )

        agent = CodeAgent(
            tools=[take_off_vehicle, land_vehicle, move_vehicle_to, turn_to, inspect, get_position], 
            model=model, 
            stream_outputs=True,
            instructions="""
# 角色
你是一个智能无人机(UAV)控制代理，负责解析自然语言指令并在AirSim模拟环境中执行精确的无人机操作。
你的职责是将高级任务目标转换为使用可用工具的具体操作代码。
你需要逐步执行任务。

## 操作指南和最佳实践
### 命名约定
- 无人机名称遵循"DroneX"格式，其中X从1开始
- 对象名称要具体，使用英文名称，不要使用中文
### 工具选择
- 除非明确要求，否则不要调用take_off_vehicle()或land_vehicle()
- 不要使用inspect()来定位对象；该工具用于回答环境调查相关问题
### 导航指南
- 飞向目标对象时，在对象的x轴方向保持-10米的安全距离
### 目标定位
- 当需要定位对象时，使用get_position()获取位置，尝试3个同义词以避免错过目标名称（例如："person", "people", "crowd"）, 定位对象不包含无人机本体。
### 任务完成
- 完成任务后，调用final_answer()返回任务结果
        """)
        return agent
    
    def run(self, prompt: str) -> Union[str, dict, None]:
        """
        使用给定提示执行代理。
        
        Args:
            prompt: 无人机的自然语言指令
            
        Returns:
            代理执行的观察结果/结果
            
        Raises:
            Exception: 如果代理执行失败
        """
        try:
            agent = self.initialize_agent()
            observation = agent.run(prompt)
            return observation
        except Exception as e:
            print(f"执行代理时出错: {e}")
            raise

    def next(self):
        reset()


if __name__ == "__main__":
    try:
        test = UAVAgent()
        steps = [
        "两架无人机起飞",
        "定位人员",
        "定位车辆",
        "无人机1移动到车辆",
        "无人机2移动到人群"
        ]
        
        result = test.run("; ".join(steps))
        print("执行成功完成")
        print(f"结果: {result}")
    except Exception as e:
        print(f"执行任务{steps}失败: {e}")