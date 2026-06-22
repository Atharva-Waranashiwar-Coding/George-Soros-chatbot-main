import React, { useState, useEffect, useRef } from 'react';
import { useChat } from '../hooks/useChat';
import { motion, AnimatePresence } from 'framer-motion';

// Bot Avatar
const BotAvatar = () => (
    <div className="w-9 h-9 rounded-full bg-gradient-to-br from-cyan-400 to-emerald-500 flex items-center justify-center text-sm font-bold text-slate-950 flex-shrink-0 mr-3 shadow-lg shadow-cyan-500/40">
        AI
    </div>
);

// User Avatar
const UserAvatar = () => (
    <div className="w-9 h-9 rounded-full bg-slate-700 flex items-center justify-center text-sm font-bold text-slate-200 flex-shrink-0 ml-3 shadow">
        U
    </div>
);

function ChatbotPage() {
    const { messages, loading, sendMessage } = useChat();
    const [input, setInput] = useState('');
    const messagesEndRef = useRef(null);
    const messageContainerRef = useRef(null);

    const handleFormSubmit = (e) => {
        e.preventDefault();
        const trimmedInput = input.trim();
        if (!trimmedInput || loading) return;
        sendMessage(trimmedInput);
        setInput('');
    };

    useEffect(() => {
        const timer = setTimeout(() => {
            if (messageContainerRef.current) {
                messageContainerRef.current.scrollTop = messageContainerRef.current.scrollHeight;
            }
        }, 50);
        return () => clearTimeout(timer);
    }, [messages]);

    return (
        <div className="flex flex-col h-screen text-slate-100 p-4 sm:p-6 w-full md:w-4/5 mx-auto" style={{ background: "linear-gradient(135deg, #030712 0%, #060b1a 35%, #05070f 100%)" }}>
            {/* Header */}
            <h1 className="text-xl md:text-2xl font-semibold mb-4 text-center text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 via-teal-200 to-emerald-300 flex-shrink-0 drop-shadow">
                Soros Investment Insights
            </h1>
            <p className="text-xs md:text-sm text-slate-400 text-center mb-4 flex-shrink-0">
                Ask about market reflexivity, investment philosophy, and economic insights
            </p>

            {/* Message Display Area */}
            <div
                ref={messageContainerRef}
                className="flex-grow overflow-y-auto mb-4 space-y-4 p-4 bg-slate-950/60 backdrop-blur rounded-2xl border border-cyan-500/20 shadow-2xl ring-1 ring-cyan-400/10"
            >
                <AnimatePresence>
                    {messages.map((message) => (
                        <motion.div
                            key={message.id}
                            className={`flex w-full ${message.sender === 'user' ? 'justify-end' : 'justify-start items-end'}`}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0 }}
                            transition={{ duration: 0.3, ease: "easeOut" }}
                        >
                            <div className={`flex items-start max-w-[85%] md:max-w-[75%] ${message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                                {message.sender === 'bot' ? <BotAvatar /> : <UserAvatar />}
                                <div className={`shadow-lg py-2.5 px-4 rounded-2xl ${message.sender === 'user' ? 'bg-gradient-to-r from-cyan-400 to-emerald-500 text-slate-950' : 'bg-slate-900/80 text-slate-100 border border-cyan-500/20'}`}>
                                    <p className="text-sm whitespace-pre-wrap break-words leading-relaxed">{message.text}</p>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {/* Loading indicator */}
                {loading && (
                    <motion.div
                        className="flex items-start w-full"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                    >
                        <BotAvatar />
                        <div className="bg-slate-900/80 text-slate-100 border border-cyan-500/20 rounded-2xl shadow-lg py-2.5 px-4">
                            <p className="text-sm text-cyan-200 animate-pulse">Thinking...</p>
                        </div>
                    </motion.div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="flex-shrink-0">
                <form onSubmit={handleFormSubmit} className="flex items-center bg-slate-950/70 backdrop-blur p-2 rounded-2xl shadow-2xl border border-cyan-500/20 focus-within:ring-2 focus-within:ring-cyan-400 transition-all duration-300">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask about Soros's investment ideas..."
                        className="flex-grow p-3 bg-transparent text-slate-100 border-none focus:outline-none placeholder-slate-500 disabled:opacity-50 text-sm"
                        aria-label="Chat message input"
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={loading || !input.trim()}
                        className="p-2.5 ml-2 bg-gradient-to-r from-cyan-400 to-emerald-500 hover:from-cyan-300 hover:to-emerald-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-950 focus:ring-cyan-400 text-slate-950 font-semibold rounded-xl transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center shadow-lg shadow-cyan-500/30"
                        aria-label="Send message"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
                        </svg>
                    </button>
                </form>
            </div>
        </div>
    );
}

export default ChatbotPage;
