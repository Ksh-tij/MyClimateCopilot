import { useRef, useEffect } from 'react';
import { MessageCircle } from 'lucide-react';
import ChatMessage from './ChatMessage';

export default function ChatHistory({ messages, loading }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  if (messages.length === 0 && !loading) {
    return (
      <div className="chat-messages">
        <div className="chat-empty">
          <MessageCircle className="chat-empty-icon" size={64} />
          <h2>Welcome to My Climate CoPilot</h2>
          <p>
            Ask questions about climate change impacts on agriculture, 
            adaptation strategies, and scientific findings from IPCC, FAO, 
            and other authoritative sources.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-messages">
      {messages.map((msg, idx) => (
        <ChatMessage key={idx} message={msg} />
      ))}
      
      {loading && (
        <div className="loading-message">
          <div className="loading-spinner"></div>
          <span>Thinking...</span>
        </div>
      )}
      
      <div ref={bottomRef} />
    </div>
  );
}
