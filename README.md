# Advanced Language Model-Based Negotiation Using Monte Carlo Tree Search and Theory of Mind

## Introduction
This repository houses code and resources for an advanced negotiation framework integrating Monte Carlo Tree Search (MCTS) and a "theory of mind" into language models. The goal is to elevate the negotiation capabilities of these models by introducing "Type II" strategic reasoning, along with a continually updated understanding of the opponent.

## Objectives

* Implement MCTS in language models for improved decision-making in negotiations.
* Incorporate a "theory of mind" that each model updates after every interaction.
* Evaluate the system against a variety of benchmarks, opponents, and real-world scenarios.

## Methodology

### State Space and Action Space

```state_space.py```
Defines the state of the game, incorporating both the text of the conversation and additional metadata like the current proposals, accepted terms, etc.

```action_space.py```
Categorises possible actions into types such as "make offer," "reject offer," etc., and restricts allowable text for each type.

### Monte Carlo Tree Search

```mcts.py```
Contains the core MCTS algorithm, including:
* Selection: UCT-based tree traversal
* Expansion: New negotiation moves proposed by the language model
* Simulation: Forward rollouts using a simplified model
* Backpropagation: Node updates based on simulation outcomes

### Theory of Mind

```theory_of_mind.py```

Implements the "theory of mind" using a continually updated "memory document":

* Initialization: Begins with some pre-defined assumptions about the opponent.
* Update Function: Alters the document based on observed moves and outcomes.
* Usage: Used as an additional input for each MCTS iteration, influencing the language model's choices.


### Types of Games

* `prisoners_dilemma.py`: Implementing the Prisoner's Dilemma game.
* `ultimatum_game.py`: Implementing the Ultimatum Game.
* `market_bargaining.py`: Implementing Market Bargaining simulations.
* `diplomacy_game.py`: Implementing a Diplomacy multi-agent game.

### How to Run

Example for running the Prisoner's Dilemma game:

```bash
python run_game.py --game prisoners_dilemma --iterations 100
```

## Evaluation Plan

* Phase 1: Intra-model evaluation (check evaluations/intra_model_eval.py)
* Phase 2: Comparative evaluation against standard LMs (evaluations/comparative_eval.py)
* Phase 3: Human evaluation (evaluations/human_eval.py)
* Phase 4: Multi-agent evaluations (evaluations/multi_agent_eval.py)
