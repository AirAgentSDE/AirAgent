from planner.planner import UAVPlanner
from agent.actor import UAVAgent
import time


def replan(planner, mission, failed_step, to_do_list):
    """
    Replan when a step fails after multiple attempts.
    
    Args:
        planner: UAVPlanner instance
        mission: Original mission description
        failed_step: The step that failed
        to_do_list: Remaining tasks
        
    Returns:
        dict: New plan with updated steps
    """
    # Create a replanning prompt that includes information about the failure
    replan_prompt = f"""
    The following step failed after multiple attempts: {failed_step['description']}
    Original mission: {mission}
    Remaining tasks: {to_do_list}
    
    Please provide a new plan that either:
    1. Modifies the failed step to make it achievable
    2. Provides an alternative approach to accomplish the same goal
    3. Skips the failed step if it's not essential and continues with remaining tasks
    
    Output your reasoning in a Socratic Q&A format, followed by a detailed plan in JSON format.
    """
    
    new_plan = planner.generate_plan(replan_prompt)
    return new_plan


def execute_step_with_retry(agent, step_description, max_attempts=3):
    """
    Execute a single step with retry mechanism.
    
    Args:
        agent: UAVAgent instance
        step_description: Description of the step to execute
        max_attempts: Maximum number of attempts before failing
        
    Returns:
        bool: True if successful, False if failed after max attempts
    """
    attempts = 0
    while attempts < max_attempts:
        try:
            print(f"Executing step: {step_description} (Attempt {attempts + 1}/{max_attempts})")
            # Execute the step through the agent
            result = agent.run(step_description)
            print(f"Step completed successfully: {step_description}")
            return True
        except Exception as e:
            attempts += 1
            print(f"Step failed: {step_description} (Attempt {attempts}/{max_attempts})")
            print(f"Error: {str(e)}")
            if attempts < max_attempts:
                print("Retrying...")
                time.sleep(2)  # Wait before retrying
            else:
                print(f"Step failed after {max_attempts} attempts: {step_description}")
                return False
    return False


def main():
    # Initialize planner and actor
    planner = UAVPlanner(
        ollama_url="http://localhost:11434/v1",
        model_name="qwen3:32b"  # Should be a heavier model for sophisticated planning
    )
    
    agent = UAVAgent(
        ollama_url="http://localhost:11434",
        model_name="ollama/qwen3:8b"  # Should be a lighter model for quick execution
    )
    
    # Get task from user
    task = input("请输入您的任务指令：")
    
    # Generate initial plan
    print("Generating initial plan...")
    plan = planner.generate_plan(task)
    
    # Initialize agent for execution
    execution_agent = agent.initialize_agent()
    
    # Extract mission components
    mission = plan.get("mission", task)
    current_step = plan.get("current_step", {})
    to_do_list = plan.get("to_do_list", [])
    
    print(f"Mission: {mission}")
    print(f"Initial step: {current_step.get('description', 'N/A')}")
    print(f"Tasks to do: {len(to_do_list)}")
    
    # Execute the initial step
    if current_step:
        step_description = current_step.get('description', '')
        success = execute_step_with_retry(execution_agent, step_description)
        
        if not success:
            print("Initial step failed. Attempting to replan...")
            new_plan = replan(planner, mission, current_step, to_do_list)
            # Update plan with new plan
            mission = new_plan.get("mission", mission)
            current_step = new_plan.get("current_step", {})
            to_do_list = new_plan.get("to_do_list", [])
            
            # Try executing the new first step
            if current_step:
                step_description = current_step.get('description', '')
                success = execute_step_with_retry(execution_agent, step_description)
                if not success:
                    print("Replanned step also failed. Exiting.")
                    return
    
    # Execute remaining steps in the to-do list
    while to_do_list:
        # Get the next task from the to-do list
        next_task = to_do_list.pop(0)
        print(f"Next task: {next_task}")
        
        # Execute the task with retry mechanism
        success = execute_step_with_retry(execution_agent, next_task)
        
        # If the task failed after max attempts, replan
        if not success:
            print("Task failed after maximum attempts. Replanning...")
            # Create a dummy step for replanning
            failed_step = {"description": next_task}
            new_plan = replan(planner, mission, failed_step, to_do_list)
            
            # Update with new plan
            mission = new_plan.get("mission", mission)
            current_step = new_plan.get("current_step", {})
            to_do_list = new_plan.get("to_do_list", [])
            
            # If we got a new current step, execute it
            if current_step:
                step_description = current_step.get('description', '')
                success = execute_step_with_retry(execution_agent, step_description)
                if not success:
                    print("Replanned step also failed. Continuing with remaining tasks.")
    
    print("Mission completed successfully!")


if __name__ == "__main__":
    main()