import React, { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import './App.css';
import AiHeadIcon from './AiHeadIcon';
import kryptoBackground from './Krypto.jpg';

function App() {
  const [userInput, setUserInput] = useState('');
  const [conversation, setConversation] = useState([]);
  const [sessionID, setSessionID] = useState('');
  const [chatHistories, setChatHistories] = useState([]);

  useEffect(() => {
    const initializeChatSession = async () => {
      const newSessionId = uuidv4();
      const sessionName = window.prompt("Would you like to name this chat session? Leave blank for 'Default Chat'.");
      setSessionID(newSessionId);
      await fetchChatHistory(newSessionId, sessionName || 'Default Chat');
    };
    
    initializeChatSession();
  }, []);

  const fetchChatHistory = async (sessionId, name) => {
    try {
      const historyResponse = await fetch('http://127.0.0.1:5000/chat-history');
      const histories = await historyResponse.json();
      setChatHistories(histories);

      await fetch('http://127.0.0.1:5000/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: '',
          session_id: sessionId,
          name: name,
        }),
      });
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleUserInput = (event) => {
    setUserInput(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const message = userInput.trim();
    if (message) {
      setConversation([...conversation, { sender: 'user', text: message }]);
      setUserInput('');

      try {
        const response = await fetch('http://127.0.0.1:5000/message', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message, session_id: sessionID }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        setConversation(conversation => [...conversation, { sender: 'bot', text: data.reply }]);
      } catch (error) {
        console.error('There was a problem with the fetch operation:', error);
      }
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <AiHeadIcon />
        <h1>Kelex<span className="chatbot-subtitle">my chatbot</span></h1>
      </header>
      <div className="chat-history-container">
        {chatHistories.length === 0 ? (
          <p className="history-placeholder">No chat history yet...</p>
        ) : (
          chatHistories.map((session, index) => (
            <div key={index} className="session-entry">
              <h2 className="session-name">{session.name}</h2>
              <p className="session-date">{session.date}</p>
              {session.exchanges.map((entry, exchangeIndex) => (
                <div key={exchangeIndex} className={`history-entry ${entry.sender}`}>
                  {entry.text}
                </div>
              ))}
            </div>
          ))
        )}
      </div>
      <div className="chat-container">
        <div className="conversation-view">
          {conversation.map((entry, index) => (
            <div key={index} className={`message ${entry.sender === 'user' ? 'message-user' : 'message-kelex'}`}>
              {entry.text}
            </div>
          ))}
        </div>
        <form onSubmit={handleSubmit}>
          <input type="text" value={userInput} onChange={handleUserInput} placeholder="Say something..." />
          <button type="submit">Send</button>
        </form>
      </div>
    </div>
  );
}

export default App;
