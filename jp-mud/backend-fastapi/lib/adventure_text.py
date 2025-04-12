from openai import OpenAI
from dotenv import load_dotenv
import os
import pathlib
import re

# Load environment variables from .env file
load_dotenv()

class AdventureText:
    def __init__(self, theme="cafe", world_content: str = None):
        self.client = OpenAI()
        self.theme = theme
        
        # Use provided world content or load from file
        if world_content is None:
            world_content = self._load_world_file(theme)
        
        self.context = f"""
        You are a Japanese language learning text adventure game.
        Generate engaging responses that teach Japanese vocabulary naturally.
        Keep responses concise and focused on the current action.
        Always include relevant Japanese vocabulary with format: 日本語 (romaji / english)
        
        World information:
        {world_content}
        """
    
    def _load_world_file(self, theme):
        """Try to load the world file based on theme"""
        world_file_name = f"{theme}-world.txt"
        possible_paths = [
            # Current directory
            world_file_name,
            # Worlds directory
            f"worlds/{world_file_name}",
            # Examples directory
            f"examples/{world_file_name}",
            # Parent directory
            f"../worlds/{world_file_name}",
            # Parent examples directory
            f"../examples/{world_file_name}",
            # Absolute path
            f"/mnt/c/Users/andre/Sites/omenking/free-genai-bootcamp-2025/jp-mud/examples/{world_file_name}"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        return f.read()
                    print(f"Loaded world file from: {path}")
                except Exception as e:
                    print(f"Error loading world file: {str(e)}")
                    return ""
        
        # Try to find it relative to the current file
        current_dir = pathlib.Path(__file__).parent.absolute()
        project_root = current_dir.parent.parent
        
        additional_paths = [
            project_root / "worlds" / world_file_name,
            project_root / "examples" / world_file_name,
        ]
        
        for path in additional_paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        return f.read()
                    print(f"Loaded world file from: {path}")
                except Exception as e:
                    print(f"Error loading world file: {str(e)}")
                    return ""
        
        print(f"Warning: Could not find {world_file_name} file")
        return ""
    
    def generate_text(self, prompt: str) -> str:
        """Generate text based on a prompt using OpenAI LLMs"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.context},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"
            
    def process_command(self, command: str, game_state) -> str:
        """
        Process a user command and generate a response based on the game state
        
        Args:
            command: The user's command
            game_state: The current game state
            
        Returns:
            Text response to the command
        """
        # Create a prompt that includes the game state and command
        room = game_state.room
        inventory = game_state.inventory
        visited_rooms = game_state.visited_rooms
        vocabulary = game_state.vocabulary
        conversation_vocabulary = game_state.conversation_vocabulary
        score = game_state.score
        theme = game_state.theme
        
        # Calculate mastery progress
        total_words = 30  # 20 object words + 10 conversation words
        mastered_words = sum(1 for v in vocabulary.values() if v) + sum(1 for v in conversation_vocabulary.values() if v)
        progress_percentage = (mastered_words / total_words) * 100 if total_words > 0 else 0
        
        prompt = f"""
        Current room: {room}
        Inventory: {', '.join(inventory) if inventory else 'empty'}
        Visited rooms: {', '.join(visited_rooms)}
        Theme: {theme}
        Score: {score}
        Vocabulary mastered: {mastered_words}/{total_words} ({progress_percentage:.1f}%)
        
        The player has entered the command: "{command}"
        
        Respond to this command in the context of a Japanese language learning text adventure.
        If the player successfully uses a Japanese vocabulary word correctly, mark it as learned.
        
        When a player learns a new vocabulary word:
        1. Add it to their vocabulary list
        2. Increase their score
        3. Mention in your response that they've learned a new word
        
        Current vocabulary mastered: {', '.join(k for k, v in vocabulary.items() if v)}
        Current conversation vocabulary mastered: {', '.join(k for k, v in conversation_vocabulary.items() if v)}
        """
        
        # Generate the response
        response = self.generate_text(prompt)
        
        # Check if new vocabulary was learned (this would be indicated in the response)
        # This is a simple implementation - in a real game, you'd want more sophisticated parsing
        if "learned a new word" in response.lower():
            # Extract the word (this is a simplified example)
            # In a real implementation, you'd parse the response more carefully
            # to identify exactly which word was learned
            
            # For demonstration purposes, we'll assume any Japanese characters in parentheses
            # represent a newly learned word
            japanese_word_match = re.search(r'([ぁ-んァ-ン一-龥]+)\s*\(', response)
            if japanese_word_match:
                new_word = japanese_word_match.group(1)
                
                # Check if it's an object vocabulary or conversation vocabulary
                # This is simplified - in a real game, you'd have a more robust way to determine this
                if "talk" in command.lower() or "話します" in command:
                    if new_word not in game_state.conversation_vocabulary:
                        game_state.conversation_vocabulary[new_word] = True
                        game_state.score += 10  # More points for conversation vocabulary
                else:
                    if new_word not in game_state.vocabulary:
                        game_state.vocabulary[new_word] = True
                        game_state.score += 5  # Points for object vocabulary
        
        # Generate and return the response
        return response