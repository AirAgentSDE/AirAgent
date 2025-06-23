'''
无人机任务规划器
'''


from typing import List, Dict, Any
from enum import Enum
from pydantic import BaseModel, dataclasses
from ollama import chat
import json
import traceback


class ActionType(Enum):
    TAKEOFF = "takeoff"
    LAND = "land"
    FLY_TO = "flyto"
    EXPLORE_AREA = "explore_area"


@dataclasses.dataclass
class Action():
    """Represents a single UAV action with parameters"""
    action_type: ActionType
    parameters: Dict[str, Any]
    description: str = ""


class ActionSeries(BaseModel):
    Series: list[Action]


@dataclasses.dataclass
class Position():
    """Represents a 3D position"""
    x: float
    y: float
    z: float


class UAVPlanner:
    '''main class for UAV planning'''
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model_name: str = "deepseek-r1:8b-0528-qwen3-fp16"):
        self.ollama_url = ollama_url
        self.model_name = model_name
        self.action_base = self._define_action_base()
        
    def _define_action_base(self) -> Dict[str, Dict]:
        """Define the available actions and their parameter schemas"""
        return {
            "takeoff": {
                "description": "Take off the UAV to 3 meters above the ground",
                "parameters": {}
            },
            "land": {
                "description": "Land the UAV at current position",
                "parameters": {}
            },
            "flyto": {
                "description": "Fly to a specific 3D coordinate",
                "parameters": {
                    "position": {
                        "type": "Position",
                        "description": "Target position in 3D space (x, y, z)",
                        "required": True
                    },
                    "speed": {
                        "type": "float",
                        "description": "Speed in meters per second",
                        "required": False
                    }
                }
            },
            "explore_area": {
                "description": "Explore a rectangular area defined by two corners",
                "parameters": {
                    "corner1": {
                        "type": "Position",
                        "description": "First corner of the rectangle (x1, y1, z1)",
                        "required": True
                    },
                    "corner2": {
                        "type": "Position",
                        "description": "Second corner of the rectangle (x2, y2, z2)",
                        "required": True
                    }
                }
            }
        }
    
    def _create_prompt(self, task_description: str) -> str:
        """Create a structured prompt for the LLM"""
        action_descriptions = []
        for action_name, action_info in self.action_base.items():
            params = []
            for param_name, param_info in action_info["parameters"].items():
                required = "(required)" if param_info["required"] else "(optional)"
                params.append(f" - {param_name}: {param_info['description']}{required}")
            
            param_str = "\n".join(params) if params else " - No parameters"
            action_descriptions.append(f"| {action_name}: {action_info['description']}{param_str}")
        
        # Build prompt in parts for better readability
        intro = """你是一个专业严谨的无人机规划专家，你需要根据给定的任务描述，生成一个可以逐步执行的无人机飞行计划: """
        task = f"\n\n任务: {task_description}"
        actions = "\n\n可行动作: " + '\n'.join(action_descriptions)
        requirements = """
\n\n要求:
1. 所有动作必须包含在可行动作列表中，不能假设或引入新动作。
2. 返回一个JSON格式的动作数组。
3. 每个动作必须包含："action"、"parameters"和"description"字段。描述需用简单的中文说明，例如：{"action": "takeoff", "parameters": {}, "description": "将无人机起飞至离地3米的高度。"}。
4. 标记为(required)的参数必须包含在动作中,
   标记为(optional)的参数可以不包含在动作中。
5. 确保动作执行顺序合理（起飞在飞行前，降落放在最后）。
6. 对于坐标和参数要具体明确。如果任务指令未包含必要参数值，需自行推断合理值。
7. 全球坐标系为NED(北、东、下), 注意Z轴方向, 负值表示地面以上, 正值表示地面以下。
8. 单次上升高度不得超过20米。
"""

        prompt = intro + task + actions + requirements + "\n\n请根据以上指令, 生成无人机飞行计划： "
        return prompt
    

    def _call_ollama(self, prompt: str) -> Any:
        """Make API call to Ollama"""
        
        response = chat(
            model = self.model_name,
            messages = [{
                'role': 'user',
                'content': prompt
            }],
            format = ActionSeries.model_json_schema(),
            options = {
                'temporature': 0.3,
                'seed': 42
            }
        )
        response = response.message['content']
        return ActionSeries.model_validate_json(response)
    

    def generate_plan(self, task_description: str) -> List[Action]:
        """Generate a UAV action plan for the given task"""        
        # Create prompt
        prompt = self._create_prompt(task_description)
        
        # Call LLM
        response = self._call_ollama(prompt)
        return response
    
    def print_plan(self, actions: List[Action]):
        """Print the action plan in a readable format"""
        print("\n" + "="*50)
        print("无人机飞行计划:")
        print("="*50)
        
        if isinstance(actions, ActionSeries):
            action_list = actions.Series    
        else:
            raise ValueError("Invalid action series format")
        
        for i, action in enumerate(action_list, 1):
            print(f"\nStep {i}: {action.action_type.value.upper()}")
            print(f"Description: {action.description}")
            if action.parameters:
                print("Parameters:")
                for key, value in action.parameters.items():
                    print(f"  - {key}: {value}")
        
        print("\n" + "="*50)
    
    def export_plan(self, actions: List[Action], filename: str):
        """Export the plan to a JSON file"""
        if not filename.endswith('.json'):
            raise ValueError("Filename must end with .json")
        
        plan_data = []
        if isinstance(actions, ActionSeries):
            actions = actions.Series
        else:
            raise ValueError("Invalid action series format")
        
        for action in actions:
            plan_data.append({
                "action": action.action_type.value,
                "parameters": action.parameters,
                "description": action.description
            })
        
        try:
            with open(filename, 'w') as f:
                json.dump(plan_data, f, indent=2)
        except IOError as e:
            raise Exception(f"Failed to write plan to file: {e}")


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