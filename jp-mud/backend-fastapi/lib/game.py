import uuid
from datetime import datetime
from typing import Dict, List, Optional

from lib.adventure_text import AdventureText
from lib.session_manager import SessionManager, GameState, GameSession

class Game:
    """Game logic class that interacts with the session manager"""
    
    def __init__(self, session_manager: SessionManager, session_id: Optional[str] = None, theme: str = "cafe", world_content: Optional[str] = None):
        """
        Initialize a new game or load an existing one
        
        Args:
            session_manager: Session manager instance to handle persistence
            session_id: Optional ID of an existing session to load
            theme: Game theme/setting (default: cafe)
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.session_manager = session_manager
        
        # Check if session exists
        session = None
        if session_id:
            session = session_manager.get_session(session_id)
            
        if session:
            # Load existing session
            self.state = session.state
            self.history = session.history
            self.created_at = session.created_at
            self.updated_at = session.updated_at
            # Create adventure text with the theme from the saved state
            self.adventure_text = AdventureText(theme=self.state.theme, world_content=world_content)
        else:
            # Create new session with the specified theme
            self.state = GameState(
                room="entrance",
                inventory=[],
                visited_rooms=["entrance"],
                npc_interactions={},
                vocabulary={},
                conversation_vocabulary={},
                score=0,
                theme=theme
            )
            self.history = []
            self.created_at = datetime.now().isoformat()
            self.updated_at = self.created_at
            # Create adventure text with the specified theme and world content
            self.adventure_text = AdventureText(theme=theme, world_content=world_content)
            
            # Save new session
            session = GameSession(
                id=self.session_id,
                state=self.state,
                history=self.history,
                created_at=self.created_at,
                updated_at=self.updated_at
            )
            self.session_manager.save_session(self.session_id, session)

    def process_command(self, command: str) -> str:
        """
        Process a command and return the response
        
        Args:
            command: User command to process
            
        Returns:
            Text response to the command
        """
        # Update the game state based on the command
        response = self.adventure_text.process_command(command, self.state)
        
        # Update the history
        self.history.append({
            "command": command,
            "response": response
        })
        
        # Update the timestamp
        self.updated_at = datetime.now().isoformat()
        
        # Save the updated session
        session = GameSession(
            id=self.session_id,
            state=self.state,
            history=self.history,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
        self.session_manager.save_session(self.session_id, session)
        
        return response
