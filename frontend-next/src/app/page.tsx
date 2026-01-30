"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { Header } from "@/components/Header";
import { JobConfig } from "@/components/JobConfig";
import { StatusSection } from "@/components/StatusSection";
import { FileGrid } from "@/components/FileGrid";
import { startScrape, getJobStatus, getFiles, getActiveJob, terminateJob, clearJobStatus, ScrapeJob, GeneratedFile, API_BASE_URL } from "@/lib/api";

export default function Home() {
  const [currentJob, setCurrentJob] = useState<ScrapeJob | null>(null);
  const [files, setFiles] = useState<GeneratedFile[]>([]);
  const [isScraping, setIsScraping] = useState(false);
  const [apiHealth, setApiHealth] = useState<boolean | null>(null);

  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const checkHealth = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      setApiHealth(response.ok);
    } catch {
      setApiHealth(false);
    }
  }, []);

  const loadFiles = useCallback(async () => {
    try {
      const data = await getFiles();
      setFiles(data);
      setApiHealth(true);
    } catch (error) {
      console.error("Failed to load files:", error);
      setApiHealth(false);
    }
  }, []);

  const stopPolling = useCallback(() => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  }, []);

  const pollStatus = useCallback(async (jobId: string) => {
    try {
      const job = await getJobStatus(jobId);
      setCurrentJob(job);
      setApiHealth(true);

      if (job.status === 'completed' || job.status === 'failed' || job.status === 'terminated') {
        stopPolling();
        setIsScraping(false);
        loadFiles();
      }
    } catch (error: any) {
      console.error("Polling error:", error);

      // If job is not found (404), server might have restarted
      if (error.message?.includes('404')) {
        setCurrentJob(prev => prev ? { ...prev, status: 'failed', error: 'Job lost (Server might have restarted)' } : null);
        stopPolling();
        setIsScraping(false);
      } else {
        // For other errors, keep polling but update health
        setApiHealth(false);
      }
    }
  }, [loadFiles, stopPolling]);

  const startPolling = useCallback((jobId: string) => {
    stopPolling();
    pollStatus(jobId); // Initial check
    pollingIntervalRef.current = setInterval(() => pollStatus(jobId), 2000);
  }, [pollStatus, stopPolling]);

  const loadActiveJob = useCallback(async () => {
    try {
      const job = await getActiveJob();
      if (job) {
        setCurrentJob(job);
        if (job.status === 'processing' || job.status === 'queued') {
          setIsScraping(true);
          startPolling(job.job_id);
        }
      }
    } catch (error) {
      console.error("Failed to load active job:", error);
    }
  }, [startPolling]);

  const handleStartScrape = async (queries: string[]) => {
    try {
      setIsScraping(true);
      const data = await startScrape(queries);
      const jobId = data.job_id;

      // Initialize a local processing state if needed or just wait for polling
      setCurrentJob({
        job_id: jobId,
        status: 'queued',
        total_queries: queries.length,
        completed_queries: 0,
        current_query: null,
        queries: queries, // Include the original queries
        results: [],
        started_at: new Date().toISOString()
      });

      startPolling(jobId);
    } catch (error) {
      console.error("Failed to start scrape:", error);
      setIsScraping(false);
      setApiHealth(false);
      alert("Failed to start scraping. Is the backend running?");
    }
  };

  const handleTerminateStatus = async () => {
    // If there's no current job, return
    if (!currentJob) return;

    // If job is already terminated/terminating/completed, return
    if (['terminated', 'terminating', 'completed', 'failed'].includes(currentJob.status)) {
      showNotification('Termination already in progress...', 'info');
      return;
    }

    // Show confirmation dialog before terminating with single-line warning
    if (!confirm('⚠️ WARNING: This will terminate the current job, stop the scraping process, and cancel all remaining pending queries. Completed queries will be preserved. Continue?')) {
      return; // User cancelled
    }

    // If there's an active job, try to terminate it on the backend
    if (currentJob.job_id) {
      try {
        // Update the job status locally immediately for better UX
        setCurrentJob(prev => prev ? { ...prev, status: 'terminating' } : null);
        showNotification('Termination signal sent. Stopping scraper...', 'info');

        const result = await terminateJob(currentJob.job_id);
        console.log('Termination request successful:', result);

        // After sending terminate signal, poll for status changes to 'terminated'
        const pollForTermination = async () => {
          try {
            const job = await getJobStatus(currentJob.job_id);
            setCurrentJob(job);

            // If the job is now terminated, stop polling
            if (job.status === 'terminated' || job.status === 'completed' || job.status === 'failed') {
              stopPolling();
              setIsScraping(false);
              loadFiles();
              showNotification('Scraping job terminated successfully', 'success');
            } else {
              // Continue polling until the status changes
              setTimeout(pollForTermination, 1000);
            }
          } catch (error) {
            console.error("Error polling for termination:", error);
            stopPolling();
            setIsScraping(false);
            showNotification('Error checking job status after termination', 'error');
          }
        };

        // Start polling for status changes
        setTimeout(pollForTermination, 1000);

      } catch (error) {
        console.error('Error terminating job:', error);
        showNotification('Failed to stop scraping: ' + (error as Error).message, 'error');

        // Reset the status back to processing if the termination request failed
        if (currentJob) {
          setCurrentJob(prev => prev ? { ...prev, status: 'processing' } : null);
        }
      }
    }
  };

  const showNotification = (message: string, type: 'info' | 'success' | 'error' = 'info') => {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 16px 24px;
      background: ${type === 'success' ? '#48bb78' : type === 'error' ? '#f56565' : '#4299e1'};
      color: white;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
      z-index: 10000;
      animation: slideIn 0.3s ease;
      font-weight: 500;
      max-width: 300px;
      word-wrap: break-word;
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
      notification.style.animation = 'slideOut 0.3s ease forwards';
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  };

  const handleClearStatus = async () => {
    // Show confirmation dialog before clearing with single-line warning
    if (!confirm('⚠️ WARNING: This will clear the current status, remove all pending queries, and permanently delete this job from the system. Action cannot be undone. Continue?')) {
      return; // User cancelled
    }

    // If there's an active job, clear its status from the backend
    if (currentJob?.job_id) {
      try {
        await clearJobStatus(currentJob.job_id);
      } catch (error) {
        console.error('Failed to clear job status from backend:', error);
        // Still proceed to clear frontend state even if backend call fails
      }
    }

    stopPolling();
    setCurrentJob(null);
    setIsScraping(false);
  };

  useEffect(() => {
    loadFiles();
    loadActiveJob();
    checkHealth(); // Initial health check
    const healthInterval = setInterval(checkHealth, 5000);

    // Add a file refresh interval that runs while scraping
    let fileInterval: NodeJS.Timeout | null = null;
    if (isScraping) {
      fileInterval = setInterval(loadFiles, 5000);
    }

    return () => {
      stopPolling();
      clearInterval(healthInterval);
      if (fileInterval) clearInterval(fileInterval);
    };
  }, [loadFiles, checkHealth, stopPolling, isScraping]);

  return (
    <>
      <style jsx global>{`
        @keyframes slideIn {
          from {
            transform: translateX(400px);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }

        @keyframes slideOut {
          from {
            transform: translateX(0);
            opacity: 1;
          }
          to {
            transform: translateX(400px);
            opacity: 0;
          }
        }
      `}</style>
      <main className="flex flex-col gap-8 pb-20">
        <Header totalFiles={files.length} />

        {apiHealth === false && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-2xl flex items-center justify-center gap-3 animate-pulse">
            <div className="w-2 h-2 rounded-full bg-red-500" />
            <span className="text-sm font-medium">Backend Server Offline - Please start FastAPI on port 8000</span>
          </div>
        )}

        <div className="space-y-12">
          <JobConfig
            onStart={handleStartScrape}
            disabled={isScraping || apiHealth === false}
          />

          <StatusSection
            job={currentJob}
            onClear={handleClearStatus}
            onTerminate={handleTerminateStatus}
          />

          <FileGrid
            files={files}
            onRefresh={loadFiles}
            currentJob={currentJob}
          />
        </div>
      </main>
    </>
  );
}
