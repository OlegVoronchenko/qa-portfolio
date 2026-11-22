import { useState } from 'react'
import ExperimentOptions from './ExperimentOptions'
import { prefersReducedMotion } from '../../utils/motion'

function CodeBlock({ label, snippet }) {
  return (
    <div className="mb-3 last:mb-0">
      {label && (
        <p className="text-[11px] font-mono text-slate-500 uppercase tracking-wider mb-1.5">
          {label}
        </p>
      )}
      <pre className="px-3 py-2.5 bg-dark-900/80 border border-dark-600/50 rounded-lg text-[12px] sm:text-sm leading-relaxed text-accent/90 font-mono overflow-x-auto">
        {snippet}
      </pre>
    </div>
  )
}

export default function AIVerificationExperiment({ experiment }) {
  const [selectedId, setSelectedId] = useState(null)
  const revealed = selectedId !== null
  const revealClass = revealed ? (prefersReducedMotion() ? '' : 'animate-fade-in') : 'hidden'

  return (
    <div className="mt-4 bg-dark-800/50 border border-dark-600 rounded-xl p-4 sm:p-5">
      <p className="text-sm text-slate-300 italic mb-3">&ldquo;{experiment.requirement}&rdquo;</p>

      <CodeBlock label={experiment.code.label} snippet={experiment.code.snippet} />

      <p className="text-sm text-slate-300 mb-3 mt-4">{experiment.prompt}</p>

      <ExperimentOptions
        options={experiment.options}
        selectedId={selectedId}
        onSelect={setSelectedId}
        correctId={experiment.correctOptionId}
        groupLabel={experiment.prompt}
      />

      <div
        data-testid="experiment-reveal"
        className={`mt-4 pt-4 border-t border-dark-600/70 ${revealClass}`}
      >
        <p className="text-sm font-semibold text-accent mb-2">{experiment.reveal.heading}</p>
        {experiment.reveal.body.map((p, i) => (
          <p key={i} className="text-sm text-slate-400 leading-relaxed mb-2">
            {p}
          </p>
        ))}
        <div className="mt-3">
          <CodeBlock
            label={experiment.reveal.correctedCode.label}
            snippet={experiment.reveal.correctedCode.snippet}
          />
          <CodeBlock
            label={experiment.reveal.boundaryCheck.label}
            snippet={experiment.reveal.boundaryCheck.snippet}
          />
        </div>
      </div>
    </div>
  )
}
