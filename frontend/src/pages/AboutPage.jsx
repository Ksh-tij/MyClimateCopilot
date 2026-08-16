export default function AboutPage() {
  return (
    <div className="about-page">
      <div className="about-hero">
        <h1>About</h1>
        <p>
          My Climate CoPilot answers questions about climate change impacts on
          agriculture using Retrieval-Augmented Generation over authoritative
          IPCC and FAO literature — with every claim traceable to a document and
          page number.
        </p>
      </div>

      <div className="about-section">
        <h2>Knowledge Base</h2>
        <div className="about-stats">
          <div className="about-stat">
            <div className="about-stat-value">8,191</div>
            <div className="about-stat-label">Passages indexed</div>
          </div>
          <div className="about-stat">
            <div className="about-stat-value">12</div>
            <div className="about-stat-label">Documents</div>
          </div>
          <div className="about-stat">
            <div className="about-stat-value">384</div>
            <div className="about-stat-label">Vector dims</div>
          </div>
          <div className="about-stat">
            <div className="about-stat-value">21</div>
            <div className="about-stat-label">Eval criteria</div>
          </div>
        </div>
      </div>

      <div className="about-section">
        <h2>How It Works</h2>
        <ul>
          <li>
            <strong>Retrieval —</strong> finds relevant passages using hybrid
            search: FAISS semantic embeddings fused with BM25 keyword matching
            via Reciprocal Rank Fusion.
          </li>
          <li>
            <strong>Generation —</strong> synthesizes an answer strictly from the
            retrieved context, with inline citations, via Groq's LLM inference.
          </li>
          <li>
            <strong>Evaluation —</strong> scores the response across 7
            expert-defined dimensions in a separate, independent LLM pass.
          </li>
        </ul>
      </div>

      <div className="about-section">
        <h2>Sources</h2>
        <ul>
          <li>IPCC Assessment Reports (AR5, AR6 — WGI, WGII, WGIII, Synthesis)</li>
          <li>FAO Climate-Smart Agriculture guidelines and sourcebooks</li>
          <li>FAO climate adaptation and food security reports</li>
        </ul>
      </div>

      <div className="about-section">
        <h2>Evaluation Framework</h2>
        <p>
          Responses are scored across 7 dimensions with 3 binary sub-criteria
          each, giving 21 points total.
        </p>
        <ul>
          <li><strong>Context —</strong> background framing and closing summary</li>
          <li><strong>Structure —</strong> logical headings and readable organisation</li>
          <li><strong>Language —</strong> fluent, correct, domain-appropriate</li>
          <li><strong>Citations —</strong> appropriate, well-quantified, easy to follow</li>
          <li><strong>Specificity —</strong> commodity and location detail, or admitting its absence</li>
          <li><strong>Comprehensiveness —</strong> complete coverage with depth</li>
          <li><strong>Scientific Accuracy —</strong> robust and consistent with the sources</li>
        </ul>
        <p>
          <strong>Note on interpretation:</strong> this rubric measures
          presentational quality and consistency with the retrieved sources. It
          is not an independent fact-check against ground truth, and because the
          evaluator shares a model family with the generator, scores skew high.
        </p>
      </div>

      <div className="about-section">
        <h2>Stack</h2>
        <ul>
          <li><strong>Frontend —</strong> React 18 + Vite</li>
          <li><strong>Backend —</strong> FastAPI + Pydantic + Uvicorn</li>
          <li><strong>Embeddings —</strong> sentence-transformers (all-MiniLM-L6-v2)</li>
          <li><strong>Search —</strong> FAISS IndexFlatIP + BM25Okapi, fused with RRF</li>
          <li><strong>LLM —</strong> Groq API (llama-3.3-70b-versatile)</li>
        </ul>
      </div>

      <div className="about-section">
        <h2>Research Background</h2>
        <p>
          Based on the ACL 2025 paper <em>"My Climate CoPilot: A Question
          Answering System for Climate Adaptation in Agriculture"</em>. Source
          code on{' '}
          <a
            href="https://github.com/Ksh-tij/MyClimateCopilot"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>.
        </p>
      </div>
    </div>
  );
}
