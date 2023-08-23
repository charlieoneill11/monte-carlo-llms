import time
from collections import Counter
from agent import LLMAgent, Agent


class PrisonersDilemmaGame:
    PAYOFF_MATRIX = {
        'C': {'C': (3, 3), 'D': (0, 5)},
        'D': {'C': (5, 0), 'D': (1, 1)}
    }

    def __init__(self, agent1, agent2, iterations):
        self.agent1 = agent1
        self.agent2 = agent2
        self.iterations = iterations

    def play_round(self):
        decision1 = self.agent1.make_decision(self.agent2.memory)
        decision2 = self.agent2.make_decision(self.agent1.memory)

        payoff1, payoff2 = self.PAYOFF_MATRIX[decision1][decision2]

        self.agent1.store_memory(decision1, decision2, payoff1)
        self.agent2.store_memory(decision2, decision1, payoff2)

        return decision1, decision2, payoff1, payoff2

    def play_game(self):
        history = []
        for i in range(self.iterations):
            decision1, decision2, payoff1, payoff2 = self.play_round()
            history.append({
                'decision1': decision1,
                'decision2': decision2,
                'payoff1': payoff1,
                'payoff2': payoff2
            })

            print(f"Round {i+1}:")
            print(f"{self.agent1.name} chose {decision1}, {self.agent2.name} chose {decision2}")
            print(f"Payoffs -> {self.agent1.name}: {payoff1}, {self.agent2.name}: {payoff2}")
            self.agent1.update_tom(history)
            self.agent2.update_tom(history)
            print(f"Theory of Mind for {self.agent1.name}: {self.agent1.tom}")
            print(f"Theory of Mind for {self.agent2.name}: {self.agent2.tom}")
            print("------")
            time.sleep(1)

        return history


class GameStatistics:
    def __init__(self, history):
        self.history = history

    def average_payoff(self):
        total_payoff1 = sum(round_data['payoff1'] for round_data in self.history)
        total_payoff2 = sum(round_data['payoff2'] for round_data in self.history)
        avg_payoff1 = total_payoff1 / len(self.history)
        avg_payoff2 = total_payoff2 / len(self.history)
        return avg_payoff1, avg_payoff2

    def most_common_decision(self):
        decisions1 = [round_data['decision1'] for round_data in self.history]
        decisions2 = [round_data['decision2'] for round_data in self.history]
        most_common1 = Counter(decisions1).most_common(1)[0][0]
        most_common2 = Counter(decisions2).most_common(1)[0][0]
        return most_common1, most_common2


class TitForTatAgent(Agent):
    def make_decision(self, opponent_memory):
        if not opponent_memory:
            return 'C'
        return opponent_memory[-1][0]


class AlwaysDefectAgent(Agent):
    def make_decision(self, opponent_memory):
        return 'D'


if __name__ == '__main__':
    # No need for AgentConfig as it's not used in the simplified LLMAgent
    agent1 = LLMAgent('Alice', 'Player 1')
    agent2 = LLMAgent('Bob', 'Player 2')

    game = PrisonersDilemmaGame(agent1, agent2, iterations=10)
    
    history = game.play_game()
    
    # Generate statistics
    stats = GameStatistics(history)
    avg_payoff1, avg_payoff2 = stats.average_payoff()
    most_common1, most_common2 = stats.most_common_decision()
    
    print(f"Average payoff for {agent1.name}: {avg_payoff1}")
    print(f"Average payoff for {agent2.name}: {avg_payoff2}")
    print(f"Most common decision for {agent1.name}: {most_common1}")
    print(f"Most common decision for {agent2.name}: {most_common2}")