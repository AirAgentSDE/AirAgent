from smolagents import CodeAgent, LiteLLMModel  
from airsim_wrapper import *  
import multiprocessing  
from concurrent.futures import ProcessPoolExecutor, as_completed  
import time  
  
def create_and_run_drone_agent(model_config, task, vehicle_name):  
    """Create agent and run task in separate process"""  
    try:  
        model = LiteLLMModel(  
            model_id=model_config["model_id"],  
            api_base=model_config["api_base"],  
        )  
        agent = CodeAgent(tools=[takeoff, land], model=model)  
        result = agent.run(task, additional_args={"vehicle_name": vehicle_name})  
        return {"vehicle_name": vehicle_name, "result": result, "status": "success"}  
    except Exception as e:  
        return {"vehicle_name": vehicle_name, "error": str(e), "status": "error"}  
  
def run_concurrent_multiprocessing():  
    model_config = {  
        "model_id": "ollama_chat/qwen3",  
        "api_base": "http://localhost:11434"  
    }  
      
    drones = ["Drone1", "Drone2", "Drone3"]  
    task = "takeoff and land"  
    results = []  
      
    with ProcessPoolExecutor(max_workers=len(drones)) as executor:  
        # Submit tasks to process pool  
        future_to_drone = {}  
        for drone_name in drones:  
            future = executor.submit(create_and_run_drone_agent, model_config, task, drone_name)  
            future_to_drone[future] = drone_name  
          
        # Collect results  
        for future in as_completed(future_to_drone):  
            drone_name = future_to_drone[future]  
            try:  
                result = future.result()  
                results.append(result)  
                print(f"Completed task for {drone_name}: {result['status']}")  
            except Exception as e:  
                print(f"Error with {drone_name}: {e}")  
                results.append({"vehicle_name": drone_name, "error": str(e), "status": "error"})  
      
    return results  
  
if __name__ == "__main__":  
    multiprocessing.set_start_method('spawn', force=True)  # For compatibility  
    print("Starting concurrent drone operations with multiprocessing...")  
    start_time = time.time()  
      
    results = run_concurrent_multiprocessing()  
      
    end_time = time.time()  
    print(f"All operations completed in {end_time - start_time:.2f} seconds")  
      
    for result in results:  
        print(f"Drone {result['vehicle_name']}: {result['status']}")
