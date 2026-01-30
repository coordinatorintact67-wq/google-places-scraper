import { useState, useEffect } from "react";
import { Download, AlertCircle, CheckCircle2, Clock, Loader2, Timer } from "lucide-react";
import { ScrapeJob, getDownloadUrl } from "@/lib/api";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

interface StatusSectionProps {
    job: ScrapeJob | null;
    onClear: () => void;
    onTerminate: () => void;
}

export function StatusSection({ job, onClear, onTerminate }: StatusSectionProps) {
    const [elapsedTime, setElapsedTime] = useState<number>(0);

    useEffect(() => {
        let interval: NodeJS.Timeout;

        if (job && (job.status === 'processing' || job.status === 'queued')) {
            const startTime = job.started_at ? new Date(job.started_at).getTime() : Date.now();

            if (!isNaN(startTime)) {
                // Update immediately
                setElapsedTime(Math.floor((Date.now() - startTime) / 1000));

                interval = setInterval(() => {
                    setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
                }, 1000);
            }
        } else if (job && (job.status === 'completed' || job.status === 'failed')) {
            const startTime = job.started_at ? new Date(job.started_at).getTime() : null;
            if (startTime && !isNaN(startTime)) {
                // If we have a completed_at, use it, otherwise use current time as fallback
                const endTime = job.completed_at ? new Date(job.completed_at).getTime() : Date.now();
                setElapsedTime(Math.floor((endTime - startTime) / 1000));
            }
        }

        return () => {
            if (interval) clearInterval(interval);
        };
    }, [job?.job_id, job?.status, job?.started_at, job?.completed_at]);

    const progress = job ? (job.completed_queries / job.total_queries) * 100 : 0;

    const formatTime = (seconds: number) => {
        if (isNaN(seconds) || seconds < 0) return "00:00";
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = Math.floor(seconds % 60);
        return [
            h > 0 ? h : null,
            m.toString().padStart(2, '0'),
            s.toString().padStart(2, '0')
        ].filter(x => x !== null).join(':');
    };

    return (
        <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-bg-card backdrop-blur-xl border border-white/10 rounded-2xl p-6 md:p-8 mb-8 shadow-md"
        >
            <div className="flex justify-between items-center mb-6 pb-4 border-b border-white/10">
                <div className="flex items-center gap-4">
                    <h2 className="text-xl font-semibold flex items-center gap-3">
                        📊 Processing Status
                    </h2>
                    <div className="hidden md:flex items-center gap-2 px-3 py-1 bg-white/5 border border-white/10 rounded-full text-xs font-mono text-text-secondary">
                        <Timer size={14} className="text-accent-purple" />
                        {job ? formatTime(elapsedTime) : '00:00'}
                    </div>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={onClear}
                        className="text-xs font-medium text-text-tertiary hover:text-text-primary px-3 py-1 rounded-md border border-white/5 hover:bg-white/5 transition-all"
                    >
                        Clear
                    </button>
                    <button
                        onClick={onTerminate}
                        disabled={!job || job.status === 'terminated' || job.status === 'completed' || job.status === 'failed'}
                        className={cn(
                            "text-xs font-medium px-3 py-1 rounded-md border border-white/5 transition-all text-text-tertiary hover:text-red-400 hover:bg-red-500/10 disabled:text-text-disabled disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-transparent"
                        )}
                    >
                        Terminate
                    </button>
                </div>
            </div>

            <div className="flex flex-col gap-6">
                {job && job.error && (
                    <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
                        <AlertCircle size={18} />
                        <div>
                            <p className="font-bold uppercase text-[10px] tracking-widest mb-1">Job Error</p>
                            <p>{job.error}</p>
                        </div>
                    </div>
                )}

                {job && (
                    <>
                        <div className="flex justify-between items-center">
                            <div className="flex items-center gap-4">
                                {job.status !== 'terminating' && (
                                    <div className={cn(
                                        "flex items-center gap-2 px-3 py-1 rounded-lg border text-sm font-medium",
                                        job.status === 'completed' && "bg-accent-green/10 border-accent-green/20 text-accent-green",
                                        job.status === 'processing' && "bg-accent-purple/10 border-accent-purple/20 text-accent-purple",
                                        job.status === 'failed' && "bg-red-500/10 border-red-500/20 text-red-400",
                                        job.status === 'queued' && "bg-accent-blue/10 border-accent-blue/20 text-accent-blue",
                                        job.status === 'terminated' && "bg-gray-500/10 border-gray-500/20 text-gray-400"
                                    )}>
                                        <div className={cn(
                                            "w-2 h-2 rounded-full",
                                            job.status === 'completed' && "bg-accent-green",
                                            job.status === 'processing' && "bg-accent-purple animate-pulse",
                                            job.status === 'failed' && "bg-red-500",
                                            job.status === 'queued' && "bg-accent-blue",
                                            job.status === 'terminated' && "bg-gray-500"
                                        )} />
                                        {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                                    </div>
                                )}

                                <div className="md:hidden flex items-center gap-2 px-3 py-1 bg-white/5 border border-white/10 rounded-full text-xs font-mono text-text-secondary">
                                    <Timer size={14} className="text-accent-purple" />
                                    {formatTime(elapsedTime)}
                                </div>
                            </div>

                            <span className="text-sm font-medium text-text-secondary">
                                {job.completed_queries}/{job.total_queries} queries
                            </span>
                        </div>

                        <div className="w-full h-2 bg-bg-secondary rounded-full overflow-hidden">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${progress}%` }}
                                className="h-full bg-primary-gradient rounded-full"
                            />
                        </div>

                        <div className="flex items-center gap-3 p-3 bg-bg-secondary border-l-4 border-accent-purple rounded-r-lg">
                            <span className="text-xs font-semibold text-text-tertiary uppercase tracking-wider">Current Query:</span>
                            <span className="text-sm font-bold text-text-primary truncate">
                                {job.current_query || "-"}
                            </span>
                        </div>
                    </>
                )}

                {/* Completed Queries Section */}
                {job && job.results && job.results.length > 0 && (
                    <div>
                        <div className="text-xs font-semibold text-text-tertiary uppercase tracking-wider mb-2 px-1">
                            Completed ({job.results.length})
                        </div>
                        <div className="flex flex-col gap-3 max-height-[400px] overflow-y-auto pr-2 custom-scrollbar">
                            <AnimatePresence initial={false}>
                                {job.results.slice().reverse().map((result, idx) => (
                                    <motion.div
                                        key={result.query + idx}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        className="flex justify-between items-center p-4 bg-bg-secondary/50 border border-white/5 rounded-xl hover:border-accent-purple/30 group transition-all"
                                    >
                                        <div className="flex flex-col gap-1">
                                            <div className="text-sm font-semibold text-text-primary">{result.query}</div>
                                            <div className="flex items-center gap-2 text-[10px] text-text-tertiary">
                                                {result.error ? (
                                                    <span className="text-red-400 flex items-center gap-1">
                                                        <AlertCircle size={10} />
                                                        Error: {result.error}
                                                    </span>
                                                ) : (
                                                    <>
                                                        <CheckCircle2 size={10} className="text-accent-green" />
                                                        <span className="px-2 py-0.5 rounded-full bg-white/5 border border-white/5 uppercase text-nowrap">
                                                            {result.total_results} results
                                                        </span>
                                                        <span className="px-2 py-0.5 rounded-full bg-white/5 border border-white/5 uppercase text-nowrap">
                                                            {new Date(result.completed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                                                        </span>
                                                    </>
                                                )}
                                            </div>
                                        </div>
                                        {result.csv_file && (
                                            <button
                                                onClick={() => window.open(getDownloadUrl(result.csv_file!), '_blank')}
                                                className="flex items-center gap-2 px-3 py-1.5 bg-bg-tertiary border border-white/10 rounded-lg text-xs font-medium text-text-secondary hover:text-text-primary hover:border-accent-purple/50 transition-all"
                                            >
                                                <Download size={14} />
                                                Download
                                            </button>
                                        )}
                                    </motion.div>
                                ))}
                            </AnimatePresence>
                        </div>
                    </div>
                )}

                {/* Pending Queries Section */}
                {job && job.queries && job.queries.length > 0 &&
                    ['queued', 'processing', 'terminating'].includes(job.status) && (
                        (() => {
                            // Calculate pending queries (those not yet completed or currently processing)
                            const completedCount = job.results ? job.results.length : 0;
                            const currentIndex = job.current_query_index || completedCount;
                            const pendingQueries = job.queries.slice(currentIndex);

                            return pendingQueries.length > 0 && (
                                <div className="flex flex-col gap-3 p-3 bg-bg-secondary border-l-4 border-yellow-500 rounded-lg">
                                    <div className="flex items-center gap-2">
                                        <span className="text-xs font-semibold text-text-tertiary uppercase tracking-wider">Pending Queries ({pendingQueries.length}):</span>
                                    </div>
                                    <div className="flex flex-wrap gap-2">
                                        {pendingQueries.map((query, idx) => (
                                            <span
                                                key={`pending-${idx}`}
                                                className="text-sm font-bold text-text-primary truncate px-3 py-1.5 bg-white/10 rounded-lg border border-white/10"
                                            >
                                                {query}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            );
                        })()
                    )}

                {!job && (
                    <div className="text-center py-10 text-text-tertiary">
                        <p>No active query. Start a new scraping query to see status updates here.</p>
                    </div>
                )}
            </div>
        </motion.section>
    );
}
