from planner.planner import UAVPlanner
from agent.actor import UAVAgent

def test_planner_actor():
    # Create a planner instance
    planner = UAVPlanner(
        ollama_url="http://localhost:11434/v1",
        model_name="qwen3:32b"  # Using a heavier model for sophisticated planning
    )
    
    # Test task
    task = "请无人机起飞并检查周围的环境"
    
    # Generate a plan
    plan = planner.generate_plan(task)
    print("Generated Plan:")
    print(plan)

if __name__ == "__main__":
    test_planner_actor()