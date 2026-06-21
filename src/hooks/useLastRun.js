import { useState, useEffect } from 'react'

const GITHUB_API = 'https://api.github.com/repos/OlegVoronchenko/qa-portfolio/actions/workflows/test-and-deploy.yml/runs?per_page=1&status=completed'

function timeAgo(dateStr) {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins} min ago`
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
  return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
}

export function useLastRun() {
  const [lastRun, setLastRun] = useState(null)

  useEffect(() => {
    fetch(GITHUB_API, {
      headers: { 'Accept': 'application/vnd.github.v3+json' }
    })
      .then(r => r.json())
      .then(data => {
        const run = data.workflow_runs?.[0]
        if (run) {
          setLastRun({
            time: timeAgo(run.updated_at),
            conclusion: run.conclusion,
            url: run.html_url
          })
        }
      })
      .catch(() => {})
  }, [])

  return lastRun
}
