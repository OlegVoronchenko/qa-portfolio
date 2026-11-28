import { useId, useState } from 'react'
import { ArrowRight, ChevronUp, Layers, Scale, Sparkles } from 'lucide-react'
import { HOW_I_THINK_SCENARIOS } from '../data/howIThink'
import { HOW_I_THINK_EXPERIMENTS } from '../data/howIThinkExperiments'
import ScenarioExperiment from './experiments/ScenarioExperiment'

const ICONS = { Layers, Scale, Sparkles }

function ScenarioCard({ scenario, isExpanded, onToggle }) {
  const contentId = useId()
  const Icon = ICONS[scenario.icon] || Layers
  const experiment = HOW_I_THINK_EXPERIMENTS[scenario.id]
  const ToggleIcon = isExpanded ? ChevronUp : ArrowRight

  return (
    <article
      data-testid="how-i-think-card"
      className="bg-dark-700 border border-dark-600 rounded-2xl p-5 sm:p-6"
    >
      <div className="flex items-center gap-2 mb-3">
        <div className="w-9 h-9 rounded-lg bg-accent-dim flex items-center justify-center text-accent flex-shrink-0">
          <Icon size={18} aria-hidden="true" />
        </div>
        <span
          data-testid="how-i-think-category"
          className="text-[11px] font-mono font-semibold text-accent tracking-wider"
        >
          {scenario.category}
        </span>
      </div>

      <h3 data-testid="how-i-think-title" className="text-lg font-bold mb-2">
        {scenario.title}
      </h3>

      <div data-testid="how-i-think-hook" className="text-sm text-slate-400 mb-4">
        {scenario.hook.map((line, i) => (
          <p key={i} className="mb-1 last:mb-0">{line}</p>
        ))}
      </div>

      <button
        type="button"
        data-testid="how-i-think-toggle"
        onClick={onToggle}
        aria-expanded={isExpanded}
        aria-controls={contentId}
        className="flex items-center gap-1.5 text-xs font-mono text-accent hover:text-accent-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/60 focus-visible:ring-offset-2 focus-visible:ring-offset-dark-700 rounded transition-colors"
      >
        {isExpanded ? 'Collapse' : scenario.cta}
        <ToggleIcon size={14} aria-hidden="true" />
      </button>

      <div
        id={contentId}
        data-testid="how-i-think-expanded"
        className={isExpanded ? 'mt-1' : 'hidden'}
      >
        <ScenarioExperiment scenario={experiment} />
      </div>
    </article>
  )
}

export default function HowIThink() {
  const [expandedId, setExpandedId] = useState(null)

  const toggle = (id) => {
    setExpandedId((current) => (current === id ? null : id))
  }

  return (
    <section
      id="how-i-think"
      data-testid="how-i-think-section"
      // scroll-mt-16 matches the fixed Navbar's height (h-16 = 64px) so an
      // anchor jump lands below it instead of under it.
      className="py-20 px-4 sm:px-6 max-w-6xl mx-auto scroll-mt-16"
    >
      <h2 className="font-mono text-2xl sm:text-3xl font-bold mb-2">
        <span className="text-accent">#</span> How I Think
      </h2>
      <p className="text-slate-400 text-sm sm:text-base mb-10 max-w-2xl">
        Good engineering starts with better questions.
      </p>

      <div className="grid gap-5 md:grid-cols-3 items-start">
        {HOW_I_THINK_SCENARIOS.map((scenario) => (
          <ScenarioCard
            key={scenario.id}
            scenario={scenario}
            isExpanded={expandedId === scenario.id}
            onToggle={() => toggle(scenario.id)}
          />
        ))}
      </div>
    </section>
  )
}
