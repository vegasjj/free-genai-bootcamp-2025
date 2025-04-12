# Japanese Language Learning MUD

A text-based adventure game for learning Japanese vocabulary, implemented with FastAPI backend and React frontend.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Backend

### Option 1: Using the FastAPI server
```bash
python run_api.py
```
This will start the FastAPI server on http://localhost:8000

### Option 2: Using the Gradio interface (legacy)
```bash
python game.py
```
This will start the Gradio interface on http://localhost:7860

## API Endpoints

The FastAPI backend provides the following endpoints:

- `GET /` - Welcome message
- `POST /api/game/new` - Start a new game session or reset an existing one
- `POST /api/game/message` - Send a message to the game (creates a new session if none provided)
- `GET /api/game/load/{session_id}` - Load an existing game session
- `GET /api/game/sessions` - List all active game sessions (for debugging)
- `POST /api/game/cleanup` - Clean up old game sessions (for maintenance)

Note: Game state is automatically saved to a JSON file after each message, providing persistence across server restarts. The system also automatically cleans up sessions older than 7 days when the server starts.


### How to run backend

```sh
uvicorn api:app --reload
```

## How to Play

The game is set in a Japanese cafe where you can:
- Move between rooms using `move [direction]`
- Look at objects using `look [object]` or `見ます [object]`
- Talk to NPCs using `talk [npc]` or `話します [npc]`

Your goal is to learn all 30 vocabulary words by interacting with objects and talking to NPCs throughout the cafe.

### Example Commands:
- `move north` - Move to the next room
- `look ドア` - Look at the door
- `talk 田中さん` - Talk to Tanaka-san

The game tracks your progress in learning vocabulary words. Try to master all 30 words!
