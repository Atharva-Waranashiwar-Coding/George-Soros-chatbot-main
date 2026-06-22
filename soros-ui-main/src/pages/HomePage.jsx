import React from 'react';
import { Link } from 'react-router-dom';
// Import Lucide icons
import { MessageCircle, LayoutDashboard } from 'lucide-react';

// Removed old inline SVG icon components

function HomePage() {
    return (
        <div
            className="flex flex-col items-center justify-center min-h-screen p-6 md:p-10 text-center"
            style={{ background: "linear-gradient(160deg, #030712 0%, #050b18 50%, #02040b 100%)" }}
        >
            {/* Title - More impactful */}
            <h1 className="text-4xl md:text-5xl font-extrabold mb-16 tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 via-teal-200 to-emerald-300 drop-shadow-lg">
                Soros Macro Lab <br className="hidden md:block" /> Risk & Pairs Analyzer
            </h1>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-4xl">

                {/* Chatbot Card */}
                <Link to="/chatbot" className="bg-slate-950/70 backdrop-blur rounded-2xl shadow-2xl p-8 flex flex-col items-center text-center transition-all duration-300 hover:shadow-cyan-500/30 hover:scale-[1.03] cursor-pointer border border-cyan-500/20 group ring-1 ring-cyan-400/10">
                    <MessageCircle className="w-12 h-12 mb-5 text-cyan-300 transition-all duration-300 group-hover:text-emerald-300 group-hover:scale-110" strokeWidth={1.5} />
                    <h2 className="text-2xl font-semibold mb-3 text-slate-100">
                        AI Investment Chatbot
                    </h2>
                    <p className="text-slate-300 mb-4 flex-grow">
                        Get George Soros-style macro and risk insights through conversation.
                    </p>
                    <span className="mt-auto px-6 py-2 bg-gradient-to-r from-cyan-400 to-emerald-500 group-hover:from-cyan-300 group-hover:to-emerald-400 text-slate-950 font-semibold rounded-lg transition-all duration-300 shadow-lg shadow-cyan-500/30">
                        Start Chatting
                    </span>
                </Link>

                {/* Pair Trading Card */}
                <Link to="/pairs" className="bg-slate-950/70 backdrop-blur rounded-2xl shadow-2xl p-8 flex flex-col items-center text-center transition-all duration-300 hover:shadow-cyan-500/30 hover:scale-[1.03] cursor-pointer border border-cyan-500/20 group ring-1 ring-cyan-400/10">
                    <LayoutDashboard className="w-12 h-12 mb-5 text-cyan-300 transition-all duration-300 group-hover:text-emerald-300 group-hover:scale-110" strokeWidth={1.5} />
                    <h2 className="text-2xl font-semibold mb-3 text-slate-100">
                        Pairs Trading Backtest
                    </h2>
                    <p className="text-slate-300 mb-4 flex-grow">
                        Test cointegration, hedge ratios, and simple mean-reversion P&L for your chosen pair.
                    </p>
                    <span className="mt-auto px-6 py-2 bg-gradient-to-r from-cyan-400 to-emerald-500 group-hover:from-cyan-300 group-hover:to-emerald-400 text-slate-950 font-semibold rounded-lg transition-all duration-300 shadow-lg shadow-cyan-500/30">
                        Run Backtest
                    </span>
                </Link>

            </div>
        </div>
    );
}

export default HomePage;
