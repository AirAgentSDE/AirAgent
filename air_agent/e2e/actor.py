from smolagents import CodeAgent, LiteLLMModel
import airsim
# from .airsim_wrapper import *
from airsim_wrapper import *
import json
import math
import numpy as np
import time


class UAVAgent:
    def __init__(self, ollama_url: str = "http://localhost:11434", model_name: str = "ollama/qwen3-coder:30b"):
        self.model_id = model_name
        self.api_base = ollama_url
        

    def initialize_agent(self):
        model = LiteLLMModel(
            model_id=self.model_id,
            api_base=self.api_base,
            temperature=0.2,
            max_completion_tokens=2048,
            seed=900
        )

        agent = CodeAgent(tools=[take_off_vehicle, land_vehicle, move_vehicle_to, turn_to, inspect, get_position], model=model, stream_outputs=True,
                          instructions="""
# 角色
你是一个智能无人机(UAV)控制代理, 负责解析自然语言指令并在AirSim仿真环境中执行精确的无人机操作。
你的职责是将高级任务目标转化为使用可用工具的具体操作序列。
你需要逐步执行任务。

# 操作指南与最佳实践
## 命名规范
- 无人机名称遵循"DroneX"格式, 其中X是从1开始的数字
- 对物体名称要具体。使用英文名称，不要用中文。例如："person"、"people"、"crowd"。避免使用通用术语如"transportation tool"
## 工具选择
- 除非明确要求, 否则不要调用take_off_vehicle()或land_vehicle()
- 不要使用inspect()定位物体，该工具用于回答调查环境相关问题
## 导航规范
- 飞向目标物体时, 需保持与物体在x轴方向-10米的安全距离
## 目标定位
- 需要定位物体时, 使用get_position()获取位置, 应尝试5个同义词避免遗漏目标名称(例如："person"、"people"、"crowd")

        """)
        return agent
    
    def run(self, prompt):
        agent = self.initialize_agent()
        observation = agent.run(prompt)
        return observation




if __name__ == "__main__":
    test = UAVAgent()
    steps = ["Both UAVs take off",
    "UAV1 move towards the transportation tool",
    "UAV2 move towards the crowd"]
    previous_step = []
    
    print(f"\n计划包含 {len(steps)} 个步骤")
    
    for i, step in enumerate(steps):
        print(f"\n--- 执行步骤 {i+1}/{len(steps)} ---")
        print(f"当前步骤: {step}")
        print(f"已完成步骤: {' '.join(previous_step) if previous_step else '无'}")
        prompt = f"Already completed {','.join(previous_step) if previous_step != [] else 'nothing so far'}. Now do **{step}**"
        
        # 执行当前步骤并等待完成
        result = test.run(prompt)
        print(f"步骤 {i+1} 完成，结果: {result}")
        
        # 添加到已完成列表
        previous_step.append(step)
        # 短暂停顿确保步骤执行完毕
        time.sleep(1)
        