'''
无人机任务规划器，通过提示链技术增强结果
'''

from litellm import completion
from hlp.prompt.base_zh import REASONING_SYSTEM_INSTRUCTIONS, PLANNING_SYSTEM_INSTRUCTIONS
import json
import re


class UAVPlanner:
    '''无人机规划器主类'''
    def __init__(self, ollama_url: str = "http://localhost:11434", model_name: str = "ollama/gpt-oss:20b"):
        self.base_url = ollama_url
        self.model_name = model_name
        self.reasoning_instructions = REASONING_SYSTEM_INSTRUCTIONS
        self.planning_instructions = PLANNING_SYSTEM_INSTRUCTIONS

    def query_llm(self, prompt: str, system_instructions: str, stage_name: str = "") -> str:
        """LLM 调用端口"""
        print(f"\n=== {stage_name} ===")
        response = completion(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": prompt}
            ],
            api_base=self.base_url,
            stream=True,
            temperature=0.2,
            reasoning_effort="high",
            seed=42
        )
        
        content_chunks = []
        for chunk in response:
            if chunk.choices[0].delta.content:
                content_chunks.append(chunk.choices[0].delta.content)
                print(chunk.choices[0].delta.content, end="", flush=True)
        
        return "".join(content_chunks)
            

    def stage1_reasoning(self, task: str) -> str:
        """Stage 1: Mission reasoning and analysis"""
        prompt = f"""
Analyze the following UAV mission:

Task: {task}
"""
        
        reasoning_response = self.query_llm(prompt, self.reasoning_instructions, "任务分析")
        return reasoning_response

    def stage2_planning(self, task: str, reasoning_result: str) -> str:
        """Stage 2: Structured planning generation"""
        # Replace the context placeholder in planning instructions
        planning_instructions = self.planning_instructions.replace(
            "{{reasoning-analysis}}", reasoning_result
        )
        
        prompt = f"""
Generate an executable action plan based on the following UAV mission and reasoning analysis:

Task: {task}
"""
        
        planning_response = self.query_llm(prompt, planning_instructions, "计划制定")
        return planning_response

    def generate_plan(self, task: str) -> dict:
        """Generate complete plan using two-stage approach"""
        print(f"\n已接到任务：{task}，正在制定计划...")
        print("=" * 60)
        
        # Stage 1: Chain Reasoning
        reasoning_result = self.stage1_reasoning(task)
        print("=" * 60)
        
        # Stage 2: Planning
        planning_result = self.stage2_planning(task, reasoning_result)
        print("=" * 60)
        
        # 解析规划结果为JSON格式
        try:
            # 清理规划结果，提取JSON部分
            cleaned_planning_result = planning_result.strip()
            # 如果结果以方括号开头，尝试直接解析
            if cleaned_planning_result.startswith('[') and cleaned_planning_result.endswith(']'):
                plan_json = json.loads(cleaned_planning_result)
            else:
                # 否则尝试提取方括号内的内容
                match = re.search(r'\[(.*?)\]', cleaned_planning_result, re.DOTALL)
                if match:
                    # 将行动列表转换为JSON数组
                    actions = [action.strip().strip('"\'') for action in match.group(1).split(',') if action.strip()]
                    plan_json = actions
                else:
                    plan_json = cleaned_planning_result
        except json.JSONDecodeError:
            # 如果解析失败，返回原始结果
            plan_json = planning_result
        
        print("\n" + "=" * 60)
        print("\U00002705 任务计划阶段已完成!")
        
        return plan_json

    def generate_response(self, task: str) -> str:
        """生成响应文本（与之前版本兼容）"""
        print(f"\n已接到任务：{task}，正在制定计划...")
        print("=" * 60)
        
        # Stage 1: Chain Reasoning
        reasoning_result = self.stage1_reasoning(task)
        print("=" * 60)
        
        # Stage 2: Planning
        planning_result = self.stage2_planning(task, reasoning_result)
        print("=" * 60)
        
        print("\n" + "=" * 60)
        print("\U00002705 任务计划阶段已完成!")
        
        return planning_result

    def extract_plan(self, response: str) -> list:
        """从响应中提取计划列表"""
        try:
            # 清理响应，提取JSON部分
            cleaned_response = response.strip()
            # 如果结果以方括号开头，尝试直接解析
            if cleaned_response.startswith('[') and cleaned_response.endswith(']'):
                plan_list = json.loads(cleaned_response)
            else:
                # 否则尝试提取方括号内的内容
                match = re.search(r'\[(.*?)\]', cleaned_response, re.DOTALL)
                if match:
                    # 将行动列表转换为字符串数组
                    actions = [action.strip().strip('"\'') for action in match.group(1).split(',') if action.strip()]
                    plan_list = actions
                else:
                    plan_list = []
            return plan_list
        except json.JSONDecodeError:
            # 如果解析失败，返回空列表
            return []

if __name__ == "__main__":
    planner = UAVPlanner()

    # 测试任务
    test_task = "启动两架无人机，一架去找人，一架去找车辆"

    print("开始测试 UAVPlanner...")

    # 测试 generate_plan 方法
    plan = planner.generate_plan(test_task)

    print("\n使用 generate_plan 方法生成的计划:")
    print(plan)
    print(f"计划类型: {type(plan)}")

    # 验证输出是否为列表格式
    if isinstance(plan, list):
        print("✓ 计划格式正确 (列表)")
        for i, action in enumerate(plan):
            print(f"  {i+1}. {action}")
    else:
        print("✗ 计划格式不正确")

    print("\n" + "="*50)
