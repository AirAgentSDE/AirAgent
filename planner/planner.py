'''
UAV Task Planner
'''

from openai import OpenAI
from planner.prompt.base import BASE_SYSTEM_INSTRUCTIONS
from planner.prompt.example import example1, example2
import json


class UAVPlanner:
    '''Main class for UAV planning'''
    def __init__(self, ollama_url: str = "http://:11434/v1", model_name: str = "qwen3:32b"):
        self.ollama_url = ollama_url
        self.model_name = model_name
        self.client = OpenAI(base_url=ollama_url, api_key="ollama")
        self.system_instructions = BASE_SYSTEM_INSTRUCTIONS

    def query_llm(self, prompt: str) -> str:
        """
        Query the LLM with the given prompt.

        Args:
            prompt (str): The prompt to query the LLM with.

        Returns:
            str: The response from the LLM.
        """
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_instructions},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2048,
            temperature=1
        )
        return response.choices[0].message.content.strip()
        
    def generate_plan(self, task: str) -> dict:
        """
        Generate a detailed plan with mission, current step, and to-do list for the UAV agent to execute.

        Args:
            task (str): The high-level task description from the user.

        Returns:
            dict: A detailed plan containing mission, current step, and to-do list.
        """
        # Create the prompt for the LLM with examples
        prompt = f"""
        Given the task: {task}
        
        Please provide your reasoning in a Socratic Q&A format, followed by a detailed plan in JSON format.
        Make sure to break down your given mission into subgoals, and determine the most appropriate first action to begin the mission.
        Use the action space: takeoff, land, move_to, turn_to, inspect, look_for.
        
        Here are some examples of how to structure your response:
        
        {example1}
        
        {example2}
        """
        
        # Query the LLM to get the plan
        llm_response = self.query_llm(prompt)
        
        # Try to extract JSON from the response
        try:
            # Find the JSON part in the response (between [Plan] markers or braces)
            plan_start = llm_response.find('[Plan]')
            if plan_start != -1:
                # Extract everything after [Plan]
                json_str = llm_response[plan_start + 6:].strip()
                # Find the first opening brace and last closing brace
                start = json_str.find('{')
                end = json_str.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = json_str[start:end]
            else:
                # If no [Plan] marker, try to find JSON directly
                start = llm_response.find('{')
                end = llm_response.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = llm_response[start:end]
                else:
                    raise ValueError("No JSON found in response")
            
            plan = json.loads(json_str)
            return plan
        except (json.JSONDecodeError, ValueError) as e:
            # If JSON parsing fails, create a basic plan structure
            return {
                "mission": task,
                "current_step": {
                    "description": "Take off the drone",
                    "action": {
                        "type": "takeoff",
                        "vehicle": "Drone1"
                    }
                },
                "to_do_list": [
                ]
            }