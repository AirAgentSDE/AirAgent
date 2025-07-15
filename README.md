# air_agent
An agentic UAV system

## components
The system take a plan-act architecture(Erdogan et al., 2025),
consists of three components: a high level planner, a low level controller, and a semantic mapper


### high level planner
Creating a step by step plan for the UAV agent to follow
see `hlp/planner.py` for more details

### low level controller
Controlling the UAV agent to follow the plan
see `llc` for more details

### semantic mapper
Mapping the surrounding environment to a graph representation dictionary
provided to low level controller, to ensure the generated plan is grounded
see `mapper` for more details

## file structure
