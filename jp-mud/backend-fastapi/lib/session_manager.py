import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pydantic import BaseModel

# Define the data models
class GameState(BaseModel):
    room: str
    inventory: List[str] = []
    visited_rooms: List[str] = []
    npc_interactions: Dict[str, int] = {}
    vocabulary: Dict[str, bool] = {}
    conversation_vocabulary: Dict[str, bool] = {}
    score: int = 0
    theme: str = "cafe"
    
class GameSession(BaseModel):
    id: str
    state: GameState
    history: List[Dict[str, str]] = []
    created_at: datetime = datetime.now()
    last_active: datetime = datetime.now()

class SessionManager:
    """Manages game sessions with file-based storage"""
    
    def __init__(self, sessions_dir: str):
        """
        Initialize the session manager
        
        Args:
            sessions_dir: Directory to store session files
        """
        self.sessions_dir = sessions_dir
        # Ensure the sessions directory exists
        os.makedirs(self.sessions_dir, exist_ok=True)
        # Dictionary to store active sessions
        self.sessions: Dict[str, GameSession] = {}
        # Load existing sessions
        self.load_sessions()
    
    def get_session_file_path(self, session_id: str) -> str:
        """Get the file path for a session"""
        return os.path.join(self.sessions_dir, f"{session_id}.json")
    
    def load_sessions(self) -> Dict[str, GameSession]:
        """Load all sessions from files"""
        try:
            # List all session files in the directory
            if os.path.exists(self.sessions_dir):
                for filename in os.listdir(self.sessions_dir):
                    if filename.endswith('.json'):
                        session_id = filename[:-5]  # Remove .json extension
                        self.load_session(session_id)
            
            print(f"Loaded {len(self.sessions)} sessions from {self.sessions_dir}")
            return self.sessions
        except Exception as e:
            print(f"Error loading sessions: {e}")
            return {}
    
    def load_session(self, session_id: str) -> Optional[GameSession]:
        """Load a specific session from file"""
        try:
            session_path = self.get_session_file_path(session_id)
            
            if not os.path.exists(session_path):
                return None
                
            with open(session_path, 'r') as f:
                session_data = json.load(f)
                
                state_data = session_data.get('state', {})
                state = GameState(
                    room=state_data.get('room', 'entrance'),
                    inventory=state_data.get('inventory', []),
                    visited_rooms=state_data.get('visited_rooms', []),
                    npc_interactions=state_data.get('npc_interactions', {}),
                    vocabulary=state_data.get('vocabulary', {}),
                    conversation_vocabulary=state_data.get('conversation_vocabulary', {}),
                    score=state_data.get('score', 0),
                    theme=state_data.get('theme', "cafe")
                )
                
                session = GameSession(
                    id=session_id,
                    state=state,
                    history=session_data.get('history', []),
                    created_at=datetime.fromisoformat(session_data.get('created_at', datetime.now().isoformat())),
                    last_active=datetime.fromisoformat(session_data.get('last_active', datetime.now().isoformat()))
                )
                
                # Store in memory
                self.sessions[session_id] = session
                return session
                
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None
    
    def save_session(self, session_id: str, session: GameSession) -> bool:
        """Save a session to file"""
        try:
            # Convert session to a serializable format
            session_data = {
                'id': session.id,
                'state': {
                    'room': session.state.room,
                    'inventory': session.state.inventory,
                    'visited_rooms': session.state.visited_rooms,
                    'npc_interactions': session.state.npc_interactions,
                    'vocabulary': session.state.vocabulary,
                    'conversation_vocabulary': session.state.conversation_vocabulary,
                    'score': session.state.score,
                    'theme': session.state.theme
                },
                'history': session.history,
                'created_at': session.created_at,
                'updated_at': session.updated_at
            }
            
            # Save to individual file
            file_path = self.get_session_file_path(session_id)
            with open(file_path, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            # Store in memory
            self.sessions[session_id] = session
            return True
                
        except Exception as e:
            print(f"Error saving session {session_id}: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and its file"""
        try:
            # Remove from memory
            if session_id in self.sessions:
                del self.sessions[session_id]
            
            # Remove file
            file_path = self.get_session_file_path(session_id)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted session file: {file_path}")
            
            return True
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[GameSession]:
        """Get a session by ID, loading from file if necessary"""
        if session_id in self.sessions:
            return self.sessions[session_id]
        
        # Try to load from file
        return self.load_session(session_id)
    
    def create_session(self, session_id: Optional[str] = None, initial_state: Optional[GameState] = None) -> GameSession:
        """Create a new session"""
        # Use provided ID or generate a new one
        session_id = session_id or str(uuid.uuid4())
        
        # Use provided state or create default
        if initial_state is None:
            initial_state = GameState(
                room="entrance",
                inventory=[],
                visited_rooms=["entrance"],
                npc_interactions={},
                vocabulary={},
                conversation_vocabulary={},
                score=0,
                theme="cafe"
            )
        
        # Create session
        now = datetime.now().isoformat()
        session = GameSession(
            id=session_id,
            state=initial_state,
            history=[],
            created_at=now,
            updated_at=now
        )
        
        # Save to file
        self.save_session(session_id, session)
        
        return session
    
    def update_session(self, session_id: str, state: Optional[GameState] = None, 
                      history_entry: Optional[Dict[str, str]] = None) -> Optional[GameSession]:
        """Update a session with new state and/or history entry"""
        session = self.get_session(session_id)
        
        if not session:
            return None
        
        # Update state if provided
        if state:
            session.state = state
        
        # Add history entry if provided
        if history_entry:
            session.history.append(history_entry)
        
        # Update timestamp
        session.updated_at = datetime.now().isoformat()
        
        # Save to file
        self.save_session(session_id, session)
        
        return session
    
    def cleanup_old_sessions(self, max_age_days: int = 7) -> int:
        """Remove sessions older than max_age_days days"""
        try:
            now = datetime.now()
            sessions_to_remove = []
            
            for session_id, session in self.sessions.items():
                # Parse the updated_at timestamp
                try:
                    last_updated = datetime.fromisoformat(session.updated_at)
                    age = now - last_updated
                    
                    # If session is older than max_age_days, mark for removal
                    if age > timedelta(days=max_age_days):
                        sessions_to_remove.append(session_id)
                except Exception as e:
                    print(f"Error parsing timestamp for session {session_id}: {e}")
            
            # Remove old sessions
            for session_id in sessions_to_remove:
                self.delete_session(session_id)
            
            if sessions_to_remove:
                print(f"Removed {len(sessions_to_remove)} old sessions")
            
            return len(sessions_to_remove)
        except Exception as e:
            print(f"Error cleaning up old sessions: {e}")
            return 0
    
    def list_sessions(self) -> List[str]:
        """List all session IDs"""
        return list(self.sessions.keys())


# Import at the end to avoid circular imports
import uuid
