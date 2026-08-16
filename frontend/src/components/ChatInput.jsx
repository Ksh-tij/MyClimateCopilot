import { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';

export default function ChatInput({ 
  onSend, 
  disabled,
  options,
  onOptionsChange
}) {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 150) + 'px';
    }
  }, [input]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="chat-input-container">
      <form onSubmit={handleSubmit} className="chat-input-wrapper">
        <textarea
          ref={textareaRef}
          className="chat-input"
          placeholder="Ask a question about climate change and agriculture..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          rows={1}
        />
        <button 
          type="submit" 
          className="chat-send-btn"
          disabled={disabled || !input.trim()}
        >
          <Send size={20} />
        </button>
      </form>
      
      <div className="chat-options">
        <label className="chat-option">
          <input
            type="checkbox"
            checked={options.includeEvaluation}
            onChange={(e) => onOptionsChange({ ...options, includeEvaluation: e.target.checked })}
          />
          Include Evaluation
        </label>
        
        <label className="chat-option">
          Mode:
          <select
            value={options.mode}
            onChange={(e) => onOptionsChange({ ...options, mode: e.target.value })}
          >
            <option value="hybrid">Hybrid</option>
            <option value="dense">Dense (Semantic)</option>
            <option value="bm25">BM25 (Keyword)</option>
          </select>
        </label>
        
        <label className="chat-option">
          Sources:
          <select
            value={options.topK}
            onChange={(e) => onOptionsChange({ ...options, topK: parseInt(e.target.value) })}
          >
            <option value="3">3</option>
            <option value="5">5</option>
            <option value="7">7</option>
            <option value="10">10</option>
          </select>
        </label>
      </div>
    </div>
  );
}
