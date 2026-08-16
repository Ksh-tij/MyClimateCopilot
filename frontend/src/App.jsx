import { useState } from 'react';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import AboutPage from './pages/AboutPage';

export default function App() {
  const [currentPage, setCurrentPage] = useState('chat');

  return (
    <div className="app">
      <Navbar currentPage={currentPage} onNavigate={setCurrentPage} />
      
      {currentPage === 'chat' && <HomePage />}
      {currentPage === 'about' && <AboutPage />}
    </div>
  );
}
