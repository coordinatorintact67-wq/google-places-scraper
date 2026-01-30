"use client";

import { FileText, Download, Clock, HardDrive, Trash2 } from "lucide-react";
import { GeneratedFile, getDownloadUrl, ScrapeJob, ScrapeResult, deleteFile, deleteAllCsv } from "@/lib/api";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

interface FileGridProps {
    files: GeneratedFile[];
    onRefresh: () => void;
    currentJob?: ScrapeJob | null;
}

export function FileGrid({ files, onRefresh, currentJob }: FileGridProps) {
    const formatFileSize = (bytes: number) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} min ago`;
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

        return date.toLocaleDateString();
    };

    const handleDelete = async (e: React.MouseEvent, filename: string) => {
        e.stopPropagation();
        if (confirm(`Are you sure you want to delete ${filename}?`)) {
            try {
                await deleteFile(filename);
                onRefresh();
            } catch (error) {
                console.error("Failed to delete file:", error);
                alert("Failed to delete file");
            }
        }
    };

    return (
        <section className="bg-bg-card backdrop-blur-xl border border-white/10 rounded-2xl p-6 md:p-8 shadow-md">
            <div className="flex justify-between items-center mb-8 pb-4 border-b border-white/10">
                <h2 className="text-xl font-semibold flex items-center gap-3">
                    <HardDrive className="text-accent-blue" size={24} />
                    Generated CSV Files
                </h2>
                <div className="flex gap-2">
                    <button
                        onClick={async () => {
                            if (window.confirm("Are you sure you want to delete ALL CSV files? This cannot be undone.")) {
                                try {
                                    await deleteAllCsv();
                                    onRefresh();
                                } catch (error) {
                                    console.error("Failed to delete all CSV files:", error);
                                    alert("Failed to delete all CSV files");
                                }
                            }
                        }}
                        className="flex items-center gap-2 text-xs font-bold text-red-500 hover:text-red-400 uppercase tracking-widest px-4 py-2 rounded-full border border-red-500/20 hover:bg-red-500/5 transition-all"
                    >
                        <Trash2 size={14} />
                        Delete All
                    </button>
                    <button
                        onClick={onRefresh}
                        className="flex items-center gap-2 text-xs font-bold text-accent-blue hover:text-accent-blue/80 uppercase tracking-widest px-4 py-2 rounded-full border border-accent-blue/20 hover:bg-accent-blue/5 transition-all"
                    >
                        <Clock size={14} />
                        Refresh
                    </button>
                </div>
            </div>

            {files.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-20 text-center text-text-tertiary">
                    <div className="w-20 h-20 rounded-3xl bg-white/5 flex items-center justify-center mb-6 border border-white/5">
                        <FileText size={40} className="opacity-20" />
                    </div>
                    <p className="text-lg font-medium text-text-secondary mb-1">No CSV files yet</p>
                    <span className="text-sm">Start a scraping job to generate files</span>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {files.map((file, idx) => {
                        const isThisFileProcessing = file.status === 'processing';

                        return (
                            <motion.div
                                key={file.filename}
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: idx * 0.05 }}
                                className="group flex flex-col gap-4 p-5 bg-bg-secondary/50 border border-white/10 rounded-2xl hover:border-accent-purple/40 hover:shadow-glow-sm transition-all cursor-pointer relative overflow-hidden"
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="w-12 h-12 rounded-xl bg-primary-gradient flex items-center justify-center text-white shadow-lg shadow-accent-purple/20 group-hover:scale-110 transition-transform">
                                            <FileText size={24} />
                                        </div>
                                        {isThisFileProcessing ? (
                                            <div className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-accent-purple/10 border border-accent-purple/20">
                                                <div className="w-1.5 h-1.5 rounded-full bg-accent-purple animate-pulse" />
                                                <span className="text-[10px] font-bold text-accent-purple uppercase tracking-wider">Processing</span>
                                            </div>
                                        ) : (
                                            <div className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-accent-green/10 border border-accent-green/20">
                                                <div className="w-1.5 h-1.5 rounded-full bg-accent-green" />
                                                <span className="text-[10px] font-bold text-accent-green uppercase tracking-wider">Complete</span>
                                            </div>
                                        )}
                                    </div>
                                    <div className="flex gap-2">
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                window.open(getDownloadUrl(file.filename), '_blank');
                                            }}
                                            className="p-2 rounded-lg bg-white/5 border border-white/10 text-text-tertiary hover:text-accent-purple hover:border-accent-purple/50 transition-all"
                                            title="Download CSV"
                                        >
                                            <Download size={18} />
                                        </button>
                                        <button
                                            onClick={(e) => handleDelete(e, file.filename)}
                                            className="p-2 rounded-lg bg-white/5 border border-white/10 text-text-tertiary hover:text-red-500 hover:border-red-500/50 transition-all"
                                            title="Delete CSV"
                                        >
                                            <Trash2 size={18} />
                                        </button>
                                    </div>
                                </div>
                                <div className="flex flex-col gap-1">
                                    <div className="text-sm font-bold text-text-primary line-clamp-1 group-hover:text-accent-purple transition-colors">
                                        {file.filename}
                                    </div>
                                    <div className="flex items-center gap-2 text-[11px] font-medium text-text-tertiary">
                                        <span className="px-2 py-0.5 rounded-full bg-white/5 border border-white/5 uppercase text-nowrap">
                                            {formatFileSize(file.size)}
                                        </span>
                                        <span className="px-2 py-0.5 rounded-full bg-white/5 border border-white/5 uppercase text-nowrap">
                                            {formatDate(file.created)}
                                        </span>
                                    </div>
                                </div>
                                <button
                                    onClick={() => window.open(getDownloadUrl(file.filename), '_blank')}
                                    className="mt-2 w-full flex items-center justify-center gap-2 py-2.5 bg-primary-gradient text-white text-xs font-bold rounded-xl opacity-0 group-hover:opacity-100 transition-all translate-y-2 group-hover:translate-y-0"
                                >
                                    Download CSV
                                </button>
                            </motion.div>
                        );
                    })}
                </div>
            )}
        </section>
    );
}
