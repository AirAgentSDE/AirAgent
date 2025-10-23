# Project Overview

This is an intelligent control agent system for Unmanned Aerial Vehicles (UAVs) based on the AirSim simulation environment. The project utilizes Large Language Models (LLMs) and Vision Language Models (VLMs) to parse natural language instructions and convert them into specific UAV operation sequences, thereby achieving intelligent control of UAVs.

Main Technology Stack:
- Python
- AirSim (UAV simulation platform)
- smolagents (for building agents and tools)
- LiteLLM (for interacting with LLMs)
- OpenCV (for image processing)

The project architecture is divided into two main modules:
1. **e2e (End-to-End Execution)**: Contains the implementation of UAV agents and AirSim API wrappers, responsible for executing specific UAV control commands.
2. **hlp (High-Level Planning)**: Contains task planners, responsible for decomposing user instructions into executable high-level action plans.

# 项目结构

```
air_agent/
├── e2e/
│   ├── __init__.py
│   ├── actor.py
│   └── airsim_wrapper.py
└── hlp/
    ├── __init__.py
    ├── planner.py
    └── prompt/
        ├── base.py
        └── example.py
```

## e2e Module

- `actor.py`: Defines the `UAVAgent` class, responsible for initializing LLM models and agents, and executing user instructions.
- `airsim_wrapper.py`: Wraps the AirSim API, providing tools such as takeoff, landing, movement, turning, and detection for agent use.

## hlp Module

- `planner.py`: Defines the `UAVPlanner` class, responsible for converting user instructions into executable high-level action plans.
- `prompt/base.py`: Defines the system instructions for the planner, including planning steps and output formats.
- `prompt/example.py`: Provides examples of planner outputs.

# Development and Execution

## Environment Dependencies

- AirSim simulation environment
- Python 3.x
- Related Python libraries (see code import section for details)

## Execution Method

1. Start the AirSim simulation environment.
2. Run the `UAVAgent` in `actor.py` to execute specific UAV control tasks.
3. Run the `UAVPlanner` in `planner.py` to generate high-level action plans.

## Development Conventions

- UAV naming follows the "DroneX" format.
- Object names should be in English, avoiding Chinese or generic terms.
- Maintain safe distance when flying towards target objects.
- Code follows Python standard naming and formatting conventions.