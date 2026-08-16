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
          <span className="chat-empty-icon">
            <MessageCircle size={40} strokeWidth={2.5} />
          </span>
          <span className="chat-empty-tag">RAG · IPCC + FAO</span>
          <h2>Ask the corpus</h2>
          <p>
            Questions about climate impacts on agriculture and adaptation
            strategies, answered from indexed IPCC and FAO literature — every
            claim cited back to a document and page.
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
          <span>Retrieving &amp; generating…</span>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
