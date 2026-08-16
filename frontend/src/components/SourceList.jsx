import { useState } from 'react';
import { FileText, ChevronDown, ChevronUp } from 'lucide-react';

function SourceCard({ source, index }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div 
      className={`source-card ${expanded ? 'expanded' : ''}`}
      onClick={() => setExpanded(!expanded)}
    >
      <div className="source-card-header">
        <span className="source-card-number">{index + 1}</span>
        <span className="source-card-title">{source.title}</span>
        {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </div>
      <div className="source-card-meta">
        {source.source} • Page {source.page_number}
      </div>
      <div className="source-card-text">
        {source.text}
      </div>
      <div className="source-card-score">
        Relevance: {(source.score * 100).toFixed(1)}%
      </div>
    </div>
  );
}

export default function SourceList({ sources }) {
  if (!sources || sources.length === 0) {
    return (
      <div className="sidebar-section">
        <h3>
          <FileText size={18} />
          Sources
        </h3>
        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>
          Retrieved passages will appear here after you ask a question.
        </p>
      </div>
    );
  }

  return (
    <div className="sidebar-section">
      <h3>
        <FileText size={18} />
        Sources ({sources.length})
      </h3>
      <div className="sources-list">
        {sources.map((source, idx) => (
          <SourceCard key={source.chunk_id || idx} source={source} index={idx} />
        ))}
      </div>
    </div>
  );
}
