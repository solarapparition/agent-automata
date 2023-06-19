# Automata-Core

**Note**: Codebase is not functional yet.

## Introduction
Automata is an attempt at a cognitive architecture that can compose actions from simple autonomous agents into complex, goal-oriented collective behavior.

The core idea behind this architecture is that instead of having a complex central agent managing many commands and sub-agents, or a fixed set of agents with specific roles in a task loop, we modify Langchain agents to be able to call each other as tools, and then establish a hierarchical, rank-based structure to control the direction of the calls:
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

The hope with this architecture is that it allows each individual sub-agent (called an "automaton" in this system) to be predictable and reliable, while still allowing for complex, flexible behavior to emerge from the interactions between automata.

This repository contains the foundational architecture of the system.

## Installation
TBD
