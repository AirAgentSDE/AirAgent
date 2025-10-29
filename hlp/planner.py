'''
无人机任务规划器
'''

from litellm import completion
from hlp.prompt.base_zh import SYSTEM_INSTRUCTIONS
import json
import re


class UAVPlanner:
    '''无人机规划器主类'''
    def __init__(self, ollama_url: str = "http://localhost:11434", model_name: str = "ollama/qwen3:30b-instruct"):
        self.base_url = ollama_url
        self.model_name = model_name
        self.system_instructions = SYSTEM_INSTRUCTIONS

    def query_llm(self, prompt: str) -> str:
        """LLM 调用端口"""
        response = completion(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_instructions},
                {"role": "user", "content": prompt}
            ],
            api_base=self.base_url,
            stream=False,
            temperature=0.4,
            seed=0
        )
        
        return response.choices[0].message.content
    
    

if __name__ == "__main__":
    planner = UAVPlanner()

    # 测试任务
    test_task = "启动两架无人机，一架去找人，一架去找车辆"

    print("开始测试 UAVPlanner...")
    plan = planner.query_llm(test_task)
    print(plan)

