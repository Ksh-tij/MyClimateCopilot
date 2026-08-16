import { useState } from 'react';
import { AlertCircle } from 'lucide-react';
import ChatHistory from '../components/ChatHistory';
import ChatInput from '../components/ChatInput';
import EvalCard from '../components/EvalCard';
import SourceList from '../components/SourceList';
import { askQuestion } from '../services/api';

export default function HomePage() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastResponse, setLastResponse] = useState(null);
  const [options, setOptions] = useState({
    topK: 5,
    mode: 'hybrid',
    includeEvaluation: false
  });

  const handleSend = async (query) => {
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: query }]);
    setLoading(true);
    setError(null);

    try {
      const response = await askQuestion({
        query,
        topK: options.topK,
        mode: options.mode,
        includeSources: true,
        includeEvaluation: options.includeEvaluation
      });

      // Add assistant message
      setMessages(prev => [...prev, { role: 'assistant', content: response.answer }]);
      setLastResponse(response);
    } catch (err) {
      setError(err.message);
      // Add error message
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `Sorry, I encountered an error: ${err.message}. Please make sure the backend server is running.`
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="main-content">
      <div className="chat-section">
        {error && (
          <div className="error-message" style={{ margin: 'var(--spacing-md)' }}>
            <AlertCircle size={18} />
            {error}
          </div>
        )}
        
        <ChatHistory messages={messages} loading={loading} />
        
        <ChatInput 
          onSend={handleSend}
          disabled={loading}
          options={options}
          onOptionsChange={setOptions}
        />
      </div>
      
      <aside className="sidebar">
        <EvalCard evaluation={lastResponse?.evaluation} />
        <SourceList sources={lastResponse?.sources} />
      </aside>
    </div>
  );
}
