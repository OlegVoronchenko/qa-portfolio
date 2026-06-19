import { GITHUB_CONFIG } from '../config/github'

export class GitHubActionsService {
  constructor(token) {
    this.token = token || null
    this.base = `${GITHUB_CONFIG.apiBase}/repos/${GITHUB_CONFIG.owner}/${GITHUB_CONFIG.repo}`
  }

  headers() {
    const h = { Accept: 'application/vnd.github.v3+json' }
    if (this.token) h.Authorization = `Bearer ${this.token}`
    return h
  }

  async triggerWorkflow() {
    if (!this.token) return false
    const res = await fetch(
      `${this.base}/actions/workflows/${GITHUB_CONFIG.workflowId}/dispatches`,
      {
        method: 'POST',
        headers: { ...this.headers(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ ref: 'main' }),
      },
    )
    return res.status === 204
  }

  async getLatestRun() {
    const res = await fetch(
      `${this.base}/actions/workflows/${GITHUB_CONFIG.workflowId}/runs?per_page=1`,
      { headers: this.headers() },
    )
    if (!res.ok) return null
    const data = await res.json()
    return data.workflow_runs?.[0] || null
  }

  async getRunJobs(runId) {
    const res = await fetch(`${this.base}/actions/runs/${runId}/jobs`, {
      headers: this.headers(),
    })
    if (!res.ok) return []
    const data = await res.json()
    return data.jobs || []
  }

  async pollUntilComplete(runId, onUpdate, intervalMs = 3000) {
    return new Promise((resolve) => {
      const poll = async () => {
        const jobs = await this.getRunJobs(runId)
        onUpdate(jobs)

        const run = await this.getLatestRun()
        if (run && run.id === runId && run.status === 'completed') {
          resolve(run)
          return
        }
        setTimeout(poll, intervalMs)
      }
      poll()
    })
  }
}
