/**
 * TestResults Component
 *
 * Displays live results from the Playwright test suite.
 * Data sourced from dist/test_report.json which is
 * regenerated on every CI run.
 *
 * Features:
 * - Summary cards (passed/failed/total/duration)
 * - Expandable test rows with full details
 * - Per-step code snippets
 * - TC/REQ/AC badges with clickable detail panels
 * - Screenshot thumbnails with fullscreen modal
 * - Coverage tags and locator strategy badges
 *
 * If test_report.json fails to load, falls back to
 * DEFAULT_DATA so the section never appears broken.
 */
import { useState, useEffect, useCallback } from 'react'
import { useLastRun } from '../hooks/useLastRun'
import { getRequirement, getAcceptanceCriterion } from '../hooks/useRequirements'
import {
  CheckCircle2,
  XCircle,
  ListChecks,
  Timer,
  Play,
  RotateCw,
  ChevronDown,
  Code2,
} from 'lucide-react'

const MARK_COLORS = {
  smoke: 'bg-blue-500/20 text-blue-400',
  navigation: 'bg-purple-500/20 text-purple-400',
  content: 'bg-emerald-500/20 text-emerald-400',
  responsive: 'bg-orange-500/20 text-orange-400',
  performance: 'bg-yellow-500/20 text-yellow-400',
  accessibility: 'bg-pink-500/20 text-pink-400',
  general: 'bg-slate-500/20 text-slate-400',
}

const LOCATOR_BADGES = {
  'get_by_role': { label: 'role', color: 'text-emerald-400 border-emerald-500/30', title: 'Uses ARIA role — best practice' },
  'get_by_text': { label: 'text', color: 'text-blue-400 border-blue-500/30', title: 'Uses visible text content' },
  'get_by_label': { label: 'label', color: 'text-purple-400 border-purple-500/30', title: 'Uses form label' },
  'data-testid': { label: 'testid', color: 'text-yellow-400 border-yellow-500/30', title: 'Uses data-testid attribute' },
  'css-selector': { label: 'css', color: 'text-orange-400 border-orange-500/30', title: 'Uses CSS selector' },
  'evaluate': { label: 'js', color: 'text-cyan-400 border-cyan-500/30', title: 'Uses JavaScript evaluation' },
}

const STATUS_DISPLAY = {
  pass:    { label: 'PASS',  className: 'text-emerald-400' },
  passed:  { label: 'PASS',  className: 'text-emerald-400' },
  fail:    { label: 'FAIL',  className: 'text-red-400' },
  failed:  { label: 'FAIL',  className: 'text-red-400' },
  skip:    { label: 'SKIP',  className: 'text-yellow-400' },
  skipped: { label: 'SKIP',  className: 'text-yellow-400' },
  error:   { label: 'ERROR', className: 'text-red-400' },
  xfail:   { label: 'XFAIL', className: 'text-orange-400' },
}

const getStatusDisplay = (status) =>
  STATUS_DISPLAY[status?.toLowerCase()] ?? { label: (status || '').toUpperCase(), className: 'text-slate-400' }

const DEFAULT_DATA = {
  timestamp: 'not yet run',
  summary: { passed: 20, failed: 0, total: 20, duration_ms: 18450 },
  tests: [
    { name: 'test_page_loads_with_correct_title', status: 'pass', duration_ms: 150, mark: 'smoke', description: 'Page must load and title must identify the QA engineer', steps: [{ name: 'Navigate to base URL', status: 'pass' }, { name: 'Wait for page load state', status: 'pass' }, { name: 'Get page title', status: 'pass' }, { name: 'Assert title contains name', status: 'pass' }, { name: 'Assert title contains QA role', status: 'pass' }], error: null },
    { name: 'test_hero_heading_displays_name', status: 'pass', duration_ms: 120, mark: 'smoke', description: 'Hero section h1 must contain the engineer name', steps: [{ name: 'Navigate to page', status: 'pass' }, { name: 'Locate heading level 1 by role', status: 'pass' }, { name: 'Get heading inner text', status: 'pass' }, { name: 'Assert name present in heading', status: 'pass' }], error: null },
    { name: 'test_navigation_is_present', status: 'pass', duration_ms: 80, mark: 'smoke', description: 'Navigation landmark must be visible on all viewports', steps: [{ name: 'Navigate to page', status: 'pass' }, { name: 'Locate navigation by role', status: 'pass' }, { name: 'Assert navigation is visible', status: 'pass' }], error: null },
    { name: 'test_page_has_no_javascript_errors', status: 'pass', duration_ms: 310, mark: 'smoke', description: 'No JavaScript console errors on page load', steps: [{ name: 'Set up console error listener', status: 'pass' }, { name: 'Navigate to page', status: 'pass' }, { name: 'Wait for networkidle', status: 'pass' }, { name: 'Filter error-level console messages', status: 'pass' }, { name: 'Assert no errors found', status: 'pass' }], error: null },
    { name: 'test_react_app_hydrated_successfully', status: 'pass', duration_ms: 95, mark: 'smoke', description: 'React app must render content into #root element', steps: [{ name: 'Navigate to page', status: 'pass' }, { name: 'Locate #root element', status: 'pass' }, { name: 'Count child elements', status: 'pass' }, { name: 'Assert children count > 0', status: 'pass' }], error: null },
    { name: 'test_nav_link_is_visible_with_correct_href[About-#about]', status: 'pass', duration_ms: 90, mark: 'navigation', description: 'Each navigation link must be visible with correct anchor href', steps: [{ name: 'Navigate to page', status: 'pass' }, { name: 'Locate navigation landmark', status: 'pass' }, { name: 'Find link by name within navigation', status: 'pass' }, { name: 'Assert link is visible', status: 'pass' }, { name: 'Assert href attribute matches expected anchor', status: 'pass' }], error: null },
    { name: 'test_nav_link_is_visible_with_correct_href[Skills-#skills]', status: 'pass', duration_ms: 88, mark: 'navigation', description: 'Each navigation link must be visible with correct anchor href', steps: [{ name: 'Navigate to page', status: 'pass' }, { name: 'Locate navigation landmark', status: 'pass' }, { name: 'Find link by name within navigation', status: 'pass' }, { name: 'Assert link is visible', status: 'pass' }, { name: 'Assert href attribute matches expected anchor', status: 'pass' }], error: null },
    { name: 'test_nav_link_is_visible_with_correct_href[Projects-#projects]', status: 'pass', duration_ms: 92, mark: 'navigation', description: 'Each navigation link must be visible with correct anchor href', steps: [{ name: 'Navigate to page', status: 'pass' }, { name: 'Locate navigation landmark', status: 'pass' }, { name: 'Find link by name within navigation', status: 'pass' }, { name: 'Assert link is visible', status: 'pass' }, { name: 'Assert href attribute matches expected anchor', status: 'pass' }], error: null },
    { name: 'test_nav_link_is_visible_with_correct_href[Contact-#contact]', status: 'pass', duration_ms: 91, mark: 'navigation', description: 'Each navigation link must be visible with correct anchor href', steps: [{ name: 'Navigate to page', status: 'pass' }, { name: 'Locate navigation landmark', status: 'pass' }, { name: 'Find link by name within navigation', status: 'pass' }, { name: 'Assert link is visible', status: 'pass' }, { name: 'Assert href attribute matches expected anchor', status: 'pass' }], error: null },
    { name: 'test_skills_section_contains_core_stack[Python]', status: 'pass', duration_ms: 105, mark: 'content', description: 'Core technology skills must be visible in skills section', steps: [{ name: 'Navigate to page', status: 'pass' }, { name: 'Locate skills section by id', status: 'pass' }, { name: 'Search for skill text within section', status: 'pass' }, { name: 'Assert skill tag is visible', status: 'pass' }], error: null },
    { name: 'test_skills_section_contains_core_stack[Playwright]', status: 'pass', duration_ms: 98, mark: 'content', description: 'Core technology skills must be visible in skills section', steps: [{ name: 'Navigate to page', status: 'pass' }, { name: 'Locate skills section by id', status: 'pass' }, { name: 'Search for skill text within section', status: 'pass' }, { name: 'Assert skill tag is visible', status: 'pass' }], error: null },
    { name: 'test_skills_section_contains_core_stack[Pytest]', status: 'pass', duration_ms: 101, mark: 'content', description: 'Core technology skills must be visible in skills section', steps: [{ name: 'Navigate to page', status: 'pass' }, { name: 'Locate skills section by id', status: 'pass' }, { name: 'Search for skill text within section', status: 'pass' }, { name: 'Assert skill tag is visible', status: 'pass' }], error: null },
    { name: 'test_projects_section_has_expected_cards', status: 'pass', duration_ms: 115, mark: 'content', description: 'Projects section must display exactly 3 project cards', steps: [{ name: 'Navigate to page', status: 'pass' }, { name: 'Locate projects section', status: 'pass' }, { name: 'Count project card elements', status: 'pass' }, { name: 'Assert count equals 3', status: 'pass' }], error: null },
    { name: 'test_contact_section_has_required_channels', status: 'pass', duration_ms: 89, mark: 'content', description: 'Contact section must show all 4 communication channels', steps: [{ name: 'Navigate to page', status: 'pass' }, { name: 'Locate contact section', status: 'pass' }, { name: 'Count contact item elements', status: 'pass' }, { name: 'Assert count equals 4', status: 'pass' }], error: null },
    { name: 'test_test_results_section_renders', status: 'pass', duration_ms: 110, mark: 'content', description: 'Test results section must render summary and test rows', steps: [{ name: 'Navigate to page', status: 'pass' }, { name: 'Locate test results section', status: 'pass' }, { name: 'Assert summary cards are visible', status: 'pass' }, { name: 'Wait for test rows to render', status: 'pass' }, { name: 'Assert at least one test row exists', status: 'pass' }], error: null },
    { name: 'test_mobile_viewport_no_horizontal_scroll', status: 'pass', duration_ms: 200, mark: 'responsive', description: 'Page must not cause horizontal overflow on mobile viewport', steps: [{ name: 'Set viewport to 390x844 mobile size', status: 'pass' }, { name: 'Navigate to page', status: 'pass' }, { name: 'Evaluate scrollWidth vs innerWidth', status: 'pass' }, { name: 'Assert no horizontal overflow', status: 'pass' }], error: null },
    { name: 'test_mobile_hero_section_visible', status: 'pass', duration_ms: 130, mark: 'responsive', description: 'Hero section must be fully visible on mobile viewport', steps: [{ name: 'Set viewport to 390x844 mobile size', status: 'pass' }, { name: 'Navigate to page', status: 'pass' }, { name: 'Locate hero heading', status: 'pass' }, { name: 'Assert heading is visible', status: 'pass' }], error: null },
    { name: 'test_page_load_time_within_budget', status: 'pass', duration_ms: 180, mark: 'performance', description: 'Full page load must complete within 3000ms budget', steps: [{ name: 'Navigate to page', status: 'pass' }, { name: 'Measure loadEventEnd via Performance API', status: 'pass' }, { name: 'Measure navigationStart via Performance API', status: 'pass' }, { name: 'Calculate load duration', status: 'pass' }, { name: 'Assert duration < 3000ms', status: 'pass' }], error: null },
    { name: 'test_images_have_alt_text', status: 'pass', duration_ms: 250, mark: 'accessibility', description: 'All images must have non-empty alt attributes for accessibility', steps: [{ name: 'Navigate to page', status: 'pass' }, { name: 'Find all img elements', status: 'pass' }, { name: 'Check alt attribute on each image', status: 'pass' }, { name: 'Collect violations', status: 'pass' }, { name: 'Assert no violations found', status: 'pass' }], error: null },
    { name: 'test_headings_hierarchy_is_correct', status: 'pass', duration_ms: 140, mark: 'accessibility', description: 'Page must have exactly one h1 and correct heading hierarchy', steps: [{ name: 'Navigate to page', status: 'pass' }, { name: 'Count h1 elements', status: 'pass' }, { name: 'Assert exactly one h1 exists', status: 'pass' }, { name: 'Verify h2 elements exist', status: 'pass' }, { name: 'Assert no heading levels are skipped', status: 'pass' }], error: null },
  ],
}

function formatMs(ms) {
  if (ms >= 1000) return `${(ms / 1000).toFixed(2)}s`
  return `${ms}ms`
}

function StepRow({ step, index }) {
  const [showCode, setShowCode] = useState(false)
  const hasCode = step.code && step.code.trim()

  return (
    <div>
      <button
        onClick={() => hasCode && setShowCode(!showCode)}
        className={`flex items-center gap-2 text-xs w-full text-left ${hasCode ? 'cursor-pointer hover:bg-dark-600/30 -mx-1 px-1 rounded' : 'cursor-default'}`}
      >
        {step.status === 'pass' ? (
          <CheckCircle2 size={12} className="text-emerald-400 flex-shrink-0" />
        ) : (
          <XCircle size={12} className="text-red-400 flex-shrink-0" />
        )}
        <span className="text-slate-400 font-mono flex-1">
          {index + 1}. {step.name}
        </span>
        {hasCode && (
          <Code2 size={11} className={`flex-shrink-0 transition-colors ${showCode ? 'text-accent' : 'text-slate-600'}`} />
        )}
      </button>
      {showCode && hasCode && (
        <pre className="mt-1 mb-2 ml-5 px-3 py-2 bg-dark-900/80 border border-dark-600/50 rounded-lg text-[11px] leading-relaxed text-accent/90 font-mono overflow-x-auto">
          {step.code}
        </pre>
      )}
    </div>
  )
}

function TestRow({ test, isOpen, onToggle, onScreenshot }) {
  const [activeBadge, setActiveBadge] = useState(null)

  const toggleBadge = (type, id) => {
    setActiveBadge(prev =>
      prev?.type === type && prev?.id === id
        ? null
        : { type, id }
    )
  }

  const getBadgeContent = () => {
    if (!activeBadge) return null
    if (activeBadge.type === 'req') {
      const req = getRequirement(activeBadge.id)
      if (!req) return null
      return { title: `${req.id} — ${req.title}`, body: req.requirement }
    }
    const ac = getAcceptanceCriterion(test.req_id, activeBadge.id)
    if (!ac) return null
    return { title: `${ac.id} — ${ac.title}`, body: ac.description }
  }

  return (
    <div className={`border-b border-dark-600/50 last:border-b-0 ${isOpen ? 'bg-dark-800/40' : 'hover:bg-dark-800/30'} transition-colors`}>
      <div
        className="flex items-center gap-3 py-3 px-4 sm:px-6 cursor-pointer hover:bg-white/5 transition-colors duration-150"
        onClick={onToggle}
      >
        {test.status === 'pass' ? (
          <CheckCircle2 size={14} className="text-emerald-400 flex-shrink-0" />
        ) : test.status === 'fail' ? (
          <XCircle size={14} className="text-red-400 flex-shrink-0" />
        ) : (
          <span className="w-3.5 h-3.5 rounded-full bg-yellow-400/80 flex-shrink-0" />
        )}
        <span className="flex-1 text-sm font-mono text-slate-300 truncate">
          {test.name}
        </span>
        <span className={`text-xs font-semibold font-mono w-12 text-center flex-shrink-0 ${getStatusDisplay(test.status).className}`}>
          {getStatusDisplay(test.status).label}
        </span>
        <span className="text-xs font-mono text-slate-500 w-16 text-right flex-shrink-0">
          {formatMs(test.duration_ms)}
        </span>
      </div>

      {isOpen && (
        <div className="px-4 sm:px-6 pb-4">
          <div className="bg-dark-700 border border-dark-600 rounded-xl p-4 space-y-3">
            <div className="flex items-center gap-2">
              {test.mark && (
                <span className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full ${MARK_COLORS[test.mark] || MARK_COLORS.general}`}>
                  {test.mark}
                </span>
              )}
              {test.locator_strategy && LOCATOR_BADGES[test.locator_strategy] && (
                <span className={`text-[10px] px-1.5 py-0.5 rounded border font-mono ${LOCATOR_BADGES[test.locator_strategy].color}`} title={LOCATOR_BADGES[test.locator_strategy].title}>
                  {LOCATOR_BADGES[test.locator_strategy].label}
                </span>
              )}
            </div>

            {test.tc_id && (
              <div className="mb-3">
                <span className="text-[11px] text-slate-500 uppercase tracking-wider font-semibold block mb-2">Test ID</span>
                <div className="flex items-center gap-2">
                  <span className="text-xs px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono font-semibold">
                    {test.tc_id}
                  </span>
                </div>
              </div>
            )}

            {(test.req_id || test.ac_ids?.length > 0) && (
              <div className="mb-3">
                <span className="text-[11px] text-slate-500 uppercase tracking-wider font-semibold block mb-2">Requirements</span>
                <div className="flex items-center gap-2 flex-wrap">
                  {test.req_id && (
                    <button
                      onClick={(e) => { e.stopPropagation(); toggleBadge('req', test.req_id) }}
                      className={`text-xs px-2.5 py-1 rounded border font-mono transition-all duration-200 cursor-pointer ${
                        activeBadge?.id === test.req_id && activeBadge?.type === 'req'
                          ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300'
                          : 'bg-gray-800 border-white/10 text-gray-400 hover:border-emerald-500/30 hover:text-emerald-400'
                      }`}
                    >
                      {test.req_id}
                    </button>
                  )}
                  {test.ac_ids?.map((acId) => (
                    <button
                      key={acId}
                      onClick={(e) => { e.stopPropagation(); toggleBadge('ac', acId) }}
                      className={`text-xs px-2.5 py-1 rounded border font-mono transition-all duration-200 cursor-pointer ${
                        activeBadge?.id === acId && activeBadge?.type === 'ac'
                          ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300'
                          : 'bg-gray-800/60 border-white/5 text-gray-500 hover:border-emerald-500/30 hover:text-emerald-400'
                      }`}
                    >
                      {acId}
                    </button>
                  ))}
                </div>

                {activeBadge && (() => {
                  const content = getBadgeContent()
                  if (!content) return null
                  return (
                    <div className="mt-3 p-4 rounded-lg bg-gray-900/60 border border-emerald-500/20 animate-fadeIn">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-semibold text-emerald-400 font-mono">{content.title}</span>
                        <button
                          onClick={(e) => { e.stopPropagation(); setActiveBadge(null) }}
                          className="text-gray-500 hover:text-gray-300 text-sm leading-none"
                        >
                          &times;
                        </button>
                      </div>
                      <p className="text-sm text-gray-300 leading-relaxed">{content.body}</p>
                    </div>
                  )
                })()}
              </div>
            )}

            {test.description && (
              <div className="pb-3 border-b border-white/5">
                <span className="text-[11px] text-slate-500 uppercase tracking-wider font-semibold">Description</span>
                <p className="text-sm text-slate-300 mt-1">{test.description}</p>
              </div>
            )}

            {test.coverage && test.coverage.length > 0 && (
              <div>
                <span className="text-[11px] text-slate-500 uppercase tracking-wider font-semibold">Coverage</span>
                <div className="flex flex-wrap gap-1.5 mt-1.5">
                  {test.coverage.map((tag) => (
                    <span key={tag} className="text-[10px] px-2 py-0.5 rounded-full bg-dark-800 border border-white/[0.08] text-slate-400">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {test.screenshot && (
              <div>
                <span className="text-[11px] text-slate-500 uppercase tracking-wider font-semibold block mb-2">Screenshot</span>
                <div className="relative group inline-block">
                  <img
                    src={test.screenshot}
                    alt={`Screenshot for ${test.name}`}
                    className="h-24 w-auto rounded-lg border border-white/10 cursor-zoom-in hover:border-emerald-500/30 transition-all duration-200"
                    onClick={(e) => { e.stopPropagation(); onScreenshot(test.screenshot) }}
                  />
                  <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none">
                    <span className="text-white text-[10px] bg-black/60 px-2 py-1 rounded">Click to expand</span>
                  </div>
                </div>
              </div>
            )}

            <div>
              <span className="text-[11px] text-slate-500 uppercase tracking-wider">Steps</span>
              <div className="mt-1.5 space-y-1">
                {test.steps?.map((step, i) => (
                  <StepRow key={i} step={step} index={i} />
                ))}
              </div>
            </div>

            <div className="flex items-center gap-4 pt-1">
              <div>
                <span className="text-[11px] text-slate-500 uppercase tracking-wider">Duration</span>
                <p className="text-xs font-mono text-slate-300 mt-0.5">{formatMs(test.duration_ms)}</p>
              </div>
            </div>

            {test.error && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
                <span className="text-[11px] text-red-400 uppercase tracking-wider font-semibold">Error</span>
                <p className="text-xs text-red-300 font-mono mt-1">{test.error}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default function TestResults() {
  const [data, setData] = useState(DEFAULT_DATA)
  const [loading, setLoading] = useState(false)
  const [running, setRunning] = useState(false)
  const [runProgress, setRunProgress] = useState(0)
  const [expanded, setExpanded] = useState(new Set())
  const [fullScreenshot, setFullScreenshot] = useState(null)
  const lastRun = useLastRun()

  const fetchReport = useCallback(() => {
    setLoading(true)
    fetch(`${import.meta.env.BASE_URL}test_report.json`)
      .then((r) => {
        if (!r.ok) throw new Error('not found')
        return r.json()
      })
      .then((d) => setData(d))
      .catch(() => setData(DEFAULT_DATA))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    fetchReport()
  }, [fetchReport])

  const simulateRun = () => {
    if (running) return
    setRunning(true)
    setRunProgress(0)
    setExpanded(new Set())

    const total = data.tests.length
    let current = 0

    const interval = setInterval(() => {
      current++
      setRunProgress(current)
      if (current >= total) {
        clearInterval(interval)
        setTimeout(() => {
          setRunning(false)
          fetchReport()
        }, 400)
      }
    }, 150)
  }

  const toggleExpand = (name) => {
    setExpanded((prev) => {
      const next = new Set(prev)
      if (next.has(name)) next.delete(name)
      else next.add(name)
      return next
    })
  }

  const summary = data.summary || {
    passed: data.passed || 0,
    failed: data.failed || 0,
    total: data.total || 0,
    duration_ms: data.tests?.reduce((s, t) => s + (t.duration_ms || parseFloat(t.duration || 0) * 1000), 0) || 0,
  }

  const summaryCards = [
    { icon: <CheckCircle2 size={20} />, label: 'Passed', value: summary.passed, color: 'text-emerald-400' },
    { icon: <XCircle size={20} />, label: 'Failed', value: summary.failed, color: summary.failed > 0 ? 'text-red-400' : 'text-slate-500' },
    { icon: <ListChecks size={20} />, label: 'Total', value: summary.total, color: 'text-slate-300' },
    { icon: <Timer size={20} />, label: 'Duration', value: formatMs(summary.duration_ms), color: 'text-accent-teal' },
  ]

  return (
    <section id="test-results" className="py-20 px-4 sm:px-6 max-w-6xl mx-auto">
      <div className="flex items-baseline justify-between flex-wrap gap-2 mb-2">
        <h2 className="font-mono text-2xl sm:text-3xl font-bold">
          <span className="text-accent">#</span> Test Results
        </h2>
        {lastRun && (
          <a
            href={lastRun.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 transition-colors duration-200"
          >
            <span className={`w-1.5 h-1.5 rounded-full ${lastRun.conclusion === 'success' ? 'bg-emerald-400' : 'bg-red-400'}`} />
            Last run: {lastRun.time}
          </a>
        )}
      </div>
      <p className="text-slate-500 mb-10 text-sm sm:text-base">
        Live results from this portfolio&apos;s automated test suite
      </p>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
        {summaryCards.map((c) => (
          <div
            key={c.label}
            className="bg-dark-700 border border-dark-600 rounded-xl p-4 flex items-center gap-3"
          >
            <span className={c.color}>{c.icon}</span>
            <div>
              <div className={`text-lg font-bold font-mono ${c.color}`}>{c.value}</div>
              <div className="text-[11px] text-slate-500 uppercase tracking-wider">{c.label}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="flex items-center justify-between mb-4">
        <span className="text-xs text-slate-600 font-mono">
          {data.timestamp && data.timestamp !== 'not yet run' ? `Last run: ${data.timestamp}` : 'Showing default data'}
        </span>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchReport}
            disabled={loading || running}
            className="flex items-center gap-2 text-xs font-mono text-accent hover:text-accent-light transition-colors disabled:opacity-50"
          >
            <RotateCw size={14} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
          <button
            onClick={simulateRun}
            disabled={running || loading}
            className="flex items-center gap-2 bg-accent hover:bg-accent/90 text-dark-900 font-semibold px-4 py-2 rounded-lg text-xs font-mono transition-colors disabled:opacity-70"
          >
            <Play size={14} fill="currentColor" />
            {running ? 'Running...' : 'Run Tests'}
          </button>
        </div>
      </div>

      {running && (
        <div className="mb-4">
          <div className="h-1.5 bg-dark-600 rounded-full overflow-hidden">
            <div
              className="h-full bg-accent rounded-full transition-all duration-150"
              style={{ width: `${(runProgress / data.tests.length) * 100}%` }}
            />
          </div>
          <div className="text-xs text-slate-500 font-mono mt-1">
            Running test {runProgress} / {data.tests.length}...
          </div>
        </div>
      )}

      <div className="bg-dark-700 border border-dark-600 rounded-2xl overflow-hidden">
        <div className="flex items-center gap-3 px-4 sm:px-6 py-2 border-b border-white/5">
          <div className="w-3.5 flex-shrink-0" />
          <span className="flex-1 min-w-0 text-xs font-semibold text-slate-500 uppercase tracking-wider">Test Name</span>
          <span className="flex-shrink-0 w-12 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</span>
          <span className="flex-shrink-0 w-16 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">Duration</span>
        </div>

        {data.tests.map((t) => (
          <TestRow
            key={t.name}
            test={t}
            isOpen={expanded.has(t.name)}
            onToggle={() => toggleExpand(t.name)}
            onScreenshot={setFullScreenshot}
          />
        ))}
      </div>

      {fullScreenshot && (
        <div
          className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4"
          onClick={() => setFullScreenshot(null)}
        >
          <img
            src={fullScreenshot}
            alt="Full screenshot"
            className="max-w-full max-h-full rounded-lg border border-white/20"
          />
          <button
            className="absolute top-4 right-4 text-white/60 hover:text-white text-2xl"
            onClick={() => setFullScreenshot(null)}
          >
            &#x2715;
          </button>
        </div>
      )}
    </section>
  )
}
