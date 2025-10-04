import React, { useState, FormEvent, useRef, useEffect } from 'react';
import styles from './ChatCanvas.module.css';

interface ChatMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
}

interface ApiResponse {
  visual_description: string;
  success: boolean;
}

interface ApiError {
  error: string;
  success: boolean;
}

const ChatCanvas: React.FC = () => {
  const [inputValue, setInputValue] = useState<string>('');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto scroll to bottom when new messages are added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  // Auto resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [inputValue]);

  const generateId = (): string => {
    return Date.now().toString() + Math.random().toString(36).substr(2, 9);
  };

  const addMessage = (type: 'user' | 'ai', content: string): void => {
    const newMessage: ChatMessage = {
      id: generateId(),
      type,
      content,
      timestamp: new Date()
    };
    setChatHistory(prev => [...prev, newMessage]);
  };

  const handleSubmit = async (e?: FormEvent<HTMLFormElement>): Promise<void> => {
    if (e) e.preventDefault();
    
    if (!inputValue.trim() || isLoading) {
      return;
    }

    const userPrompt = inputValue.trim();
    setInputValue('');
    setIsLoading(true);

    // Add user message to chat history
    addMessage('user', userPrompt);

    try {
      const response = await fetch('http://localhost:8000/api/v1/visualize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: userPrompt }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ApiResponse | ApiError = await response.json();

      if (data.success && 'visual_description' in data) {
        // Add AI response to chat history
        addMessage('ai', data.visual_description);
      } else if ('error' in data) {
        addMessage('ai', `Error: ${data.error}`);
      } else {
        addMessage('ai', 'Sorry, I couldn\'t generate a visual description. Please try again.');
      }
    } catch (error) {
      console.error('Error calling API:', error);
      addMessage('ai', 'Sorry, there was an error connecting to the service. Please check if the backend is running and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>): void => {
    setInputValue(e.target.value);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>): void => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const formatTimestamp = (timestamp: Date): string => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };


  return (
    <div className={styles.chatContainer}>
      {/* Modern Header */}
      <div className={styles.header}>
        <div className={styles.headerContent}>
          <div className={styles.logo}>
            <div className={styles.logoIcon}>🎨</div>
            <h1 className={styles.title}>MindCanvas</h1>
          </div>
          <p className={styles.subtitle}>AI-powered visual storytelling</p>
        </div>
      </div>

      {/* Chat Messages Area */}
      <div className={styles.messagesContainer}>
        <div className={styles.messagesWrapper}>
          {chatHistory.length === 0 ? (
            <div className={styles.emptyState}>
              <div className={styles.emptyIcon}>✨</div>
              <h3 className={styles.emptyTitle}>Mulai Perjalanan Kreatif Anda</h3>
              <p className={styles.emptyDescription}>
                Bagikan konsep abstrak dan saksikan transformasinya menjadi cerita visual yang hidup
              </p>
              <div className={styles.suggestions}>
                <button 
                  className={styles.suggestionChip}
                  onClick={() => setInputValue('ketenangan')}
                >
                  Ketenangan
                </button>
                <button 
                  className={styles.suggestionChip}
                  onClick={() => setInputValue('inovasi')}
                >
                  Inovasi
                </button>
                <button 
                  className={styles.suggestionChip}
                  onClick={() => setInputValue('mimpi')}
                >
                  Mimpi
                </button>
              </div>
            </div>
          ) : (
            <>
              {chatHistory.map((message) => (
                <div
                  key={message.id}
                  className={`${styles.messageWrapper} ${styles[message.type]}`}
                >
                  <div className={styles.messageContent}>
                    <div className={styles.messageAvatar}>
                      {message.type === 'user' ? '👤' : '🎨'}
                    </div>
                    <div className={styles.messageBody}>
                      <div className={styles.messageText}>
                        {message.content}
                      </div>
                      <div className={styles.messageTime}>
                        {formatTimestamp(message.timestamp)}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className={`${styles.messageWrapper} ${styles.ai}`}>
                  <div className={styles.messageContent}>
                    <div className={styles.messageAvatar}>🎨</div>
                    <div className={styles.messageBody}>
                      <div className={styles.messageText}>
                        <div className={styles.typingIndicator}>
                          <span></span>
                          <span></span>
                          <span></span>
                        </div>
                        <span className={styles.typingText}>Melukis cerita visual Anda...</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Modern Input Area */}
      <div className={styles.inputArea}>
        <form onSubmit={handleSubmit} className={styles.inputForm}>
          <div className={styles.inputWrapper}>
            <textarea
              ref={textareaRef}
              value={inputValue}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Deskripsikan konsep abstrak..."
              className={styles.messageInput}
              disabled={isLoading}
              maxLength={500}
              rows={1}
            />
            <button
              type="submit"
              className={styles.sendButton}
              disabled={isLoading || !inputValue.trim()}
            >
              {isLoading ? (
                <div className={styles.sendingIcon}>⏳</div>
              ) : (
                <div className={styles.sendIcon}>➤</div>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatCanvas;
