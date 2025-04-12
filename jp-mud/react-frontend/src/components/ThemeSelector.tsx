import React from 'react';

interface ThemeSelectorProps {
  onThemeSelect: (theme: string) => void;
}

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

export const ThemeSelector: React.FC<ThemeSelectorProps> = ({ onThemeSelect }) => {
  return (
    <div className="theme-selector">
      <h2 className="text-xl font-bold mb-4">Choose a Theme</h2>
      <p className="mb-4">Select a setting for your Japanese learning adventure:</p>
      
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {themes.map(theme => (
          <button
            key={theme.id}
            onClick={() => onThemeSelect(theme.id)}
            className="p-3 border rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            {theme.name}
          </button>
        ))}
      </div>
    </div>
  );
};
