'''
无人机任务规划器
'''


from typing import List, Dict, Any
from enum import Enum
from pydantic import BaseModel, dataclasses
from ollama import chat
import json
import traceback


class UAVPlanner:
    '''main class for UAV planning'''
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model_name: str = "qwen3:8b"):
        self.ollama_url = ollama_url
        self.model_name = model_name
        self.action_base = self._define_action_base()
        
    def _define_action_base(self) -> Dict:
        """Define the available actions"""
        return {
        }
    
    def _create_prompt(self, task: str) -> str:
        """Create a structured prompt for the LLM"""
        # Build prompt in parts for better readability
        intro = """ """
        task = f""
        actions = f""
        requirements = """

"""
        prompt = intro + task + actions + requirements + " "
        return prompt
    

    def _call_ollama(self, prompt: str) -> Any:
        """Make API call to Ollama"""
        
        response = chat(
            model = self.model_name,
            messages = [{
                'role': 'user',
                'content': prompt
            }],
            options = {
                'temporature': 0.3,
                'seed': 42
            }
        )
        response = response.message['content']
        return 
    

    def generate_plan(self, task_description: str) -> List[Action]:
        """Generate a UAV action plan for the given task"""        
        # Create prompt
        prompt = self._create_prompt(task_description)
        
        # Call LLM
        response = self._call_ollama(prompt)
        return response
    

def main():
    try:
        # Initialize planner
        planner = UAVPlanner(
            ollama_url="http://localhost:11434",
            model_name="deepseek-r1:8b-0528-qwen3-fp16"
        )
        
        # Example tasks
        example_tasks = [
            "检查风力发电机是否遭到破坏",
            "在森林区域内搜索失踪的人",
            "检查一条河流沿岸的污染情况，从(10, 20)到(50, 60)的矩形区域进行检查",
            "最近的船只在哪里？",
        ]
        
        print("无人机正在待命，准备执行任务。")
        print("任务示例：")
        for i, task in enumerate(example_tasks, 1):
            print(f"{i}. {task}")
        
        print("\n选项:")
        print("1-4: 选择示例任务")
        print("5: 输入自定义任务")
        print("0: 退出")
        
        while True:
            try:
                choice = input("\n请输入您的选择: ").strip()
                
                if choice == "0":
                    print("正在退出程序...")
                    break
                    
                elif choice in ["1", "2", "3", "4"]:
                    idx = int(choice) - 1
                    task = example_tasks[idx]
                    print(f"\n已接收任务: {task}")
                    
                    try:
                        print("正在生成飞行计划，请稍候...")
                        actions = planner.generate_plan(task)
                        planner.print_plan(actions)
                        
                        # Ask if user wants to export
                        export = input("\n是否导出计划? (y/n): ").strip().lower()
                        if export == 'y':
                            filename = f"uav_plan_{choice}.json"
                            print(f"正在将计划导出至文件: {filename}")
                            planner.export_plan(actions, filename)
                            print(f"成功导出至 {filename}")
                            
                    except Exception as e:
                        print(f"error generating plan: {e}")
                        traceback.print_exc()
                        
                elif choice == "5":
                    custom_task = input("请输入您的指令: ").strip()
                    if custom_task:
                        try:
                            print("正在生成飞行计划，请稍候...")
                            actions = planner.generate_plan(custom_task)
                            planner.print_plan(actions)
                            
                            export = input("\n是否导出计划? (y/n): ").strip().lower()
                            if export == 'y':
                                filename = "custom_uav_plan.json"
                                print(f"正在将计划导出至文件: {filename}")
                                planner.export_plan(actions, filename)
                                print(f"成功导出至 {filename}")
                                
                        except Exception as e:
                            print(f"error generating plan: {e}")
                            traceback.print_exc()
                else:
                    print("无效选择, 请输入 0-5 之间的数字")
                    
            except KeyboardInterrupt:
                print("\n检测到键盘中断, 正在安全退出...")
                break
                
            except Exception as e:
                print(f"unknown exception: {e}")
                traceback.print_exc()
    except Exception as e:
        print(f"error initialization: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()