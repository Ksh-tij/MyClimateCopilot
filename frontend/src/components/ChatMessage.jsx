import ReactMarkdown from 'react-markdown';
import { User, Bot } from 'lucide-react';

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`message message-${message.role}`}>
      <div className="message-avatar">
        {isUser ? <User size={18} /> : <Bot size={18} />}
      </div>
      <div className="message-content">
        {isUser ? (
          <p>{message.content}</p>
        ) : (
          <ReactMarkdown>{message.content}</ReactMarkdown>
        )}
      </div>
    </div>
  );
}
