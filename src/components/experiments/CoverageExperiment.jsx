import { useState } from 'react'
import ExperimentOptions from './ExperimentOptions'
import { prefersReducedMotion } from '../../utils/motion'

function OverlapBar({ label, count, note, segments }) {
  return (
    <div className="flex-1 min-w-[160px]">
      <p className="text-xs font-mono text-slate-400 mb-1.5">
        {label} <span className="text-slate-600">({count})</span>
      </p>
      <div className="flex gap-0.5 h-3 rounded overflow-hidden mb-1.5" aria-hidden="true">
        {segments.map((seg, i) => (
          <div
            key={i}
            className={`flex-1 ${seg === 'shared' ? 'bg-accent/25' : 'bg-accent'}`}
          />
        ))}
      </div>
      <p className="text-[11px] text-slate-600">{note}</p>
    </div>
  )
}

export default function CoverageExperiment({ experiment }) {
  const [selectedId, setSelectedId] = useState(null)
  const revealed = selectedId !== null
  const revealClass = revealed ? (prefersReducedMotion() ? '' : 'animate-fade-in') : 'hidden'

  return (
    <div className="mt-4 bg-dark-800/50 border border-dark-600 rounded-xl p-4 sm:p-5">
      <p className="text-xs text-slate-600 italic mb-4">
        Illustrative figures, not measured data.
      </p>

      <div className="flex flex-col sm:flex-row gap-4 mb-5">
        <OverlapBar {...experiment.illustration.suiteA} />
        <OverlapBar {...experiment.illustration.suiteB} />
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
