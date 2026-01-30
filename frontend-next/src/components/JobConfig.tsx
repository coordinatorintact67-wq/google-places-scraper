"use client";

import { useState, useEffect } from "react";
import { Search, List, Play, Zap } from "lucide-react";
import { cn } from "@/lib/utils";

interface JobConfigProps {
    onStart: (queries: string[]) => void;
    disabled?: boolean;
}

export function JobConfig({ onStart, disabled }: JobConfigProps) {
    const [singleQuery, setSingleQuery] = useState("");
    const [multipleQueries, setMultipleQueries] = useState("");

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
                    <textarea
                        value={multipleQueries}
                        onChange={(e) => setMultipleQueries(e.target.value)}
                        disabled={disabled}
                        rows={5}
                        placeholder="restaurants&#10;coffee shops&#10;gyms"
                        className="w-full p-3 bg-bg-secondary border border-white/10 rounded-lg text-text-primary focus:outline-none focus:border-accent-purple focus:ring-4 focus:ring-accent-purple/10 transition-all resize-none"
                    />
                    <button
                        onClick={handleMultipleSubmit}
                        disabled={disabled || !multipleQueries.trim()}
                        className="w-full flex items-center justify-center gap-2 p-3 bg-secondary-gradient text-white rounded-lg font-medium shadow-lg shadow-accent-pink/20 hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none transition-all"
                    >
                        <Play size={16} fill="currentColor" />
                        Start Multiple Queries
                    </button>
                </div>
            </div>
        </section>
    );
}
