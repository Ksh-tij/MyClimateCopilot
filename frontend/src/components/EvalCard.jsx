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

function gradeFor(percentage) {
  if (percentage >= 90) return 'Excellent';
  if (percentage >= 75) return 'Good';
  if (percentage >= 60) return 'Adequate';
  if (percentage >= 40) return 'Needs work';
  return 'Poor';
}

/* Score is discrete (0-3), so render it as discrete segments rather than a
   continuous bar — the mark should match the shape of the data. */
function Meter({ score, max }) {
  return (
    <div
      className="eval-meter"
      role="img"
      aria-label={`${score} of ${max} sub-criteria met`}
    >
      {Array.from({ length: max }, (_, i) => (
        <span key={i} className={`eval-seg ${i < score ? 'is-on' : ''}`} />
      ))}
    </div>
  );
}

export default function EvalCard({ evaluation }) {
  if (!evaluation) {
    return (
      <div className="sidebar-section">
        <h3>
          <BarChart3 size={16} />
          Evaluation
        </h3>
        <p className="sidebar-hint">
          Turn on <strong>Include Evaluation</strong> to score the answer against
          the 7-dimension expert rubric.
        </p>
      </div>
    );
  }

  const dimensions = Object.entries(evaluation.dimensions || {});

  return (
    <div className="sidebar-section">
      <h3>
        <BarChart3 size={16} />
        Evaluation Score
      </h3>

      <div className="eval-summary">
        <div className="eval-score">
          {evaluation.total_score}
          <span className="eval-max">/{evaluation.max_score}</span>
        </div>
        <div className="eval-score-meta">
          <div className="eval-percentage">{evaluation.percentage.toFixed(1)}%</div>
          <span className="eval-grade">{gradeFor(evaluation.percentage)}</span>
        </div>
      </div>

      <div className="eval-dimensions">
        {dimensions.map(([key, dim]) => (
          <div key={key} className="eval-dimension">
            <span className="eval-dimension-name">
              {DIMENSION_LABELS[key] || dim.name}
            </span>
            <Meter score={dim.score} max={dim.max_score} />
            <span className="eval-dimension-score">
              {dim.score}/{dim.max_score}
            </span>
          </div>
        ))}
      </div>

      {evaluation.feedback && (
        <div className="eval-feedback">
          <span className="eval-feedback-label">Evaluator notes</span>
          {evaluation.feedback}
        </div>
      )}
    </div>
  );
}
