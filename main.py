from planner.planner import UAVPlanner
from agent.actor import UAVAgent


def main():
    planner = UAVPlanner(
        ollama_url="http://localhost:11434/v1",
        model_name="qwen3:32b" # Should be a heavier model for sophisticated planning
    )
    task = input("请输入您的任务指令：")
    plan = planner.generate_plan(task)
    agent = UAVAgent(
        ollama_url="http://localhost:11434",
        model_name="ollama/qwen3:8b" # Should be a lighter model for quick execution

    )
    agent.run(plan)




if __name__ == "__main__":
    main()