"use client";

import { useState, useEffect, useRef } from "react";
import { Search, List, Play, Zap, Maximize2, Minimize2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { createPortal } from "react-dom";

interface JobConfigProps {
    onStart: (queries: string[]) => void;
    disabled?: boolean;
}

export function JobConfig({ onStart, disabled }: JobConfigProps) {
    const [singleQuery, setSingleQuery] = useState("");
    const [multipleQueries, setMultipleQueries] = useState("");
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [mounted, setMounted] = useState(false);
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const gutterRef = useRef<HTMLDivElement>(null);
    const fullscreenGutterRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        setMounted(true);
    }, []);

    // Persist queries to localStorage
    useEffect(() => {
        const savedSingle = localStorage.getItem("singleQuery");
        const savedMultiple = localStorage.getItem("multipleQueries");
        if (savedSingle) setSingleQuery(savedSingle);
        if (savedMultiple) setMultipleQueries(savedMultiple);
    }, []);

    useEffect(() => {
        localStorage.setItem("singleQuery", singleQuery);
    }, [singleQuery]);

    useEffect(() => {
        localStorage.setItem("multipleQueries", multipleQueries);
    }, [multipleQueries]);

    useEffect(() => {
        if (isFullscreen) {
            document.body.style.overflow = 'hidden';

            const handleKeyDown = (e: KeyboardEvent) => {
                if (e.key === 'Escape') {
                    setIsFullscreen(false);
                }
            };
            window.addEventListener('keydown', handleKeyDown);
            return () => {
                window.removeEventListener('keydown', handleKeyDown);
                document.body.style.overflow = 'unset';
            };
        } else {
            document.body.style.overflow = 'unset';
        }
    }, [isFullscreen]);

    const handleSingleSubmit = () => {
        const query = singleQuery.trim();
        if (query) onStart([query]);
    };

    const handleMultipleSubmit = () => {
        const queries = multipleQueries
            .split("\n")
            .map((q) => q.trim())
            .filter((q) => q.length > 0);
        if (queries.length > 0) onStart(queries);
    };

    return (
        <section className="bg-bg-card backdrop-blur-xl border border-white/10 rounded-2xl p-6 md:p-8 shadow-md hover:border-accent-purple/30 hover:shadow-glow transition-all duration-300">
            <div className="flex flex-col gap-2 mb-8 pb-6 border-b border-white/10">
                <h2 className="text-2xl font-semibold flex items-center gap-3">
                    <Zap className="text-accent-purple" size={24} />
                    Configure Scraping
                </h2>
                <p className="text-text-secondary text-sm">Extract business data from Google Places</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Single Query */}
                <div className="flex flex-col gap-4">
                    <label className="flex items-center gap-2 text-xs font-medium text-text-secondary uppercase tracking-wider">
                        <Search size={14} className="text-accent-purple" />
                        Single Query
                    </label>
                    <input
                        type="text"
                        value={singleQuery}
                        onChange={(e) => setSingleQuery(e.target.value)}
                        disabled={disabled}
                        placeholder="e.g., restaurants, hotels, gyms"
                        className="w-full p-3 bg-bg-secondary border border-white/10 rounded-lg text-text-primary focus:outline-none focus:border-accent-purple focus:ring-4 focus:ring-accent-purple/10 transition-all"
                    />
                    <button
                        onClick={handleSingleSubmit}
                        disabled={disabled || !singleQuery.trim()}
                        className="w-full flex items-center justify-center gap-2 p-3 bg-primary-gradient text-white rounded-lg font-medium shadow-lg shadow-accent-purple/20 hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none transition-all"
                    >
                        <Play size={16} fill="currentColor" />
                        Start Single Query
                    </button>
                </div>

                {/* Multiple Queries */}
                <div className="flex flex-col gap-4">
                    <label className="flex items-center gap-2 text-xs font-medium text-text-secondary uppercase tracking-wider">
                        <List size={14} className="text-accent-purple" />
                        Multiple Queries (one per line)
                    </label>

                    <div className="relative group overflow-hidden bg-bg-secondary border border-white/10 rounded-lg focus-within:border-accent-purple focus-within:ring-4 focus-within:ring-accent-purple/10 transition-all min-h-[200px]">
                        <div
                            ref={gutterRef}
                            className="absolute left-0 top-0 bottom-0 w-12 bg-white/5 border-r border-white/10 flex flex-col items-center py-3 select-none pointer-events-none z-0 overflow-hidden"
                        >
                            {multipleQueries.split('\n').map((_, i) => (
                                <span key={i} className="text-[11px] font-mono text-white/40 h-6 flex items-center justify-center shrink-0">
                                    {i + 1}
                                </span>
                            ))}
                        </div>
                        <textarea
                            value={multipleQueries}
                            onChange={(e) => setMultipleQueries(e.target.value)}
                            onScroll={(e) => {
                                if (gutterRef.current) {
                                    gutterRef.current.scrollTop = e.currentTarget.scrollTop;
                                }
                            }}
                            disabled={disabled}
                            placeholder="restaurants&#10;coffee shops&#10;gyms"
                            className="w-full pl-15 p-3 bg-transparent border-none text-text-primary text-sm leading-6 focus:outline-none transition-all resize-none relative z-1 h-full min-h-[200px]"
                            style={{
                                backgroundImage: 'linear-gradient(transparent 23px, rgba(255, 255, 255, 0.03) 24px)',
                                backgroundSize: '100% 24px',
                                lineHeight: '24px'
                            }}
                        />
                        <button
                            onClick={() => setIsFullscreen(true)}
                            className="absolute bottom-3 right-3 p-2 rounded-lg bg-white/5 border border-white/10 text-text-tertiary hover:text-accent-purple hover:border-accent-purple/50 transition-all backdrop-blur-md z-10"
                            title="Full Screen"
                        >
                            <Maximize2 size={18} />
                        </button>
                    </div>

                    <button
                        onClick={handleMultipleSubmit}
                        disabled={disabled || !multipleQueries.trim()}
                        className="w-full flex items-center justify-center gap-2 p-3 bg-secondary-gradient text-white rounded-lg font-medium shadow-lg shadow-accent-pink/20 hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                    >
                        <Play size={16} fill="currentColor" />
                        Start Multiple Queries
                    </button>
                </div>
            </div>

            {/* Fullscreen Portal */}
            {mounted && isFullscreen && createPortal(
                <div className="fixed inset-0 z-[99999] bg-[#0b0e14] flex flex-col p-8 md:p-12">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-6 shrink-0">
                        <div>
                            <h3 className="text-2xl font-bold text-white flex items-center gap-3">
                                <List className="text-accent-purple" size={28} />
                                Multiple Queries Editor
                            </h3>
                            <p className="text-text-tertiary text-sm mt-1">One query per line • Line numbers enabled</p>
                        </div>
                        <button
                            onClick={() => setIsFullscreen(false)}
                            className="p-3 rounded-xl bg-white/5 border border-white/10 text-text-tertiary hover:text-white hover:bg-white/10 transition-all flex items-center gap-3"
                        >
                            <Minimize2 size={22} />
                            <span className="font-semibold">Exit Fullscreen</span>
                        </button>
                    </div>

                    {/* Editor - Takes remaining space */}
                    <div className="flex-1 relative bg-bg-secondary border border-white/20 rounded-2xl overflow-hidden shadow-2xl focus-within:border-accent-purple transition-all mb-6">
                        <div
                            ref={fullscreenGutterRef}
                            className="absolute left-0 top-0 bottom-0 w-16 bg-white/5 border-r border-white/10 flex flex-col items-center py-3 select-none pointer-events-none z-0 overflow-hidden"
                        >
                            {multipleQueries.split('\n').map((_, i) => (
                                <span key={i} className="text-sm font-mono text-white/40 h-8 flex items-center justify-center shrink-0">
                                    {i + 1}
                                </span>
                            ))}
                        </div>
                        <textarea
                            ref={textareaRef}
                            autoFocus
                            value={multipleQueries}
                            onChange={(e) => setMultipleQueries(e.target.value)}
                            onScroll={(e) => {
                                if (fullscreenGutterRef.current) {
                                    fullscreenGutterRef.current.scrollTop = e.currentTarget.scrollTop;
                                }
                            }}
                            disabled={disabled}
                            placeholder="Enter your queries here, one per line..."
                            className="w-full h-full pl-20 p-3 bg-transparent border-none text-text-primary text-base focus:outline-none transition-all resize-none relative z-1"
                            style={{
                                backgroundImage: 'linear-gradient(transparent 31px, rgba(255, 255, 255, 0.02) 32px)',
                                backgroundSize: '100% 32px',
                                lineHeight: '32px'
                            }}
                        />
                    </div>

                    {/* Footer */}
                    <div className="shrink-0 flex flex-col gap-4">
                        <button
                            onClick={() => {
                                handleMultipleSubmit();
                                setIsFullscreen(false);
                            }}
                            disabled={disabled || !multipleQueries.trim()}
                            className="w-full flex items-center justify-center gap-4 py-6 bg-primary-gradient text-white rounded-2xl font-bold text-xl shadow-2xl shadow-accent-purple/40 hover:scale-[1.01] active:scale-[0.99] transition-all disabled:opacity-50"
                        >
                            <Play size={26} fill="currentColor" />
                            Launch Scraper for {multipleQueries.split('\n').filter(q => q.trim()).length} Queries
                        </button>
                        <p className="text-center text-text-tertiary text-sm">
                            Press <kbd className="px-2 py-1 bg-white/10 rounded font-mono text-text-secondary">Esc</kbd> to return to dashboard
                        </p>
                    </div>
                </div>,
                document.body
            )}
        </section>
    );
}
