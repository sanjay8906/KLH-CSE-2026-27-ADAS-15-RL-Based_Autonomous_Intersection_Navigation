# RL-Based Autonomous Intersection Navigation ADAS

[![Python](https://img.shields.io/badge/Python-3.10--3.11-3776AB.svg?style=flat-square\&logo=python\&logoColor=white)](https://www.python.org/)
[![Simulator](https://img.shields.io/badge/Simulator-MetaDrive-2F6B4F.svg?style=flat-square)](https://github.com/metadriverse/metadrive)
[![License](https://img.shields.io/github/license/sanjay8906/RL-Based_Autonomous_Intersection_Navigation_ADAS?style=flat-square)](LICENSE)
[![Contributors](https://img.shields.io/github/contributors/sanjay8906/RL-Based_Autonomous_Intersection_Navigation_ADAS?style=flat-square)](https://github.com/sanjay8906/RL-Based_Autonomous_Intersection_Navigation_ADAS/graphs/contributors)
[![Issues](https://img.shields.io/github/issues/sanjay8906/RL-Based_Autonomous_Intersection_Navigation_ADAS?style=flat-square)](https://github.com/sanjay8906/RL-Based_Autonomous_Intersection_Navigation_ADAS/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/sanjay8906/RL-Based_Autonomous_Intersection_Navigation_ADAS?style=flat-square)](https://github.com/sanjay8906/RL-Based_Autonomous_Intersection_Navigation_ADAS/pulls)
[![GitHub Stars](https://img.shields.io/github/stars/sanjay8906/RL-Based_Autonomous_Intersection_Navigation_ADAS?style=flat-square)](https://github.com/sanjay8906/RL-Based_Autonomous_Intersection_Navigation_ADAS/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/sanjay8906/RL-Based_Autonomous_Intersection_Navigation_ADAS?style=flat-square)](https://github.com/sanjay8906/RL-Based_Autonomous_Intersection_Navigation_ADAS/network/members)

> A modular research framework for reinforcement-learning-based autonomous intersection navigation and decision-making in simulated driving environments.

---

## Table of Contents

* [Overview](#overview)
* [Objectives](#objectives)
* [Key Features](#key-features)
* [System Architecture](#system-architecture)
* [Repository Structure](#repository-structure)
* [Technology Stack](#technology-stack)
* [Intersection Navigation](#intersection-navigation)
* [Reinforcement Learning Formulation](#reinforcement-learning-formulation)
* [Simulation Environment](#simulation-environment)
* [Installation](#installation)
* [Usage](#usage)
* [Development](#development)
* [Testing](#testing)
* [Evaluation](#evaluation)
* [Roadmap](#roadmap)
* [Project Status](#project-status)
* [Research Direction](#research-direction)
* [Contributing](#contributing)
* [License](#license)
* [Acknowledgements](#acknowledgements)
* [Disclaimer](#disclaimer)
* [Author](#author)

---

## Overview

**RL-Based Autonomous Intersection Navigation ADAS** is a research-oriented autonomous driving project focused on applying Reinforcement Learning (RL) to autonomous vehicle decision-making and navigation in road intersection environments.

Intersections introduce complex decision-making challenges because an autonomous vehicle must simultaneously consider its own state, surrounding traffic, road geometry, navigation objectives, and potential collision risks.

This project provides a modular simulation architecture that separates:

* Sensor interfaces
* Vehicle controllers
* Simulator integration
* Environment interaction
* Utility components
* Reinforcement learning components

The architecture is designed to support experimentation with autonomous driving policies while maintaining a clear separation between individual system components.

---

## Objectives

The primary objectives of this project are:

1. Develop a modular autonomous driving simulation framework.
2. Model intersection navigation as a sequential decision-making problem.
3. Integrate Reinforcement Learning into autonomous vehicle navigation.
4. Provide reusable sensor and controller abstractions.
5. Integrate autonomous driving scenarios using MetaDrive.
6. Support experimentation with different navigation and control strategies.
7. Evaluate autonomous vehicle behavior using safety and performance metrics.
8. Establish a foundation for future research in autonomous driving and reinforcement learning.

---

## Key Features

### Modular Architecture

The system separates major autonomous-driving components into independent modules, making the project easier to maintain, test, and extend.

### Simulator Adapter

A dedicated simulator adapter provides an interface between the autonomous-driving system and MetaDrive.

### Sensor Abstraction

Sensor components provide a structured interface for obtaining observations from the simulated environment.

### Controller Abstraction

Controllers provide a dedicated layer for converting decisions into vehicle-control actions.

### Reinforcement Learning Ready

The architecture is designed to support the development of reinforcement-learning environments, policies, training pipelines, and evaluation workflows.

### Development Tooling

The project includes development tooling for:

* Automated testing
* Code formatting
* Static type checking
* Linting
* Pre-commit validation
* Continuous integration

---

## System Architecture

The project follows a perception, state representation, decision-making, and control architecture.

```text
                         ┌─────────────────────────┐
                         │   Simulation Scenario    │
                         │                         │
                         │   Road / Traffic / Ego  │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │         Sensors         │
                         │                         │
                         │ Vehicle & Environment  │
                         │      Observations       │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │  State Representation   │
                         │                         │
                         │ Position / Velocity /   │
                         │ Lane / Traffic / Goal   │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Reinforcement Learning  │
                         │         Agent           │
                         │                         │
                         │      State → Action     │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │       Controller        │
                         │                         │
                         │ Steering / Throttle /   │
                         │         Braking         │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │        Simulator        │
                         │                         │
                         │    Vehicle Dynamics     │
                         └────────────┬────────────┘
                                      │
                                      └──────────────► Next State
```

The modular design allows individual components to be modified or replaced without requiring major changes to the rest of the system.

---

## Repository Structure

```text
RL-Based_Autonomous_Intersection_Navigation_ADAS/
│
├── .github/
│   └── workflows/
│
├── Documents/
│
├── src/
│   ├── main.py
│   ├── manual.py
│   │
│   └── adas_sim/
│       ├── controllers/
│       ├── metadrive/
│       ├── sensors/
│       ├── utils/
│       └── __init__.py
│
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
├── uv.lock
└── README.md
```

### Directory Description

| Path                        | Description                            |
| --------------------------- | -------------------------------------- |
| `src/`                      | Main application source code           |
| `src/adas_sim/`             | Core ADAS simulation package           |
| `src/adas_sim/controllers/` | Vehicle controller implementations     |
| `src/adas_sim/metadrive/`   | MetaDrive simulator integration        |
| `src/adas_sim/sensors/`     | Sensor and observation interfaces      |
| `src/adas_sim/utils/`       | Shared utility functionality           |
| `src/main.py`               | Main project entry point               |
| `src/manual.py`             | Manual vehicle-control experimentation |
| `Documents/`                | Project documentation                  |
| `.github/workflows/`        | GitHub Actions workflows               |
| `pyproject.toml`            | Python project and tool configuration  |
| `uv.lock`                   | Locked dependency configuration        |
| `.pre-commit-config.yaml`   | Pre-commit development configuration   |

---

## Technology Stack

| Technology             | Purpose                                   |
| ---------------------- | ----------------------------------------- |
| Python 3.10–3.11       | Runtime supported by MetaDrive 0.4.3      |
| Reinforcement Learning | Autonomous decision-making                |
| MetaDrive              | Autonomous driving simulation             |
| uv                     | Python package and environment management |
| pytest                 | Automated testing                         |
| Ruff                   | Linting                                   |
| Black                  | Code formatting                           |
| mypy                   | Static type checking                      |
| pre-commit             | Automated development checks              |
| Git                    | Version control                           |
| GitHub                 | Source control and collaboration          |

---

## Intersection Navigation

Intersection navigation is a challenging autonomous-driving problem because the vehicle must make decisions in an environment containing multiple interacting agents and possible paths.

Relevant information may include:

* Ego vehicle position
* Ego vehicle velocity
* Current lane
* Road geometry
* Nearby vehicles
* Relative vehicle positions
* Distance to the intersection
* Navigation target
* Traffic conditions
* Collision risk
* Vehicle acceleration and braking state

The autonomous agent must continuously observe the environment, determine an appropriate action, execute that action, and evaluate the resulting state.

---

## Reinforcement Learning Formulation

The intersection-navigation problem can be formulated as a Markov Decision Process (MDP).

```text
                         Current State
                               │
                               ▼
                    ┌────────────────────┐
                    │    RL Policy       │
                    │                    │
                    │      π(a | s)      │
                    └─────────┬──────────┘
                              │
                              ▼
                            Action
                              │
                              ▼
                    ┌────────────────────┐
                    │    Environment     │
                    └─────────┬──────────┘
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
           Next State                   Reward
```

### State

The state representation may contain information such as:

* Ego vehicle state
* Surrounding traffic state
* Lane information
* Relative distances
* Road geometry
* Navigation target
* Intersection state

### Action

The action space may contain vehicle control commands such as:

* Steering
* Acceleration
* Braking
* Velocity control

### Reward

The reward function should encourage successful navigation while penalizing unsafe or inefficient behavior.

A conceptual formulation is:

```text
Reward =
    Navigation Progress
  + Task Completion
  - Collision Risk
  - Unsafe Behavior
  - Excessive Braking
  - Unnecessary Delay
```

The exact state space, action space, RL algorithm, and reward formulation will be determined by the final implementation and experimental design.

---

## Simulation Environment

The project integrates **MetaDrive** through a dedicated adapter layer.

This separation between the simulation environment and the core ADAS architecture allows the project to evolve independently of the underlying simulator.

The adapter architecture can also provide a path toward supporting additional simulation platforms in future development.

---

## Installation

### Prerequisites

Before installing the project, ensure that the following software is available:

* Python 3.10 (MetaDrive 0.4.3 requires Python below 3.12)
* Git
* uv

### Clone the Repository

```bash
git clone https://github.com/sanjay8906/RL-Based_Autonomous_Intersection_Navigation_ADAS.git
cd RL-Based_Autonomous_Intersection_Navigation_ADAS
```

### Install Dependencies

Using `uv`:

```bash
uv sync
```

This creates and manages the project's Python environment based on the project configuration and lock file.
The project dependencies include MetaDrive and the libraries used by its ADAS sensors and display.

### Activate the Environment

#### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

#### Linux / macOS

```bash
source .venv/bin/activate
```

---

## Usage

The current project entry point is:

```bash
uv run python src/main.py
```

The default app configuration uses MetaDrive's built-in multi-block road network (`--map 3`) and starts in ADAS auto mode. Focus the MetaDrive simulator window and press `M` to switch between AUTO and MANUAL. Use `W/A/S/D` or the arrow keys in MANUAL mode: `W`/up accelerates, `A`/left and `D`/right steer, and `S`/down brakes. To start directly in MANUAL mode, add `--manual`:

```bash
uv run python src/main.py --manual
```

For manual-control experimentation:

```bash
uv run python src/manual.py
```

The execution workflow may change as the reinforcement learning environment and training pipeline are developed.

---

## Development

Install development dependencies:

```bash
uv sync --dev
```

### Code Formatting

Format the source code using Black:

```bash
black .
```

### Linting

Run Ruff:

```bash
ruff check .
```

### Static Type Checking

Run mypy:

```bash
mypy src
```

### Pre-Commit

Run all configured pre-commit checks:

```bash
pre-commit run --all-files
```

---

## Testing

Run the project's test suite using:

```bash
pytest
```

For development, tests should be added alongside new functionality to maintain reliability as the project grows.

Recommended future testing areas include:

* Sensor interfaces
* Controller behavior
* Simulator adapters
* Environment transitions
* Reward calculation
* State representation
* Action execution
* RL environment compliance

---

## Evaluation

A complete autonomous intersection-navigation system should be evaluated using both safety and performance metrics.

| Metric              | Description                                              |
| ------------------- | -------------------------------------------------------- |
| Success Rate        | Percentage of successfully completed navigation episodes |
| Collision Rate      | Frequency of collisions                                  |
| Average Reward      | Mean cumulative episode reward                           |
| Episode Duration    | Number of simulation steps or time required              |
| Navigation Progress | Progress toward the target                               |
| Travel Time         | Time required to complete the scenario                   |
| Control Smoothness  | Quality of steering, acceleration, and braking           |
| Policy Stability    | Consistency across repeated experiments                  |

Future experiments should evaluate policies across multiple scenarios, traffic configurations, and random seeds.

---

## Experimental Methodology

A robust evaluation pipeline should follow a reproducible workflow:

```text
Scenario Configuration
        │
        ▼
Environment Initialization
        │
        ▼
Policy Execution
        │
        ▼
Episode Collection
        │
        ▼
Metric Calculation
        │
        ▼
Statistical Analysis
        │
        ▼
Comparison & Visualization
```

Experiments should record:

* Environment configuration
* Random seed
* Policy configuration
* Episode statistics
* Reward values
* Collision events
* Navigation success
* Execution time

This will allow different approaches to be compared consistently.

---

## Roadmap

### Architecture

* [x] Establish modular project structure
* [x] Establish simulator adapter architecture
* [x] Integrate MetaDrive
* [x] Establish sensor abstraction
* [x] Establish controller abstraction
* [ ] Improve simulator abstraction
* [ ] Expand configuration management

### Reinforcement Learning

* [ ] Define the intersection MDP
* [ ] Implement RL environment
* [ ] Define state representation
* [ ] Define action space
* [ ] Implement reward function
* [ ] Implement training pipeline
* [ ] Implement policy evaluation
* [ ] Add experiment configuration
* [ ] Add model checkpointing
* [ ] Add training visualization

### Evaluation

* [ ] Implement collision-rate evaluation
* [ ] Implement navigation success-rate evaluation
* [ ] Implement reward analysis
* [ ] Add scenario-based evaluation
* [ ] Add performance benchmarking
* [ ] Add experiment logging
* [ ] Add result visualization
* [ ] Compare multiple RL approaches

### Future Research

* [ ] Multi-agent intersection navigation
* [ ] Safe Reinforcement Learning
* [ ] Risk-aware decision-making
* [ ] Traffic-aware planning
* [ ] Adaptive behavior under dynamic traffic
* [ ] Sim-to-real experimentation

---

## Project Status

**Status: Active Development**

The project is currently under active development.

The current focus is establishing a modular autonomous-driving simulation architecture and simulator integration that can serve as the foundation for reinforcement learning experiments.

The reinforcement learning training, evaluation, and benchmarking components will be expanded as development progresses.

This repository should currently be considered a research and development prototype rather than a production autonomous-driving system.

---

## Research Direction

The project is intended to provide a foundation for research in the following areas:

* Autonomous Driving
* Advanced Driver Assistance Systems
* Reinforcement Learning
* Deep Reinforcement Learning
* Autonomous Vehicle Decision-Making
* Intelligent Transportation Systems
* Multi-Agent Systems
* Safe Reinforcement Learning
* Autonomous Vehicle Control
* Traffic-Aware Planning
* Simulation-Based Autonomous Driving

The long-term objective is to develop and evaluate autonomous navigation policies capable of operating safely and efficiently in increasingly complex intersection scenarios.

---

## Contributing

Contributions are welcome.

### Development Workflow

Create a feature branch:

```bash
git checkout -b feature/your-feature
```

Make the required changes and run the project's checks:

```bash
pytest
ruff check .
black .
mypy src
```

Commit the changes:

```bash
git add .
git commit -m "feat: add your feature"
```

Push the branch:

```bash
git push origin feature/your-feature
```

Then open a Pull Request against the main development branch.

### Contribution Guidelines

When contributing:

* Keep changes focused and modular.
* Follow the existing project structure.
* Add tests for new functionality where appropriate.
* Maintain type annotations where applicable.
* Run formatting and linting before submitting a Pull Request.
* Update documentation when introducing user-facing changes.
* Avoid committing generated files, credentials, or local environment data.

---

## Branching Strategy

The repository can use the following branch structure as development expands:

```text
main
 │
 ├── develop
 │    │
 │    ├── feature/*
 │    ├── fix/*
 │    └── experiment/*
 │
 └── release/*
```



## Acknowledgements

This project builds upon open-source technologies and research in autonomous driving, reinforcement learning, and driving simulation.

The project uses the MetaDrive simulation framework as part of its autonomous-driving experimentation environment.

---

## Disclaimer

This project is intended for research, education, and simulation purposes.

It is not intended to control real-world vehicles and should not be used as a safety-critical automotive system without appropriate validation, certification, hardware testing, and compliance with applicable automotive safety standards.

---

## Author

**Sanjay**

GitHub:
https://github.com/sanjay8906

Repository:
https://github.com/sanjay8906/RL-Based_Autonomous_Intersection_Navigation_ADAS

---

## Project Links

* Repository: https://github.com/sanjay8906/RL-Based_Autonomous_Intersection_Navigation_ADAS
* Issues: https://github.com/sanjay8906/RL-Based_Autonomous_Intersection_Navigation_ADAS/issues
* Pull Requests: https://github.com/sanjay8906/RL-Based_Autonomous_Intersection_Navigation_ADAS/pulls
* Contributors: https://github.com/sanjay8906/RL-Based_Autonomous_Intersection_Navigation_ADAS/graphs/contributors
