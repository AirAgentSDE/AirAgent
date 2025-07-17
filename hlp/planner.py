'''
无人机任务规划器
'''


from ollama import chat
import json
import gradio as gr
from prompt.base import BASE_SYSTEM_INSTRUCTIONS


class UAVPlanner:
    '''main class for UAV planning'''
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model_name: str = "qwen3:8b"):
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
                'temporature': 0.4,
                'seed': 42
            }
        )
        content = response.message.content
        output = content.split('```json')[1].split('```')[0].strip()
        return output
    

def main():
    # Initialize planner
    planner = UAVPlanner(
        ollama_url="http://localhost:11434",
        model_name="qwen3:32b"  # or "qwen3:8b" for smaller model
    )
    task = input("Enter the UAV task description: ")
    res = planner._call_ollama(task)
    print(res)



if __name__ == "__main__":
    main()