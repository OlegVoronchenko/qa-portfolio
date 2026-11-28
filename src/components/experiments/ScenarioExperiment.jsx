import { useState } from 'react'
import { Clock } from 'lucide-react'
import ExperimentOptions from './ExperimentOptions'
import { prefersReducedMotion } from '../../utils/motion'

function IntroBlock({ block }) {
  switch (block.type) {
    case 'quote':
      return (
        <p className="text-sm text-slate-300 italic border-l-2 border-accent/40 pl-3 mb-3">
          &ldquo;{block.text}&rdquo;
        </p>
      )
    case 'code':
      return (
        <div className="mb-3">
          {block.label && (
            <p className="text-[11px] font-mono text-slate-500 uppercase tracking-wider mb-1.5">
              {block.label}
            </p>
          )}
          <pre className="px-3 py-2.5 bg-dark-900/80 border border-dark-600/50 rounded-lg text-[12px] sm:text-sm leading-relaxed text-accent/90 font-mono whitespace-pre-wrap break-words">
            {block.snippet}
          </pre>
        </div>
      )
    case 'p':
    default:
      return (
        <p className="flex items-center gap-1.5 text-xs font-mono text-accent mb-3">
          <Clock size={13} aria-hidden="true" />
          {block.text}
        </p>
      )
  }
}

/**
 * One generic interactive scenario, configured entirely by data
 * (see src/data/howIThinkExperiments.js). All three How I Think
 * scenarios share the same shape now that the long-form article
 * content is gone: an optional short setup, a prompt, three option
 * buttons, and a reveal — so one component renders all three
 * instead of a bespoke component per scenario.
 */
export default function ScenarioExperiment({ scenario }) {
  const [selectedId, setSelectedId] = useState(null)
  const revealed = selectedId !== null
  const revealClass = revealed ? (prefersReducedMotion() ? '' : 'animate-fade-in') : 'hidden'

  return (
    <div className="mt-4 bg-dark-800/50 border border-dark-600 rounded-xl p-4 sm:p-5">
      {scenario.intro?.map((block, i) => (
        <IntroBlock key={i} block={block} />
      ))}

      <p className="text-sm text-slate-300 mb-3">{scenario.prompt}</p>

      <ExperimentOptions
        options={scenario.options}
        selectedId={selectedId}
        onSelect={setSelectedId}
        correctId={scenario.correctOptionId}
        groupLabel={scenario.prompt}
      />

      <div
        data-testid="experiment-reveal"
        className={`mt-4 pt-4 border-t border-dark-600/70 ${revealClass}`}
      >
        {scenario.reveal.body.map((p, i) => (
          <p key={i} className="text-sm text-slate-300 leading-relaxed mb-2 last:mb-0">
            {p}
          </p>
        ))}

        {scenario.reveal.correctedCode && (
          <div className="mt-3 mb-2">
            <p className="text-[11px] font-mono text-slate-500 uppercase tracking-wider mb-1.5">
              {scenario.reveal.correctedCode.label}
            </p>
            <pre className="px-3 py-2.5 bg-dark-900/80 border border-dark-600/50 rounded-lg text-[12px] sm:text-sm leading-relaxed text-accent/90 font-mono whitespace-pre-wrap break-words">
              {scenario.reveal.correctedCode.snippet}
            </pre>
          </div>
        )}

        {scenario.reveal.insight && (
          <div className="mt-3 pt-3 border-t border-dark-600/50">
            {scenario.reveal.insight.map((p, i) => (
              <p key={i} className="text-sm text-slate-400 leading-relaxed mb-2 last:mb-0">
                {p}
              </p>
            ))}
          </div>
        )}

        {scenario.reveal.note && (
          <p className="mt-3 text-xs text-slate-500 italic">{scenario.reveal.note}</p>
        )}
      </div>
    </div>
  )
}
