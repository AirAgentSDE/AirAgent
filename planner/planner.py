'''
无人机任务规划器
'''


from ollama import chat
from planner.prompt.base import BASE_SYSTEM_INSTRUCTIONS
import json


class UAVPlanner:
    '''main class for UAV planning'''
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model_name: str = "qwen3:32b"):
        self.ollama_url = ollama_url
        self.model_name = model_name
        
    
    def _call_ollama(self, prompt: str) -> str:
        """Make API call to Ollama"""
        response = chat(
            model = self.model_name,
            messages = [
            {
                'role': 'system',
                'content': BASE_SYSTEM_INSTRUCTIONS
            },
            {
                'role': 'user',
                'content': prompt
            }],
            options = {
                'temporature': 0.2,
                'top_p': 0.6,
                'top_k': 40,
                'seed' : 42
            }
        )
        content = response.message.content
        output = content.split('```json')[1].split('```')[0].strip()
        # Use the is_valid_json function to check and parse JSON
        output = is_valid_json(output)
        if output is None:
            raise ValueError("Invalid JSON format in response")
        return output


def is_valid_json(json_str: str):
    """
    Check if a given string is in a valid JSON structure.

    Args:
        json_str (str): The string to be checked.

    Returns:
        dict or list or None: The parsed JSON object if the string is valid, None otherwise.
    """
    try:
        obj = json.loads(json_str)
        return obj
    except json.JSONDecodeError:
        return None


def main():
    # Initialize planner
    planner = UAVPlanner(
        ollama_url="http://localhost:11434",
        model_name="qwen3:32b"  # or "qwen3:8b" for smaller model
    )
    task = input("请输入您的任务指令：")
    res = planner._call_ollama(task)
    print(res)
    return res


if __name__ == "__main__":
    main()