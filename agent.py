import os
import openai
import random
import json
import yaml

# Initialize OpenAI API
config = yaml.safe_load(open("config.yaml"))
openai.api_type = "azure"
openai.api_base = "https://utbd.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = config["api_key"]

class Agent:
    def __init__(self, name):
        self.name = name
        self.memory = []

    def make_decision(self, opponent_memory):
        raise NotImplementedError("This method should be overridden by subclass")

    def store_memory(self, decision, opponent_decision, payoff):
        self.memory.append((decision, opponent_decision, payoff))

    def retrieve_memory(self):
        return self.memory

class LanguageModelInterface:
    def __init__(self, game_type, history):
        self.game_type = game_type
        self.history = history

    def get_decision(self, game_type, history):
        prompt = self.decision_prompt(self.history)
        response = openai.ChatCompletion.create(
            engine="gpt4_large",
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.7,
            max_tokens=150,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
        )
        # Assume 'C' or 'D' is part of the response
        choice = response.choices[0].message.content.strip()
        return self.extract_response(choice)
    
    def extract_response(self, choice: str):
        if choice[-1] == '.' or choice[-1] == "'": return choice[-2]
        else: return choice[-1]
    
    def decision_prompt(self, history):
        game_options = self.game_moves()
        DECISION_PROMPT = f"""
                        {self.game_type_prompt()}. You have the choice of either 'C' (cooperate) or 'D' (defect).
                        
                        {self.game_history_prompt(history)}.

                        Based on your understanding of your opponent and yourself, what is the best possible next move to maximise your utility?
                        Think step-by-step to predict what you would do, what your opponent would do, and what the outcome would be.
                        Then, with a blank line in between, return the best possible next move e.g. C or D, and only C or D, nothing else.
                        """
        return DECISION_PROMPT
        
    def game_type_prompt(self):
        GAME_PROMPT = f"""You are playing the following game:
                          {self.game_type}."""
        if self.game_type == 'PrisonersDilemma': 
            path = 'prompt_templates/prisoners_dilemma.txt'
            with open(path, 'r') as f: 
                GAME_PROMPT += f.read()
        return GAME_PROMPT
    
    def game_history_prompt(self, history):
        GAME_HISTORY_PROMPT = f"""The history of the game is as follows (tuples of (decision, opponent decision, payoff)):
                                  {history}."""
        return GAME_HISTORY_PROMPT
    
    def game_moves(self):
        if self.game_type == 'PrisonersDilemma': return {'Cooperate': 'C', 'Defect': 'D'}

    def converse(self, agent1_tom, agent2_tom, game_type):
        # Simulate a conversation between two agents and return the conversation
        return "Conversation"

class LLMAgent(Agent):
    def __init__(self, name):
        super().__init__(name)
        self.language_model = LanguageModelInterface("PrisonersDilemma", self.retrieve_memory())

    def make_decision(self, opponent_memory):
        game_type = "PrisonersDilemma"
        decision = self.language_model.get_decision(game_type, json.dumps(self.retrieve_memory()))
        return decision
    
if __name__ == "__main__":
    agent1 = LLMAgent("Agent1")
    agent2 = LLMAgent("Agent2")

    for i in range(5):  # Play for 5 rounds
        agent1_decision = agent1.make_decision(agent2.retrieve_memory())
        agent2_decision = agent2.make_decision(agent1.retrieve_memory())

        # Store decisions and payoffs (payoff logic not implemented)
        agent1.store_memory(agent1_decision, agent2_decision, None)
        agent2.store_memory(agent2_decision, agent1_decision, None)
        
        print(f"Round {i+1}: Agent1 chose {agent1_decision}, Agent2 chose {agent2_decision}")