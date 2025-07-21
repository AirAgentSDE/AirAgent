from smolagents import CodeAgent, LiteLLMModel, GradioUI
import airsim
from airsim_wrapper import *


model = LiteLLMModel(
    model_id = "ollama/qwen3:8b",
    api_base = "http://localhost:11434",

)


agent = CodeAgent(tools=[takeOffVehicle, landVehicle, moveVehicleTo, turn_to, inspect, get_object_position], model=model,
                  instructions = """
You are a helpful assistant for controlling drones in an AirSim environment.

Remember, you should always start with `takeoff()` before using other tools.

Remember the simulator takes a NED (North, East, Down) coordinate system, so negative value in the z axis means up.

Do not land until you are explicitly told to do so.

When giving a comlicated task, always think step by step, try to break it down into smaller tasks, and use the tools provided to accomplish each step.  

Here are the known objects in the scene:
- turbine1 风力发电机1
- turbine2 风力发电机2
- solarpanels 太阳能电池板
- car 汽车
- crowd 人群
- tower1 塔1
- tower2 塔2
- tower3 塔3    

Here are some examples on how you can handle the task:



            """.strip())

GradioUI(agent).launch(share=False)