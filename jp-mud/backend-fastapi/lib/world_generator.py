from openai import OpenAI
import os
import pathlib

class WorldGenerator:
    def __init__(self):
        self.client = OpenAI()
        self.prompt_file = self._load_prompt_file()
        
    def _load_prompt_file(self):
        """Load the world generator prompt file"""
        prompt_file_name = "World-Generator-Prompt.txt"
        possible_paths = [
            # Current directory
            os.path.join(os.path.dirname(__file__), prompt_file_name),
            # Prompts directory
            os.path.join(os.path.dirname(__file__), "..", "prompts", prompt_file_name),
            # Parent directory
            os.path.join(os.path.dirname(__file__), "..", prompt_file_name),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        return f.read()
                    print(f"Loaded prompt file from: {path}")
                except Exception as e:
                    print(f"Error loading prompt file: {str(e)}")
                    return ""
        
        print(f"Warning: Could not find {prompt_file_name} file")
        return ""
    
    def generate_world(self, theme: str) -> str:
        """
        Generate a new world based on the given theme
        
        Args:
            theme: The theme for the world (e.g., cafe, office, school)
            
        Returns:
            Generated world content as a string
        """
        # Create the complete prompt by combining the base prompt with the theme
        prompt = f"""
        Using the following prompt template, generate a complete world for the theme: {theme}
        
        {self.prompt_file}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a world generator for a Japanese language learning text adventure game. Generate detailed, thematic worlds that help users learn Japanese vocabulary in context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000  # Increased token limit for detailed world generation
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating world: {str(e)}")
            # Return a basic world structure as fallback
            return f"""
## World: {theme} Theme

### Room 1: Entrance (入口/iriguchi)
A simple entrance area.
- Vocabulary:
  - ドア (doa) - door
  - 椅子 (isu) - chair
  - 机 (tsukue) - desk

[Error: Failed to generate complete world. Please try again.]
"""
