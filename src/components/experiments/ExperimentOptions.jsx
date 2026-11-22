import { CheckCircle2 } from 'lucide-react'

/**
 * Shared single-choice control reused by all three How I Think
 * experiments. Plain native <button>s (keyboard- and touch-operable
 * without any custom widget code) with aria-pressed to communicate
 * selection; no radiogroup/roving-tabindex machinery, which would be
 * more ARIA than this simple, non-form choice needs.
 *
 * Re-selectable: picking a different option after the first choice
 * is allowed (not disabled), so a visitor can compare reveals.
 */
export default function ExperimentOptions({ options, selectedId, onSelect, correctId, groupLabel }) {
  const hasSelected = selectedId !== null

  return (
    <div role="group" aria-label={groupLabel} className="flex flex-wrap gap-2">
      {options.map((opt) => {
        const isSelected = selectedId === opt.id
        const isCorrect = hasSelected && correctId && opt.id === correctId

        return (
          <button
            key={opt.id}
            type="button"
            data-testid="experiment-option"
            onClick={() => onSelect(opt.id)}
            aria-pressed={isSelected}
            className={`flex items-center gap-1.5 text-sm px-3 py-2 rounded-lg border text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/60 focus-visible:ring-offset-2 focus-visible:ring-offset-dark-700 ${
              isSelected
                ? 'bg-accent-dim border-accent text-accent'
                : 'bg-dark-800/60 border-dark-600 text-slate-300 hover:border-accent/40'
            }`}
          >
            {opt.label}
            {isCorrect && (
              <CheckCircle2 size={14} className="text-accent flex-shrink-0" aria-hidden="true" />
            )}
          </button>
        )
      })}
    </div>
  )
}
