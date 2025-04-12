// API base URL - update this to match your backend server
const API_BASE_URL = 'http://localhost:8000/api';

// Store the current session ID in memory
let currentSessionId: string | null = null;

export interface GameState {
  room: string;
  inventory: string[];
  health: number;
  [key: string]: any;
}

export interface GameResponse {
  message: string;
  session_id?: string;
  game_state?: GameState;
  success?: boolean;
  error?: string;
}

/**
 * Send a message to the game
 */
export const sendMessage = async (message: string, theme: string = "cafe"): Promise<GameResponse> => {
  try {
    if (!currentSessionId) {
      return {
        success: false,
        error: 'No active session',
        message: 'You need to start a new game first.',
      };
    }

    const response = await fetch(`${API_BASE_URL}/game/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: currentSessionId,
        theme,
      }),
    });

    const data = await response.json();
    
    // Store the session ID for future requests
    if (data.session_id) {
      currentSessionId = data.session_id;
    }

    return data;
  } catch (error) {
    console.error('Error sending message:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : String(error),
      message: 'Failed to send message. Please try again.',
    };
  }
};

/**
 * Start a new game session
 */
export const newGame = async (theme: string = "cafe"): Promise<GameResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/game/new`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        theme,
      }),
    });
    
    const data = await response.json();
    
    // Store the session ID for future requests
    if (data.session_id) {
      currentSessionId = data.session_id;
    }
    
    return data;
  } catch (error) {
    console.error('Error starting new game:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : String(error),
      message: 'Failed to start a new game. Please try again.',
    };
  }
};

/**
 * Load an existing game session
 */
export const loadGame = async (sessionId: string): Promise<GameResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/game/load/${sessionId}`);
    
    const data = await response.json();
    
    // Store the session ID for future requests
    if (data.session_id) {
      currentSessionId = data.session_id;
    }
    
    return data;
  } catch (error) {
    console.error('Error loading game:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : String(error),
      message: 'Failed to load game. Please try again.',
    };
  }
};

/**
 * List all available game sessions
 * @returns Promise with the list of session IDs
 */
export const listSessions = async (): Promise<string[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/game/sessions`);

    if (!response.ok) {
      throw new Error(`Server responded with status: ${response.status}`);
    }

    const data = await response.json();
    return data.sessions;
  } catch (error) {
    console.error('Error listing game sessions:', error);
    throw error;
  }
};

/**
 * Get the current session ID
 */
export const getCurrentSessionId = (): string | null => {
  return currentSessionId;
};
