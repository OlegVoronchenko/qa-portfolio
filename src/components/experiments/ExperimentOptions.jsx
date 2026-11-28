import { CheckCircle2 } from 'lucide-react'

/**
 * Shared single-choice control reused by all three How I Think
 * scenarios. Plain native <button>s (keyboard- and touch-operable
 * without any custom widget code) with aria-pressed to communicate
 * selection; no radiogroup/roving-tabindex machinery, which would be
 * more ARIA than this simple, non-form choice needs.
 *
 * An option's `detail` doubles as the scenario setup (e.g. "Suite A
 * (1,000 tests)" + what makes it distinct), so the choice itself
 * carries the context instead of a separate block above it.
 *
 * The correctness indicator only renders when `correctId` is passed.
 * Two of the three scenarios are judgment calls with no single right
 * answer, so they never pass `correctId` and never grade a choice.
 *
 * Re-selectable: picking a different option after the first choice
 * is allowed (not disabled), so a visitor can compare reveals.
 */
export default function ExperimentOptions({ options, selectedId, onSelect, correctId, groupLabel }) {
  const hasSelected = selectedId !== null

  return (
    <div role="group" aria-label={groupLabel} className="flex flex-col gap-2">
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
            className={`flex flex-col gap-1 text-left px-3 py-2.5 rounded-lg border transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/60 focus-visible:ring-offset-2 focus-visible:ring-offset-dark-700 ${
              isSelected
                ? 'bg-accent-dim border-accent text-accent'
                : 'bg-dark-800/60 border-dark-600 text-slate-300 hover:border-accent/40'
            }`}
          >
            <span className="flex items-center gap-1.5 text-sm font-medium">
              {opt.label}
              {isCorrect && (
                <CheckCircle2
                  data-testid="experiment-correct-indicator"
                  size={14}
                  className="text-accent flex-shrink-0"
                  aria-hidden="true"
                />
              )}
            </span>
            {opt.detail && (
              <span className="text-xs text-slate-500 leading-snug">{opt.detail}</span>
            )}
          </button>
        )
      })}
    </div>
  )
}
