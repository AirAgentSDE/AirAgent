# 项目概述

本项目是一个基于计划-执行架构（plan-act architecture）的无人机代理系统（UAV Agent System），旨在通过高层规划器生成任务计划，并由低层执行器控制无人机完成具体动作。

## 核心组件

1.  **高层规划器 (High-level Planner)**
    *   位于 `planner/` 目录。
    *   负责根据用户输入的任务指令，生成详细的执行计划。
    *   使用较重的 LLM 模型（如 qwen3:32b）进行复杂推理和规划。
    *   规划结果通常是一个包含主要目标和子目标的 JSON 结构。

2.  **低层执行器 (Low-level Actor)**
    *   位于 `agent/` 目录。
    *   负责解析高层规划器生成的计划，并控制无人机执行具体动作。
    *   使用较轻的 LLM 模型（如 ollama/qwen3:8b）进行快速响应和执行。
    *   与 AirSim 仿真环境交互，执行起飞、降落、移动、转向等操作。

3.  **语义地图器 (Semantic Mapper)**
    *   项目文档中提及，但当前代码中未实现具体功能。
    *   预期功能是将环境信息映射为图结构 JSON，为规划器提供环境信息支持。

## 主要依赖

*   **AirSim**: 用于无人机仿真环境。
*   **Ollama**: 用于运行本地 LLM 模型。
*   **smolagents**: 用于构建 LLM 驱动的代理和工具。
*   **OpenAI Python SDK**: 用于与 Ollama 提供的 LLM API 交互。

# 构建与运行

## 环境准备

1.  安装并运行 [AirSim](https://microsoft.github.io/AirSim/) 仿真环境。
2.  安装并运行 [Ollama](https://ollama.com/)，并拉取所需的模型：
    *   `qwen3:32b` (用于规划器)
    *   `qwen3:8b` (用于执行器)
    *   `qwen2.5vl:7b` (用于视觉理解，如果需要)
3.  安装 Python 依赖项 (根据代码推断，可能需要 `requirements.txt`，但当前未提供):
    *   `openai`
    *   `smolagents`
    *   `airsim`
    *   `numpy`
    *   `opencv-python`

## 运行项目

1.  确保 AirSim 和 Ollama 服务正在运行。
2.  在项目根目录下执行主程序：
    ```bash
    python main.py
    ```
3.  根据提示输入任务指令，系统将自动生成计划并控制无人机执行。

## 测试

*   项目包含一个测试文件 `test_planner_actor.py`，但具体内容未知。通常可以通过运行此文件来执行测试。

# 开发约定

*   **语言**: 主要使用 Python。
*   **架构**: 采用计划-执行架构，分离高层规划与低层执行。
*   **工具定义**: 使用 `smolagents` 的 `@tool` 装饰器定义可在执行器中调用的工具函数。
*   **LLM 集成**: 使用 `openai` Python SDK 与 Ollama 提供的 LLM 服务交互。
*   **代码结构**: 代码按功能模块划分到 `planner` 和 `agent` 目录中。