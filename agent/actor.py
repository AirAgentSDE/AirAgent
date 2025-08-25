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
        """
        Execute a prompt with the UAV agent.
        
        Args:
            prompt (str): The task description to execute
            
        Returns:
            The result of the agent execution
        """
        agent = self.initialize_agent()
        # Directly pass the string prompt to the agent
        return agent.run(prompt)


if __name__ == "__main__":
    test = UAVAgent()
    test.run("起飞无人机 Drone1，飞到坐标点 (10, 10, -5)，转向 90 度，描述所有看到的物体。")