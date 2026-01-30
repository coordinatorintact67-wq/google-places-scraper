"use client";

import { LucideIcon } from "lucide-react";

export function Header({ totalFiles }: { totalFiles: number }) {
    return (
        <header className="flex flex-col md:flex-row justify-between items-center mb-12 p-6 bg-bg-card backdrop-blur-xl border border-white/10 rounded-2xl shadow-md">
            <div className="flex items-center gap-4 mb-4 md:mb-0">
                <div className="w-10 h-10 rounded-xl bg-primary-gradient p-[2px]">
                    <div className="w-full h-full bg-bg-primary rounded-[10px] flex items-center justify-center overflow-hidden">
                        <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <rect width="40" height="40" rx="12" fill="url(#gradient1)" />
                            <path d="M20 10L28 16V24L20 30L12 24V16L20 10Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            <circle cx="20" cy="20" r="3" fill="white" />
                            <defs>
                                <linearGradient id="gradient1" x1="0" y1="0" x2="40" y2="40">
                                    <stop offset="0%" stopColor="#667eea" />
                                    <stop offset="100%" stopColor="#764ba2" />
                                </linearGradient>
                            </defs>
                        </svg>
                    </div>
                </div>
                <h1 className="text-3xl font-bold bg-primary-gradient bg-clip-text text-transparent">
                    Google Places Scraper
                </h1>
            </div>
            <div className="flex gap-8 text-right">
                <div className="flex flex-col items-end">
                    <span className="text-[10px] text-text-tertiary uppercase tracking-wider">Total Files</span>
                    <span className="text-2xl font-bold bg-success-gradient bg-clip-text text-transparent">
                        {totalFiles}
                    </span>
                </div>
            </div>
        </header>
    );
}
