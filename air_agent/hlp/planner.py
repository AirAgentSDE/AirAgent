'''
UAV Task Planner
'''

from litellm import completion
from .prompt.base import BASE_SYSTEM_INSTRUCTIONS
from .prompt.example import example1
# from prompt.base import BASE_SYSTEM_INSTRUCTIONS
# from prompt.example import example1
import json


class UAVPlanner:
    '''Main class for UAV planning'''
    def __init__(self, ollama_url: str = "http://localhost:11434", model_name: str = "ollama/gpt-oss:20b"):
        self.base_url = ollama_url
        self.model_name = model_name
        self.system_instructions = BASE_SYSTEM_INSTRUCTIONS

    def query_llm(self, prompt: str) -> str:
        try:
            response = completion(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_instructions},
                    {"role": "user", "content": prompt}
                ],
                api_base=self.base_url,
                stream=True,
                temperature=0.2,
                reasoning_effort="high",
                seed=42
            )
            collected_responses = []
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    collected_responses.append(chunk.choices[0].delta.content)
                    print(chunk.choices[0].delta.content, end="", flush=True)
            return ''.join(collected_responses)
            
        except Exception as e:
            print(f"Error querying LLM: {e}")


    def generate_response(self, task: str) -> dict:
        prompt = f"""
        You task is {task}.

        Here are some output examples:
        {json.dumps(example1)}

        """
        
        llm_response = self.query_llm(prompt)
        return llm_response
        
    def extract_reasoning(self, llm_response: str) -> str:
        reasoning = llm_response.split("</推理>")[0].strip("<推理>")
        return reasoning
    
    def extract_plan(self, llm_response: str) -> str:
        plan = llm_response.split("<计划>")[1].strip("</计划>")
        plan = json.loads(plan)
        return plan


if __name__ == "__main__":
    planner = UAVPlanner()