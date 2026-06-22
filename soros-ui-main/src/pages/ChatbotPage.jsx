import React, { useState, useEffect, useRef } from 'react';
import { useChat } from '../hooks/useChat';
import { Switch } from '@headlessui/react';
import { motion, AnimatePresence } from 'framer-motion';

// Bot Avatar - Solid Color
const BotAvatar = () => (
    <div className="w-9 h-9 rounded-full bg-gradient-to-br from-cyan-400 to-emerald-500 flex items-center justify-center text-sm font-bold text-slate-950 flex-shrink-0 mr-3 shadow-lg shadow-cyan-500/40">
        AI
    </div>
);
// User Avatar Placeholder
const UserAvatar = () => (
    <div className="w-9 h-9 rounded-full bg-slate-700 flex items-center justify-center text-sm font-bold text-slate-200 flex-shrink-0 ml-3 shadow">
        U
    </div>
);

const ModelSelector = ({ model, setModel }) => {
    return (
        <div className="flex items-center space-x-3 p-3 bg-slate-950/70 rounded-xl border border-cyan-500/20">
            <label className="text-xs uppercase tracking-wide text-cyan-200/80">Model</label>
            <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="bg-slate-900 text-slate-100 border border-cyan-500/30 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-400"
            >
                <option value="gemini">Gemini (Soros)</option>
                <option value="rag">Custom RAG</option>
                <option value="transformer">Transformer API</option>
            </select>
        </div>
    );
};


function ChatbotPage() {
    const { messages, loading, sendMessage, transformerToken, setTransformerToken } = useChat();
    const [input, setInput] = useState('');
    const [selectedModel, setSelectedModel] = useState('rag');

    const messagesEndRef = useRef(null);
    const messageContainerRef = useRef(null);

    const handleFormSubmit = (e) => {
        e.preventDefault();
        const trimmedInput = input.trim();
        if (!trimmedInput || loading) return;
        sendMessage(trimmedInput, selectedModel);
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
        // Main container - Apply user's width/centering preference
        <div className="flex flex-col h-screen text-slate-100 p-4 sm:p-6 w-full md:w-4/5 mx-auto" style={{ background: "linear-gradient(135deg, #030712 0%, #060b1a 35%, #05070f 100%)" }}>
            {/* Header */}
            <h1 className="text-xl md:text-2xl font-semibold mb-4 text-center text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 via-teal-200 to-emerald-300 flex-shrink-0 drop-shadow">
                AI Investment Chatbot
            </h1>

            {/* Message Display Area - Darker BG */}
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

                {/* Loading indicator - Minimal Text */}
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

            {/* Footer Area containing Input and Switch */}
            <div className="flex-shrink-0 pt-2">
                {selectedModel === 'transformer' && (
                    <div className="mb-2 flex flex-col sm:flex-row sm:items-center sm:space-x-3 space-y-2 sm:space-y-0 bg-slate-950/70 backdrop-blur px-3 py-2 rounded-xl border border-cyan-500/20">
                        <label className="text-xs uppercase tracking-wide text-cyan-200/80">Transformer Token</label>
                        <input
                            type="text"
                            value={transformerToken}
                            onChange={(e) => setTransformerToken(e.target.value)}
                            placeholder="Paste bearer token"
                            className="flex-grow p-2 bg-slate-900 text-slate-100 border border-cyan-500/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-400 text-xs"
                        />
                    </div>
                )}
                {/* Input Form */}
                <form onSubmit={handleFormSubmit} className="flex items-center bg-slate-950/70 backdrop-blur p-2 rounded-2xl shadow-2xl border border-cyan-500/20 focus-within:ring-2 focus-within:ring-cyan-400 transition-all duration-300">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder={`Ask ${selectedModel === 'gemini' ? 'Gemini (Soros Style)' : selectedModel === 'rag' ? 'Soros RAG - macro/risk questions' : 'Transformer model'}...`}
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
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5"> <path strokeLinecap="round" strokeLinejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" /> </svg>
                    </button>
                </form>

                {/* Model Toggle Switch - Below Input */}
                <div className="mt-3 flex justify-center"> {/* Adjusted margin */}
                    <ModelSelector model={selectedModel} setModel={setSelectedModel} />
                </div>
            </div>

        </div>
    );
}

export default ChatbotPage;
