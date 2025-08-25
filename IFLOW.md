# UAV Agent System - Developer Guide

This document serve as context for coding agent to take over the project development.
The system uses a plan-act architecture with a high-level planner generating mission plans and a low-level actor executing actions in an AirSim environment.

## System Architecture

The system follows a plan-act architecture:
1. **High-level Planner**: Generates detailed mission plans using a sophisticated LLM (qwen3:32b)
2. **Low-level Actor**: Executes actions in AirSim using a lightweight LLM (qwen3:8b)
3. **Semantic Mapper** (planned): Will provide environmental context as graph structures

## Core Components

### Planner (`planner/planner.py`)
- **Purpose**: Transforms user tasks into structured mission plans
- **Model**: `qwen3:32b` via Ollama at `http://localhost:11434/v1`
- **Process**:
  - Receives natural language tasks from `main.py`
  - Uses Socratic Q&A reasoning to decompose tasks
  - Outputs JSON plans with mission, current_step, and to_do_list
- **Key Methods**:
  - `generate_plan(task)`: Creates structured mission plan

### Actor (`agent/actor.py`)
- **Purpose**: Executes mission plans in AirSim environment
- **Model**: `ollama/qwen3:8b` via Ollama at `http://localhost:11434`
- **Framework**: Built with `smolagents` for tool calling capabilities
- **Key Methods**:
  - `run(plan)`: Executes mission plan step-by-step

### AirSim Wrapper (`agent/airsim_wrapper.py`)
- **Purpose**: Provides tool functions for UAV actions
- **Available Actions**:
  - `take_off_vehicle(vehicle_name)`: Launch drone
  - `land_vehicle(vehicle_name)`: Land drone
  - `move_vehicle_to(point, vehicle_name)`: Move to coordinates
  - `turn_to(yaw, vehicle_name)`: Rotate to angle
  - `inspect(visual_query, vehicle_name, camera_name)`: Analyze environment with VLM
  - `look_for(object_name, camera_name, vehicle_name)`: Detect objects

## System Workflow

1. **User Input**: Task entered via `main.py`
2. **Planning Phase**:
   - `UAVPlanner` processes task with `qwen3:32b`
   - Generates JSON plan with Socratic reasoning
3. **Execution Phase**:
   - `UAVAgent` receives plan
   - Processes plan with `ollama/qwen3:8b`
   - Executes actions via AirSim API
4. **Environment Interaction**: Actions performed through `airsim_wrapper.py` tools

## Setup Requirements

1. **AirSim**: Running simulation environment
2. **Ollama**: Serving LLMs locally with models:
   - `ollama pull qwen3:32b` (planner)
   - `ollama pull qwen3:8b` (actor)
   - `ollama pull qwen2.5vl:7b` (vision, optional)
3. **Python Dependencies**:
   ```bash
   pip install openai smolagents airsim numpy opencv-python
   ```

## Running the System

1. Start AirSim environment
2. Start Ollama service: `ollama serve`
3. Run main application: `python main.py`
4. Enter task when prompted

## Key Implementation Details

### Plan Structure
```json
{
  "mission": "Task description",
  "current_step": {
    "description": "Next action description",
    "action": {
      "type": "takeoff|land|move_to|turn_to|inspect|look_for",
      "parameters": "Action-specific parameters"
    }
  },
  "to_do_list": ["Remaining subtasks"]
}
```

### API Endpoints
- Planner: `http://localhost:11434/v1` (with /v1 suffix)
- Actor: `http://localhost:11434` (without /v1 suffix)

### Naming Conventions
- Object/vehicle names must be in English (e.g., "turbine1", "solarpanels")
- Non-English names should be translated before processing

## Testing

- `test_planner_actor.py`: Integration tests for planning and execution
- `agent/actor.py`: Contains basic execution test at file bottom
