import { Leaf, Github, Info, MessageSquare } from 'lucide-react';

export default function Navbar({ currentPage, onNavigate }) {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <span className="navbar-brand-mark">
          <Leaf size={22} strokeWidth={2.5} />
        </span>
        <span>My Climate CoPilot</span>
      </div>

      <div className="navbar-links">
        <a
          href="#"
          className={`navbar-link ${currentPage === 'chat' ? 'is-active' : ''}`}
          onClick={(e) => { e.preventDefault(); onNavigate('chat'); }}
        >
          <MessageSquare size={14} strokeWidth={2.5} />
          Chat
        </a>
        <a
          href="#"
          className={`navbar-link ${currentPage === 'about' ? 'is-active' : ''}`}
          onClick={(e) => { e.preventDefault(); onNavigate('about'); }}
        >
          <Info size={14} strokeWidth={2.5} />
          About
        </a>
        <a
          href="https://github.com/Ksh-tij/MyClimateCopilot"
          className="navbar-link"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Github size={14} strokeWidth={2.5} />
          GitHub
        </a>
      </div>
    </nav>
  );
}
