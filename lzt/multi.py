from smolagents import CodeAgent, LiteLLMModel
from llc.airsim_wrapper import *
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
import traceback
from transformers import AutoModelForCausalLM
# transformers 会默认 fallback 到 pt 权重


# 新增：多步任务的运行器
def run_task_sequence(agent, tasks, vehicle_name):
    results = []
    for task in tasks:
        try:
            print(f"[{vehicle_name}] 执行任务：{task}")
            result = agent.run(task, additional_args={"vehicle_name": vehicle_name})
            results.append({"task": task, "result": result})
        except Exception as e:
            error_info = traceback.format_exc()
            results.append({"task": task, "error": str(e), "trace": error_info})
    return results

# 创建并运行单个无人机的智能体任务
def create_and_run_drone_agent(model_config, task_list, vehicle_name):
    try:
        model = LiteLLMModel(
            model_id=model_config["model_id"],
            api_base=model_config["api_base"],
        )
        agent = CodeAgent(
            tools=[takeoff, land, fly_to],
            model=model
        )
        return {
            "vehicle_name": vehicle_name,
            "status": "success",
            "results": run_task_sequence(agent, task_list, vehicle_name)
        }
    except Exception as e:
        return {
            "vehicle_name": vehicle_name,
            "status": "error",
            "error": str(e),
            "trace": traceback.format_exc()
        }

# 并发运行所有无人机任务
def run_concurrent_multiprocessing():
    model_config = {
        "model_id": "ollama/mistral:instruct",
        "api_base": "http://localhost:11434"
    }

    # 多无人机分配独立任务序列（任务用中文写）
    drone_tasks = {
        "Drone1": [
            "请用 Python 编写名为 Drone1 的无人机起飞代码，使用 takeoff(vehicle_name='Drone1')，以代码块形式输出，使用 ```py 开始，以 <end_code> 结束,不要多余内容。",
            "请用 Python 编写 Drone1 飞往坐标点 (0, 0, -2) 的代码，先定义 destination = (0, 0, -2)，再使用 fly_to(point = destination, 'Drone1')。输出为代码块，不要多余内容。",
            "请用 Python 编写 Drone1 的降落代码，使用 land(vehicle_name='Drone1')，代码块格式输出。"
        ],
        "Drone2": [
            "请用 Python 编写名为 Drone2 的无人机起飞代码，使用 takeoff(vehicle_name='Drone2')，以代码块形式输出，使用 ```py 开始，以 <end_code> 结束,不要多余内容。",
            "请用 Python 编写 Drone2 飞往坐标点 (1, 2, -1) 的代码，先定义 destination = (1, 2, -1)，再使用 fly_to(point = destination, 'Drone2')。输出为代码块，不要多余内容。",
            "请用 Python 编写 Drone2 的降落代码，使用 land(vehicle_name='Drone2')，代码块格式输出。"
        ],
        "Drone3": [
            "请用 Python 编写名为 Drone3 的无人机起飞代码，使用 takeoff(vehicle_name='Drone3')，以代码块形式输出，使用 ```py 开始，以 <end_code> 结束,不要多余内容。",
            "请用 Python 编写 Drone3 飞往坐标点 (-1, 2, -1) 的代码，先定义 destination = (-1, 2, -1)，再使用 fly_to(point = destination, 'Drone3')。输出为代码块，不要多余内容。",
            "请用 Python 编写 Drone3 的降落代码，使用 land(vehicle_name='Drone3')，代码块格式输出。"
        ]
    }

    results = []

    with ProcessPoolExecutor(max_workers=len(drone_tasks)) as executor:
        future_to_drone = {
            executor.submit(create_and_run_drone_agent, model_config, tasks, name): name
            for name, tasks in drone_tasks.items()
        }

        for future in as_completed(future_to_drone):
            drone = future_to_drone[future]
            try:
                result = future.result()
                results.append(result)
                print(f"[{drone}] 完成：{result['status']}")
            except Exception as e:
                print(f"[{drone}] 异常：{e}")
                results.append({"vehicle_name": drone, "status": "error", "error": str(e)})

    return results

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn', force=True)
    print("正在启动多无人机并行任务...")
    start = time.time()
    results = run_concurrent_multiprocessing()
    end = time.time()
    print(f"所有无人机任务完成，用时：{end - start:.2f}秒")
    for r in results:
        print(f"\n{r['vehicle_name']} 执行状态：{r['status']}")
        if r['status'] == "success":
            for step in r["results"]:
                print(f"  - 任务：{step['task']}，结果：{step.get('result', '失败')}")
        else:
            print(f" 错误：{r['error']}")
            print(r.get("trace", ""))
