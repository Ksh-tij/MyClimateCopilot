export default function AboutPage() {
  return (
    <div className="about-page">
      <h1>About My Climate CoPilot</h1>
      
      <p>
        My Climate CoPilot is an AI-powered Question Answering system designed to help 
        agronomists, climate scientists, and farmer advisors understand climate change 
        impacts on agriculture and explore adaptation strategies.
      </p>

      <h2>How It Works</h2>
      <p>
        The system uses <strong>Retrieval-Augmented Generation (RAG)</strong> to provide 
        accurate, citation-backed answers from authoritative climate science literature.
      </p>
      
      <ul>
        <li><strong>Retrieval:</strong> Finds relevant passages using hybrid search 
        (semantic embeddings + keyword matching)</li>
        <li><strong>Generation:</strong> Synthesizes a coherent answer using the 
        retrieved context with Groq's fast LLM inference</li>
        <li><strong>Evaluation:</strong> Self-assesses response quality across 7 
        expert-defined dimensions</li>
      </ul>

      <h2>Knowledge Base</h2>
      <p>
        Our knowledge base includes documents from authoritative sources:
      </p>
      <ul>
        <li>IPCC Assessment Reports (AR5, AR6)</li>
        <li>FAO Climate Change Guidelines</li>
        <li>WMO Climate Science Reports</li>
        <li>Regional Climate Adaptation Studies</li>
      </ul>

      <h2>Evaluation Framework</h2>
      <p>
        Responses are evaluated across 7 dimensions with 21 sub-criteria:
      </p>
      <ul>
        <li><strong>Context:</strong> Provides background and summary</li>
        <li><strong>Structure:</strong> Well-organized with headings and bullets</li>
        <li><strong>Language:</strong> Clear, grammatically correct, domain-appropriate</li>
        <li><strong>Citations:</strong> Properly referenced sources</li>
        <li><strong>Specificity:</strong> Location and commodity-specific information</li>
        <li><strong>Comprehensiveness:</strong> Complete, in-depth coverage</li>
        <li><strong>Scientific Accuracy:</strong> Factually correct, evidence-based</li>
      </ul>

      <h2>Technology Stack</h2>
      <ul>
        <li><strong>Frontend:</strong> React + Vite</li>
        <li><strong>Backend:</strong> FastAPI + Python</li>
        <li><strong>Embeddings:</strong> sentence-transformers (all-MiniLM-L6-v2)</li>
        <li><strong>Vector Search:</strong> FAISS + BM25 with Reciprocal Rank Fusion</li>
        <li><strong>LLM:</strong> Groq API (llama-3.3-70b-versatile)</li>
      </ul>

      <h2>Research Background</h2>
      <p>
        This project is based on the ACL 2025 paper: 
        <em>"My Climate CoPilot: A Question Answering System for Climate Adaptation in Agriculture"</em>
      </p>

      <h2>Open Source</h2>
      <p>
        This project is open source. View the code, contribute, or report issues on{' '}
        <a href="https://github.com/anusanth26/MyClimateCopilot" target="_blank" rel="noopener noreferrer">
          GitHub
        </a>.
      </p>
    </div>
  );
}
