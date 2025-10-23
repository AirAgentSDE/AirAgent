from smolagents import CodeAgent, LiteLLMModel
import airsim
from airsim_wrapper import *
import json
import math
import numpy as np
import time
from typing import Optional, Union


class UAVAgent:
    """UAV Agent for controlling drones in AirSim environment using natural language instructions."""
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model_name: str = "ollama/qwen3-coder:latest"):
        """
        Initialize the UAV agent with model configuration.
        
        Args:
            ollama_url: URL for the Ollama API endpoint
            model_name: Name of the model to use for the agent
        """
        self.model = model_name
        self.api_base = ollama_url
        

    def initialize_agent(self) -> CodeAgent:
        """
        Initialize and configure the CodeAgent with tools and instructions.
        
        Returns:
            Configured CodeAgent instance
        """
        model = LiteLLMModel(
            model_id=self.model,
            api_base=self.api_base,
            temperature=0.2,
            max_completion_tokens=2048,
            seed=0
        )

        agent = CodeAgent(
            tools=[take_off_vehicle, land_vehicle, move_vehicle_to, turn_to, inspect, get_position], 
            model=model, 
            stream_outputs=True,
            instructions="""
# Role
You are an intelligent UAV (Unmanned Aerial Vehicle) control agent responsible for parsing natural language instructions and executing precise UAV operations in the AirSim simulation environment.
Your responsibility is to convert high-level task objectives into specific operational code using available tools.
You need to execute tasks step by step.

## Operation Guidelines and Best Practices
### Naming Conventions
- UAV names follow the "DroneX" format, where X starts from 1
- Be specific with object names. Use English names, not Chinese.
### Tool Selection
- Do not call take_off_vehicle() or land_vehicle() unless explicitly requested
- Do not use inspect() to locate objects; this tool is for answering environment investigation-related questions
### Navigation Guidelines
- When flying towards target objects, maintain a safe distance of -10 meters in the x-axis direction from the object
### Target Localization
- When needing to locate objects, use get_position() to get position, try 3 synonyms to avoid missing target names (e.g.: "person", "people", "crowd")
### Task Completion
- After completing the task, call final_answer() to return task results
        """)
        return agent
    
    def run(self, prompt: str) -> Union[str, dict, None]:
        """
        Execute the agent with the given prompt.
        
        Args:
            prompt: Natural language instruction for the UAV
            
        Returns:
            Observation/result from the agent execution
            
        Raises:
            Exception: If agent execution fails
        """
        try:
            agent = self.initialize_agent()
            observation = agent.run(prompt)
            return observation
        except Exception as e:
            print(f"Error executing agent: {e}")
            raise




if __name__ == "__main__":
    try:
        test = UAVAgent()
        steps = [
        "Two drones take off",
        "Drone 1 moves to vehicle",
        "Drone 2 moves to crowd"
        ]
        
        result = test.run("; ".join(steps))
        print("Execution completed successfully")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Failed to execute UAV agent: {e}")