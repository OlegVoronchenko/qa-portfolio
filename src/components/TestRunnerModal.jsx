import { useState, useEffect, useRef, useCallback } from 'react'
import {
  X,
  Play,
  Loader2,
  CheckCircle2,
  XCircle,
  ExternalLink,
  RotateCw,
  Eye,
  Clock,
} from 'lucide-react'
import { GitHubActionsService } from '../services/githubActionsService'

const STATES = { IDLE: 'idle', TRIGGERING: 'triggering', IN_PROGRESS: 'in_progress', COMPLETED: 'completed', ERROR: 'error' }

function StepIcon({ status, conclusion }) {
  if (status === 'in_progress') return <Loader2 size={14} className="animate-spin text-accent" />
  if (conclusion === 'success') return <CheckCircle2 size={14} className="text-emerald-400" />
  if (conclusion === 'failure') return <XCircle size={14} className="text-red-400" />
  if (conclusion === 'skipped') return <span className="w-3.5 h-3.5 rounded-full bg-slate-600 inline-block" />
  return <span className="w-3.5 h-3.5 rounded-full border border-slate-600 inline-block" />
}

function formatDuration(seconds) {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return m > 0 ? `${m}m ${s}s` : `${s}s`
}

export default function TestRunnerModal({ isOpen, onClose }) {
  const [state, setState] = useState(STATES.IDLE)
  const [token, setToken] = useState(() => localStorage.getItem('gh_token') || '')
  const [jobs, setJobs] = useState([])
  const [run, setRun] = useState(null)
  const [elapsed, setElapsed] = useState(0)
  const [error, setError] = useState('')
  const [testReport, setTestReport] = useState(null)
  const timerRef = useRef(null)
  const pollRef = useRef(null)

  const saveToken = (val) => {
    setToken(val)
    if (val) localStorage.setItem('gh_token', val)
    else localStorage.removeItem('gh_token')
  }

  const stopTimers = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current)
    if (pollRef.current) clearInterval(pollRef.current)
  }, [])

  useEffect(() => () => stopTimers(), [stopTimers])

  const startPolling = useCallback(
    (service, runId) => {
      setState(STATES.IN_PROGRESS)
      setElapsed(0)
      timerRef.current = setInterval(() => setElapsed((e) => e + 1), 1000)

      pollRef.current = setInterval(async () => {
        try {
          const currentJobs = await service.getRunJobs(runId)
          setJobs(currentJobs)

          const currentRun = await service.getLatestRun()
          if (currentRun && currentRun.id === runId && currentRun.status === 'completed') {
            stopTimers()
            setRun(currentRun)
            setState(STATES.COMPLETED)

            try {
              const base = import.meta.env.BASE_URL
              const res = await fetch(`${base}test_report.json`)
              if (res.ok) setTestReport(await res.json())
            } catch {}
          }
        } catch (err) {
          stopTimers()
          setError(err.message)
          setState(STATES.ERROR)
        }
      }, 3000)
    },
    [stopTimers],
  )

  const handleRun = async () => {
    const service = new GitHubActionsService(token || null)

    if (token) {
      setState(STATES.TRIGGERING)
      try {
        const ok = await service.triggerWorkflow()
        if (!ok) {
          setError('Failed to trigger workflow. Check your token permissions.')
          setState(STATES.ERROR)
          return
        }
        await new Promise((r) => setTimeout(r, 3000))
        const latest = await service.getLatestRun()
        if (latest) {
          setRun(latest)
          startPolling(service, latest.id)
        }
      } catch (err) {
        setError(err.message)
        setState(STATES.ERROR)
      }
    } else {
      setState(STATES.TRIGGERING)
      try {
        const latest = await service.getLatestRun()
        if (latest && latest.status !== 'completed') {
          setRun(latest)
          startPolling(service, latest.id)
        } else if (latest) {
          setRun(latest)
          const currentJobs = await service.getRunJobs(latest.id)
          setJobs(currentJobs)
          setState(STATES.COMPLETED)
        } else {
          setError('No workflow runs found.')
          setState(STATES.ERROR)
        }
      } catch (err) {
        setError(err.message)
        setState(STATES.ERROR)
      }
    }
  }

  const handleRetry = () => {
    stopTimers()
    setJobs([])
    setRun(null)
    setError('')
    setTestReport(null)
    setState(STATES.IDLE)
  }

  if (!isOpen) return null

  const completedSteps = jobs.reduce(
    (n, j) => n + (j.steps?.filter((s) => s.status === 'completed').length || 0),
    0,
  )
  const totalSteps = jobs.reduce((n, j) => n + (j.steps?.length || 0), 0)
  const progressPct = totalSteps > 0 ? Math.round((completedSteps / totalSteps) * 100) : 0

  return (
    <div className="fixed inset-0 z-[60] flex justify-end">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-lg bg-dark-800 border-l border-dark-600 h-full overflow-y-auto animate-slide-in-right">
        {/* Header */}
        <div className="sticky top-0 bg-dark-800 border-b border-dark-600 px-6 py-4 flex items-center justify-between z-10">
          <h2 className="font-mono text-lg font-bold text-accent">Test Runner</h2>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-300 transition-colors">
            <X size={20} />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* IDLE */}
          {state === STATES.IDLE && (
            <>
              <p className="text-sm text-slate-400">
                Run the full test suite via GitHub Actions. Tests verify smoke, navigation,
                content, responsive, performance, and accessibility.
              </p>
              <div>
                <label className="text-xs text-slate-500 uppercase tracking-wider block mb-2">
                  GitHub Token (optional for triggering)
                </label>
                <input
                  type="password"
                  value={token}
                  onChange={(e) => saveToken(e.target.value)}
                  placeholder="ghp_... (without: view results only)"
                  className="w-full bg-dark-700 border border-dark-600 rounded-lg px-4 py-2.5 text-sm text-slate-300 placeholder:text-slate-600 focus:outline-none focus:border-accent/50"
                />
              </div>
              <button
                onClick={handleRun}
                className="w-full flex items-center justify-center gap-2 bg-accent hover:bg-accent/90 text-dark-900 font-semibold py-3 rounded-lg transition-colors"
              >
                <Play size={16} fill="currentColor" />
                {token ? 'Run Tests' : 'View Latest Run'}
              </button>
            </>
          )}

          {/* TRIGGERING */}
          {state === STATES.TRIGGERING && (
            <div className="flex flex-col items-center gap-4 py-12">
              <Loader2 size={32} className="animate-spin text-accent" />
              <p className="text-sm text-slate-400">
                {token ? 'Triggering GitHub Actions workflow...' : 'Fetching latest run...'}
              </p>
            </div>
          )}

          {/* IN_PROGRESS */}
          {state === STATES.IN_PROGRESS && (
            <>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-mono text-sm font-semibold">
                    Run #{run?.run_number} — In Progress
                  </h3>
                  <div className="flex items-center gap-1.5 text-xs text-slate-500 mt-1">
                    <Clock size={12} />
                    {formatDuration(elapsed)}
                  </div>
                </div>
                {run?.html_url && (
                  <a
                    href={run.html_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-accent hover:text-accent-light flex items-center gap-1"
                  >
                    <ExternalLink size={12} />
                    View on GitHub
                  </a>
                )}
              </div>

              {/* Progress bar */}
              <div className="h-1.5 bg-dark-600 rounded-full overflow-hidden">
                <div
                  className="h-full bg-accent rounded-full transition-all duration-300"
                  style={{ width: `${progressPct}%` }}
                />
              </div>

              {/* Jobs */}
              <div className="space-y-3">
                {jobs.map((job) => (
                  <div key={job.id} className="bg-dark-700 border border-dark-600 rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <StepIcon status={job.status} conclusion={job.conclusion} />
                      <span className="text-sm font-semibold">{job.name}</span>
                    </div>
                    <div className="space-y-1 ml-5">
                      {job.steps?.map((step) => (
                        <div key={step.number} className="flex items-center gap-2 text-xs text-slate-500">
                          <StepIcon status={step.status} conclusion={step.conclusion} />
                          <span className={step.conclusion === 'failure' ? 'text-red-400' : ''}>
                            {step.name}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* COMPLETED */}
          {state === STATES.COMPLETED && (
            <>
              <div className="flex items-center gap-3">
                {run?.conclusion === 'success' ? (
                  <CheckCircle2 size={24} className="text-emerald-400" />
                ) : (
                  <XCircle size={24} className="text-red-400" />
                )}
                <div>
                  <h3 className="font-mono text-sm font-semibold">
                    Run #{run?.run_number} —{' '}
                    {run?.conclusion === 'success' ? 'Success' : 'Failed'}
                  </h3>
                  <span className="text-xs text-slate-500">
                    {formatDuration(elapsed)}
                  </span>
                </div>
              </div>

              {/* Test report */}
              {testReport && (
                <div className="bg-dark-700 border border-dark-600 rounded-xl p-4">
                  <div className="grid grid-cols-3 gap-3 mb-3">
                    <div className="text-center">
                      <div className="text-lg font-bold font-mono text-emerald-400">
                        {testReport.passed}
                      </div>
                      <div className="text-[10px] text-slate-500 uppercase">Passed</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold font-mono text-red-400">
                        {testReport.failed}
                      </div>
                      <div className="text-[10px] text-slate-500 uppercase">Failed</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold font-mono text-slate-300">
                        {testReport.total}
                      </div>
                      <div className="text-[10px] text-slate-500 uppercase">Total</div>
                    </div>
                  </div>
                  <div className="space-y-1 max-h-64 overflow-y-auto">
                    {testReport.tests?.map((t) => (
                      <div key={t.name} className="flex items-center gap-2 text-xs">
                        {t.status === 'passed' ? (
                          <CheckCircle2 size={12} className="text-emerald-400 flex-shrink-0" />
                        ) : (
                          <XCircle size={12} className="text-red-400 flex-shrink-0" />
                        )}
                        <span className="font-mono text-slate-400 truncate">{t.name}</span>
                        <span className="text-slate-600 ml-auto flex-shrink-0">{t.duration}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Jobs summary */}
              <div className="space-y-2">
                {jobs.map((job) => (
                  <div key={job.id} className="flex items-center gap-2 text-sm">
                    <StepIcon status={job.status} conclusion={job.conclusion} />
                    <span>{job.name}</span>
                  </div>
                ))}
              </div>

              <div className="flex gap-3">
                {run?.html_url && (
                  <a
                    href={run.html_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 flex items-center justify-center gap-2 border border-accent/40 text-accent py-2.5 rounded-lg text-sm hover:bg-accent-dim transition-colors"
                  >
                    <Eye size={14} />
                    Full Report
                  </a>
                )}
                <button
                  onClick={handleRetry}
                  className="flex-1 flex items-center justify-center gap-2 bg-accent hover:bg-accent/90 text-dark-900 font-semibold py-2.5 rounded-lg text-sm transition-colors"
                >
                  <RotateCw size={14} />
                  Run Again
                </button>
              </div>
            </>
          )}

          {/* ERROR */}
          {state === STATES.ERROR && (
            <div className="space-y-4">
              <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
                <p className="text-sm text-red-400">{error}</p>
              </div>
              <button
                onClick={handleRetry}
                className="w-full flex items-center justify-center gap-2 bg-accent hover:bg-accent/90 text-dark-900 font-semibold py-3 rounded-lg transition-colors"
              >
                <RotateCw size={14} />
                Retry
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
