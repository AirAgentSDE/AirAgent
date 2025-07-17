# air_agent
An agentic UAV system

## components
The system take plan-act architecture(Erdogan et al., 2025)

### high level planner
Creating a step by step plan for the UAV agent to follow,
see `planner` for more details

### low level actor
Controlling the UAV agent to follow the plan,
see `agent` for more details

### semantic mapper
Mapping the surrounding environment to a graph representation JSON,
provided to low level actor, to ensure the generated plan is grounded,
see `mapper` for more details

## file structure
