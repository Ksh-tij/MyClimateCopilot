import { BarChart3 } from 'lucide-react';

const DIMENSION_LABELS = {
  '1_context': 'Context',
  '2_structure': 'Structure',
  '3_language': 'Language',
  '4_citations': 'Citations',
  '5_specificity': 'Specificity',
  '6_comprehensiveness': 'Comprehensive',
  '7_accuracy': 'Accuracy'
};

export default function EvalCard({ evaluation }) {
  if (!evaluation) {
    return (
      <div className="sidebar-section">
        <h3>
          <BarChart3 size={18} />
          Evaluation
        </h3>
        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>
          Enable "Include Evaluation" to see quality scores for responses.
        </p>
      </div>
    );
  }

  const dimensions = Object.entries(evaluation.dimensions || {});

  return (
    <div className="sidebar-section">
      <h3>
        <BarChart3 size={18} />
        Evaluation Score
      </h3>
      
      <div className="eval-summary">
        <div className="eval-score">
          {evaluation.total_score}
          <span className="eval-max">/{evaluation.max_score}</span>
        </div>
        <div className="eval-percentage">
          {evaluation.percentage.toFixed(1)}%
        </div>
      </div>
      
      <div className="eval-dimensions">
        {dimensions.map(([key, dim]) => (
          <div key={key} className="eval-dimension">
            <span className="eval-dimension-name">
              {DIMENSION_LABELS[key] || dim.name}
            </span>
            <div className="eval-dimension-bar">
              <div 
                className="eval-dimension-fill"
                style={{ width: `${(dim.score / dim.max_score) * 100}%` }}
              />
            </div>
            <span className="eval-dimension-score">
              {dim.score}/{dim.max_score}
            </span>
          </div>
        ))}
      </div>
      
      {evaluation.feedback && (
        <div className="eval-feedback">
          "{evaluation.feedback}"
        </div>
      )}
    </div>
  );
}
