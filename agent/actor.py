from smolagents import CodeAgent, LiteLLMModel, GradioUI
import airsim
from agent.airsim_wrapper import *
import json


class UAVAgent:
    """
    A UAV agent that interacts with the AirSim environment.
    It uses a lightweight LLM model to process commands and execute actions.
    """
    def __init__(self, ollama_url: str = "http://localhost:11434", model_name: str = "ollama/qwen3:8b"):
        self.model_id = model_name
        self.api_base = ollama_url

    def initialize_agent(self):
        model = LiteLLMModel(
            model_id=self.model_id,
            api_base=self.api_base,
        )

        agent = CodeAgent(tools=[take_off_vehicle, land_vehicle, move_vehicle_to, turn_to, inspect, look_for], model=model,
                          additional_authorized_imports=["math", "time", "numpy"],
                          instructions="""
You are a helpful assistant for controlling drones in an AirSim environment.
You should follow an mission plan provided to you, and complete the tasks step by step.
when refer to a object_name or vehicle_name, always call in English, such as "turbine1", "solarpanels", "car", "crowd",
if you get a name in other language, please translate it to English first.

        """ + "/no_think")
        return agent
    def run(self, prompt):
        agent = self.initialize_agent()
        if isinstance(prompt, str):
            prompt = [prompt]
        elif isinstance(prompt, dict):
            # Check if the plan has the old format with 'plan' key
            if 'plan' in prompt:
                prompt = f"note your mission: {prompt['mission']}\n                given relevant_objects: {prompt['relevant_objects']}\n                what you should do: {prompt['reasoning']}\n                execute the following plan step by step: {prompt['plan']}"
            # Check if the plan has the new format with 'subgoals' key
            elif 'subgoals' in prompt:
                prompt = f"note your mission: {prompt['mission']}\n                execute the following subgoals step by step: {prompt['subgoals']}"
            else:
                raise ValueError("Parsed prompt is not in a valid format. Expected 'plan' or 'subgoals' key in dict.")
        else:
            raise ValueError("Parsed prompt is not in a valid format. Expected str or dict.")
        return agent.run(prompt)


if __name__ == "__main__":
    test = UAVAgent()
    test.run("起飞无人机 Drone1，飞到坐标点 (10, 10, -5)，转向 90 度，描述所有看到的物体。")