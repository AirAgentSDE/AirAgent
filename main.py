from smolagents import CodeAgent, LiteLLMModel
from airsim_wrapper import *



model = LiteLLMModel(
    model_id = "ollama_chat/qwen3",
    api_base = "http://localhost:11434",

)


agent = CodeAgent(tools=[takeoff, land], model=model)

agent.run("takeoff and land", additional_args={"vehicle_name": "Drone2"})