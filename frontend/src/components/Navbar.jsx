import { Leaf, Github, Info } from 'lucide-react';

export default function Navbar({ currentPage, onNavigate }) {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Leaf size={28} />
        <span>My Climate CoPilot</span>
      </div>
      <div className="navbar-links">
        <a 
          href="#" 
          className="navbar-link"
          onClick={(e) => { e.preventDefault(); onNavigate('chat'); }}
          style={{ color: currentPage === 'chat' ? 'var(--color-primary)' : undefined }}
        >
          Chat
        </a>
        <a 
          href="#" 
          className="navbar-link"
          onClick={(e) => { e.preventDefault(); onNavigate('about'); }}
          style={{ color: currentPage === 'about' ? 'var(--color-primary)' : undefined }}
        >
          <Info size={16} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
          About
        </a>
        <a 
          href="https://github.com/anusanth26/MyClimateCopilot"
          className="navbar-link"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Github size={16} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
          GitHub
        </a>
      </div>
    </nav>
  );
}
