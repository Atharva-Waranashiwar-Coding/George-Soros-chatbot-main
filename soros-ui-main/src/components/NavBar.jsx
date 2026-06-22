import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const links = [
  { to: '/', label: 'Home' },
  { to: '/chatbot', label: 'Chatbot' },
  { to: '/pairs', label: 'Pairs Backtest' },
];

function NavBar() {
  const location = useLocation();

  return (
    <header className="bg-slate-950/70 backdrop-blur border-b border-cyan-500/20 shadow-lg shadow-cyan-500/10">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <span className="text-lg font-semibold text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 via-teal-200 to-emerald-300 drop-shadow">
          Soros Macro Lab
        </span>
        <nav className="flex items-center space-x-3 text-sm">
          {links.map((link) => {
            const active = location.pathname === link.to;
            return (
              <Link
                key={link.to}
                to={link.to}
                className={`px-3 py-1.5 rounded-xl transition-colors ${
                  active
                    ? 'bg-gradient-to-r from-cyan-400 to-emerald-500 text-slate-950 font-semibold shadow-lg shadow-cyan-500/30'
                    : 'text-slate-300 hover:text-white hover:bg-slate-900/60 border border-transparent hover:border-cyan-500/30'
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}

export default NavBar;
