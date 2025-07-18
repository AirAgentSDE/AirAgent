from smolagents import CodeAgent, LiteLLMModel, GradioUI
import airsim
from airsim_wrapper import *


model = LiteLLMModel(
    model_id = "ollama_chat/qwen3:8b",
    api_base = "http://localhost:11434",

)


agent = CodeAgent(tools=[takeOffVehicle, landVehicle, moveVehicleTo, turn_to, inspect, get_object_position], model=model,
                  instructions = """
            

            """.strip())
