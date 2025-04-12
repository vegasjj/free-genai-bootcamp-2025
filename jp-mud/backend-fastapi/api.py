from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
from datetime import datetime, timedelta
import uuid
import json

# Import our modules
from lib.session_manager import SessionManager, GameState, GameSession
from lib.game import Game
from lib.adventure_text import AdventureText
from lib.world_generator import WorldGenerator

# Initialize FastAPI
app = FastAPI(title="MUD Adventure API")

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory to store session files
SESSIONS_DIR = os.path.join(os.path.dirname(__file__), "data", "sessions")
WORLDS_DIR = os.path.join(os.path.dirname(__file__), "data", "worlds")

# Ensure the directories exist
os.makedirs(SESSIONS_DIR, exist_ok=True)
os.makedirs(WORLDS_DIR, exist_ok=True)

# Function to get the file path for a session
def get_session_file_path(session_id):
    return os.path.join(SESSIONS_DIR, f"{session_id}.json")

# Function to get the file path for a world
def get_world_file_path(session_id):
    return os.path.join(WORLDS_DIR, f"{session_id}.txt")

# Data models
class NewGameRequest(BaseModel):
    theme: str

class MessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    theme: Optional[str] = None

class MessageResponse(BaseModel):
    session_id: str
    message: str
    game_state: Optional[GameState] = None

# Initialize the session manager
session_manager = SessionManager(SESSIONS_DIR)
# Initialize the world generator
world_generator = WorldGenerator()

# Helper function to get a game instance
def get_game(session_id, theme, world_content):
    return Game(session_manager, session_id, theme, world_content)

@app.post("/api/game/new")
async def new_game(request: NewGameRequest):
    # Generate a new session ID if none provided
    session_id = str(uuid.uuid4())

    # Clean up old session if it exists
    session_manager.delete_session(session_id)
    # Clean up old world if it exists
    world_file_path = get_world_file_path(session_id)
    if os.path.exists(world_file_path):
        os.remove(world_file_path)
    print(f"Deleted session {session_id}")

    # Generate new world content
    world_content = world_generator.generate_world(request.theme)
    
    # Save the world content
    world_file_path = get_world_file_path(session_id)
    with open(world_file_path, 'w', encoding='utf-8') as f:
        f.write(world_content)
    
    # Create new game with the generated world
    game = get_game(session_id, request.theme, world_content)
    initial_message = game.process_command("look around")
    
    return {
        "session_id": game.session_id,
        "message": initial_message,
        "game_state": game.state
    }

@app.post("/api/game/message")
async def process_message(request: MessageRequest):
    # Load the world content if it exists
    world_content = None
    if request.session_id:
        world_file_path = get_world_file_path(request.session_id)
        if os.path.exists(world_file_path):
            with open(world_file_path, 'r', encoding='utf-8') as f:
                world_content = f.read()
    
    game = get_game(request.session_id, request.theme, world_content)
    response = game.process_command(request.message)
    return MessageResponse(
        session_id=game.session_id,
        message=response,
        game_state=game.state
    )

@app.get("/api/game/load/{session_id}")
async def load_game(session_id: str):
    session = session_manager.get_session(session_id)
    if session:
        # Load the world content if it exists
        world_content = None
        world_file_path = get_world_file_path(session_id)
        if os.path.exists(world_file_path):
            with open(world_file_path, 'r', encoding='utf-8') as f:
                world_content = f.read()
        
        game = get_game(session_id, session.state.theme, world_content)
        return {
            "success": True,
            "message": f"Game session {session_id} loaded successfully",
            "session_id": game.session_id,
            "game_state": game.state,
            "history": game.history
        }
    else:
        return {
            "success": False,
            "message": f"Game session {session_id} not found"
        }

@app.get("/api/game/sessions")
async def list_sessions():
    sessions = session_manager.list_sessions()
    session_info = []
    
    for session_id in sessions:
        session = session_manager.get_session(session_id)
        if session:
            session_info.append({
                "id": session_id,
                "theme": session.state.theme,
                "created_at": session.created_at.isoformat() if hasattr(session, 'created_at') else None,
                "last_active": session.last_active.isoformat() if hasattr(session, 'last_active') else None
            })
    
    return {"sessions": session_info}

@app.post("/api/game/cleanup")
async def cleanup_sessions(days: int = 7):
    """Manually trigger cleanup of old sessions"""
    if days < 1:
        return {
            "success": False,
            "message": "Days parameter must be at least 1"
        }
    
    initial_count = len(session_manager.sessions)
    removed_count = session_manager.cleanup_old_sessions(max_age_days=days)
    final_count = len(session_manager.sessions)
    return {
        "success": True,
        "message": f"Cleaned up sessions older than {days} days",
        "removed_count": removed_count,
        "remaining_count": final_count
    }

# Run the server with: uvicorn api:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)