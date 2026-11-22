import { useState } from 'react'
import { Clock } from 'lucide-react'
import ExperimentOptions from './ExperimentOptions'
import { prefersReducedMotion } from '../../utils/motion'

export default function ReleaseRiskExperiment({ experiment }) {
  const [selectedId, setSelectedId] = useState(null)
  const revealed = selectedId !== null
  const revealClass = revealed ? (prefersReducedMotion() ? '' : 'animate-fade-in') : 'hidden'

  return (
    <div className="mt-4 bg-dark-800/50 border border-dark-600 rounded-xl p-4 sm:p-5">
      <p className="flex items-center gap-1.5 text-xs font-mono text-accent mb-4">
        <Clock size={13} aria-hidden="true" />
        {experiment.scenario.timebox}
      </p>

      <div className="grid sm:grid-cols-3 gap-3 mb-5">
        {experiment.scenario.options.map((opt) => (
          <div
            key={opt.id}
            className={`border rounded-lg p-3 ${
              selectedId === opt.id
                ? 'bg-accent-dim border-accent'
                : 'bg-dark-900/40 border-dark-600'
            }`}
          >
            <p className="text-xs font-mono text-slate-300 font-semibold mb-1">{opt.label}</p>
            <p className="text-[11px] text-slate-500 leading-relaxed">{opt.detail}</p>
          </div>
        ))}
      </div>

      <p className="text-sm text-slate-300 mb-3">{experiment.prompt}</p>

      <ExperimentOptions
        options={experiment.options}
        selectedId={selectedId}
        onSelect={setSelectedId}
        groupLabel={experiment.prompt}
      />

      <div
        data-testid="experiment-reveal"
        className={`mt-4 pt-4 border-t border-dark-600/70 ${revealClass}`}
      >
        <p className="text-sm font-semibold text-accent mb-2">{experiment.reveal.heading}</p>
        {experiment.reveal.body.map((p, i) => (
          <p key={i} className="text-sm text-slate-400 leading-relaxed mb-2 last:mb-0">
            {p}
          </p>
        ))}
      </div>
    </div>
  )
}
