import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './app/App'
import './index.css'

// Startup banner
const showStartupBanner = () => {
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  const port = window.location.port || (protocol === 'https:' ? '443' : '80');
  
  const ip = hostname === 'localhost' 
    ? 'http://localhost:' + port 
    : protocol + '//' + hostname + ':' + port;
  
  console.log(`
╔═══════════════════════════════════════════════════════════╗
║                    BitRAG Frontend                         ║
║              Initialization Complete!                      ║
╠═══════════════════════════════════════════════════════════╣
║  Frontend active at: ${ip.padEnd(48)}║
║                                                               ║
║  Ensure backend is running on http://localhost:5000         ║
╚═══════════════════════════════════════════════════════════╝
  `);
};

// Show banner after DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', showStartupBanner);
} else {
  showStartupBanner();
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
