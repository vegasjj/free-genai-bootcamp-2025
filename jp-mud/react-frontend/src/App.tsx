import { useState, useEffect } from 'react';
import { ChatWindow } from './components/ChatWindow';
import { ChatInput } from './components/ChatInput';
import * as api from './services/api';

interface Message {
  content: string;
  sender: 'user' | 'bot';
}

interface SavedSession {
  id: string;
  theme: string;
  createdAt: string;
}

export function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | undefined>()
  const [theme, setTheme] = useState<string>("cafe")
  const [gameStarted, setGameStarted] = useState(false)
  const [savedSessions, setSavedSessions] = useState<SavedSession[]>([])
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode')
    return saved ? JSON.parse(saved) : false
  })

  // Available themes
  const themes = [
    { id: 'cafe', name: 'Cafe' },
    { id: 'office', name: 'Office' },
    { id: 'school', name: 'School' },
    { id: 'hospital', name: 'Hospital' },
    { id: 'gym', name: 'Gym' },
    { id: 'postoffice', name: 'Post Office' },
    { id: 'hardware', name: 'Hardware Store' },
    { id: 'church', name: 'Church' },
    { id: 'bakery', name: 'Bakery' },
    { id: 'library', name: 'Library' },
    { id: 'arcade', name: 'Arcade' },
    { id: 'tech-conference', name: 'GenAI Tech Conference' },
    { id: 'chatroom', name: 'Internet Chatroom' }
  ];

  // Load saved sessions when component mounts
  useEffect(() => {
    loadSavedSessions();
  }, []);

  // Start a new game when component mounts and game is started
  useEffect(() => {
    if (gameStarted) {
      startNewGame();
    }
  }, [gameStarted]);

  const loadSavedSessions = async () => {
    try {
      const sessions = await api.listSessions();
      const savedSessionsData = await Promise.all(
        sessions.map(async (sessionId) => {
          const gameData = await api.loadGame(sessionId);
          return {
            id: sessionId,
            theme: gameData.game_state?.theme || 'unknown',
            createdAt: new Date(gameData.game_state?.created_at || Date.now()).toLocaleString(),
          };
        })
      );
      setSavedSessions(savedSessionsData);
    } catch (err) {
      console.error('Error loading saved sessions:', err);
    }
  };

  const loadGame = async (sessionId: string) => {
    setIsLoading(true);
    setError(undefined);
    
    try {
      const response = await api.loadGame(sessionId);
      setMessages([
        {
          content: `Welcome back to your ${response.game_state?.theme} adventure!\n${response.message}`,
          sender: 'bot'
        }
      ]);
      setTheme(response.game_state?.theme || theme);
      setGameStarted(true);
    } catch (err) {
      setError('Error loading game: ' + (err instanceof Error ? err.message : String(err)));
    } finally {
      setIsLoading(false);
    }
  };

  const startNewGame = async () => {
    setIsLoading(true);
    setError(undefined);
    
    try {
      const response = await api.newGame(theme);
      
      setMessages([
        {
          content: response.message,
          sender: 'bot'
        }
      ]);
      setGameStarted(true);
    } catch (err) {
      setError('Error starting new game: ' + (err instanceof Error ? err.message : String(err)));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;
    
    // Add user message to chat
    setMessages(prev => [...prev, { content, sender: 'user' }]);
    setIsLoading(true);
    setError(undefined);
    
    try {
      // If we don't have a session ID yet, start a new game
      if (!api.getCurrentSessionId()) {
        await startNewGame();
        return; // Return early as startNewGame will add the welcome message
      }
      
      const response = await api.sendMessage(content, theme);
      
      // Add bot response to chat
      if (response.message) {
        setMessages(prev => [...prev, { 
          content: response.message, 
          sender: 'bot' 
        }]);
      } else if (response.error) {
        setError(response.error);
      }
    } catch (err) {
      setError('Error sending message: ' + (err instanceof Error ? err.message : String(err)));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className={`app-container ${isDarkMode ? 'dark' : ''}`}>
      <header className="app-header flex justify-between items-center">
        <div>
          <h1 className="app-title">MUD Adventure</h1>
          {gameStarted && (
            <span className="app-theme">Current theme: {theme}</span>
          )}
        </div>
        <button
          onClick={() => {
            const newMode = !isDarkMode
            setIsDarkMode(newMode)
            localStorage.setItem('darkMode', JSON.stringify(newMode))
          }}
          className={`p-2 rounded-full ${isDarkMode ? 'bg-yellow-400 text-gray-900' : 'bg-gray-800 text-white'}`}
          aria-label="Toggle dark mode"
        >
          {isDarkMode ? (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          ) : (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
          )}
        </button>
      </header>
      
      <main className="app-main">
        {gameStarted ? (
          <ChatWindow messages={messages} />
        ) : (
          <div className="welcome-container">
            <h2 className="text-xl font-bold mb-4">Welcome to MUD Adventure</h2>
            <p className="mb-4">Select a theme and click "Start Game" to begin your Japanese learning adventure, or load a previous game below.</p>
            
            {savedSessions.length > 0 && (
              <div className="mt-8">
                <h3 className="text-lg font-semibold mb-3">Previous Games</h3>
                <div className="space-y-2">
                  {savedSessions.map((session) => (
                    <div 
                      key={session.id} 
                      className={`p-4 rounded-lg border ${isDarkMode ? 'border-gray-700 hover:border-gray-600' : 'border-gray-200 hover:border-gray-300'} cursor-pointer transition-colors`}
                      onClick={() => loadGame(session.id)}
                    >
                      <div className="flex justify-between items-center">
                        <div>
                          <div className="font-medium">{session.theme} Theme</div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">{session.createdAt}</div>
                        </div>
                        <button 
                          className="px-3 py-1 text-sm bg-blue-500 dark:bg-blue-600 text-white rounded hover:bg-blue-600 dark:hover:bg-blue-700 transition-colors"
                          onClick={(e) => {
                            e.stopPropagation();
                            loadGame(session.id);
                          }}
                        >
                          Load Game
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </main>
      
      {gameStarted && (
        <footer className="app-footer">
          <div className="footer-container">
            <ChatInput 
              onSendMessage={handleSendMessage} 
              isLoading={isLoading}
              placeholder="Type your command..."
            />
          </div>
        </footer>
      )}
      
      <footer className="app-footer">
        <div className="flex items-center gap-3">
          <select 
            className="theme-dropdown p-2 border rounded"
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
          >
            {themes.map(t => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
          
          <button 
            onClick={() => startNewGame()} 
            className="app-button flex items-center gap-2"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {gameStarted ? 'Generating...' : 'Starting...'}
              </>
            ) : (
              gameStarted ? 'New Game' : 'Start Game'
            )}
          </button>
        </div>
        
        {api.getCurrentSessionId() && (
          <span className="app-session-id">
            Session ID: {api.getCurrentSessionId()?.substring(0, 8)}...
          </span>
        )}
      </footer>
    </div>
  )
}

export default App;
