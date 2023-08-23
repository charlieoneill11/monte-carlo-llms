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
    def __init__(self, name, role):
        self.name = name
        self.role = role
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

    def get_decision(self, tom):
        prompt = self.decision_prompt(tom)
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
    
    def decision_prompt(self, tom):
        DECISION_PROMPT = f"""
                        {self.game_type_prompt()}. You have the choice of either 'C' (cooperate) or 'D' (defect).

                        Here is what you think of yourself: {tom['self']}
                        Here is what you think of your opponent: {tom['opponent']}

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

    def tom_update_prompt(self, history, tom: dict, role: str, self_tom: bool = False):
        if role == "Player 1":
            player_history = [{key: round_data[key] for key in ('decision1', 'payoff1')} for round_data in history]
        else:
            player_history = [{key: round_data[key] for key in ('decision2', 'payoff2')} for round_data in history]
        if not self_tom: 
            TOM_UPDATE_PROMPT = f"""
                                You are playing the Prisoner's Dilemma game. Before this round, this is what you thought of your opponent:
                                {tom['opponent']}
                                
                                After this, here's the move your opponent just did. It's a tuple of (decision, payoff):
                                {player_history[-1]}.

                                Based on this new move, rewrite your judgement of your opponent's character. Analyse what type of player they are.
                                Be specific and detailed, providing as much information as possible for someone trying to defeat them in this game.
                                In particular, be descriptive about all their past moves.
                                Focus on whether the most recent move reinforces or challenges your previous view of them.
                                """
        else:
            TOM_UPDATE_PROMPT = f"""
                                You are playing the Prisoner's Dilemma game. Before this round, this is what you thought of yourself:
                                {tom['self']}
                                
                                After this, here's the move you just did. It's a tuple of (decision, payoff):
                                {player_history[-1]}.

                                Based on this new move, rewrite your judgement of your character. Analyse what type of player you are.
                                Be specific and detailed, providing as much information as possible in order to perceive yourself.
                                In particular, be descriptive about all your past moves.
                                Focus on whether the most recent move reinforces or challenges your previous view of yourself.
                                """
        return TOM_UPDATE_PROMPT

    def converse(self, agent1_tom, agent2_tom, game_type):
        # Simulate a conversation between two agents and return the conversation
        return "Conversation"

class LLMAgent(Agent):
    def __init__(self, name, role):
        super().__init__(name, role)
        self.language_model = LanguageModelInterface("PrisonersDilemma", self.retrieve_memory())
        self.tom = {"self": "I'm just starting this game I'm trying to win.", "opponent": "I know nothing about my opponent yet."}

    def make_decision(self, opponent_memory):
        game_type = "PrisonersDilemma"
        decision = self.language_model.get_decision(self.tom)
        return decision
    
    def update_tom(self, history):
        # Update opponent
        prompt = self.language_model.tom_update_prompt(history, tom=self.tom, role=self.role)
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
        judgment = response.choices[0].message.content.strip()
        self.tom['opponent'] = judgment

        # Update ourselves
        prompt = self.language_model.tom_update_prompt(history, role = self.role, tom=self.tom, self_tom=True)
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
        judgment = response.choices[0].message.content.strip()
        self.tom['self'] = judgment