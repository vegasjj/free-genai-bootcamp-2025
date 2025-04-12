import React, { useEffect, useRef } from 'react';

interface Message {
  content: string;
  sender: 'user' | 'bot';
}

interface ChatWindowProps {
  messages: Message[];
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ messages }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex-1 p-4 overflow-y-auto">
      {messages.map((message, index) => (
        <div 
          key={index} 
          className={`mb-4 p-4 rounded-lg text-lg transition-colors ${
            message.sender === 'user' 
              ? 'bg-blue-100 dark:bg-blue-900 text-gray-900 dark:text-white ml-auto max-w-[80%]' 
              : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white max-w-[80%]'
          }`}
        >
          {message.content}
        </div>
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};
