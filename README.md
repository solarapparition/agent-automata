# Agent Automata

## Introduction
`agent-automata` is a lightweight orchestration architecture for a hierarchical group of modular, autonomous agents, with the goal of composing actions from simple autonomous agents into complex collective behavior.

The core idea behind this architecture is that instead of having a complex central agent managing many commands and sub-agents, or a fixed set of agents with specific roles in a task loop, we allow agents to call each other as tools, and then establish a hierarchical, rank-based structure to control the direction of the calls:
```
Agent A (Rank 3):
  - Agent B (Rank 2)
    - Tool 1
    - Tool 2
  - Agent C (Rank 2)
    - Tool 1
    - Tool 3
    - Agent D (Rank 1)
      - Tool 4
      - Tool 5
      - Tool 6
```
Agent A can then potentially be included as a callable sub-agent by another agent of higher rank, and so on.

## Installation
Run `pip install agent-automata` for the core package.
You can also run `pip install agent-automata[builtins]` to install some additional built-in functionality.

## Usage/Demo
There is very little concrete functionality included in the package--this is meant to be one component in a larger, more usable system of agents. The `demo` directory shows a rather trivial example of specifying a simple agent and its sub-agents/tools using yaml spec files.

To run the demo:
1. Install the package with the `[builtins]` option.
2. Download the `demo` directory (you can download the zip and extract just the `demo` directory).
3. `cd` to the `demo` directory.
4. Run `python run_demo.py`.
5. You should see some output from the demo agent, which creates a quiz and saves it to a file in a workspace.

If you find this architecture interesting and would like more documentation on how it works, please post an issue.
