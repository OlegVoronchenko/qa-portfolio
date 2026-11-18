import { useId, useState } from 'react'
import { Briefcase, MapPin, CheckCircle2, ChevronDown } from 'lucide-react'
import { useProfile } from '../hooks/useProfile'
import { prefersReducedMotion } from '../utils/motion'

// Default number of achievements shown before "Explore My Impact".
// Keeps every card scannable; the rest is one click away, not hidden.
const DEFAULT_VISIBLE_ACHIEVEMENTS = 3

function TimelineEntry({ entry, isCurrent, isLast }) {
  const [expanded, setExpanded] = useState(false)
  const moreId = useId()

  const achievements = entry.achievements || []
  const visible = achievements.slice(0, DEFAULT_VISIBLE_ACHIEVEMENTS)
  const rest = achievements.slice(DEFAULT_VISIBLE_ACHIEVEMENTS)
  const hasMore = rest.length > 0

  const revealClass = expanded
    ? prefersReducedMotion() ? '' : 'animate-fade-in'
    : 'hidden'

  return (
    <div className="flex gap-4 sm:gap-5">
      <div className="flex flex-col items-center flex-shrink-0 w-5 pt-2.5">
        <span
          className={`w-3 h-3 rounded-full border-2 flex-shrink-0 ${
            isCurrent ? 'bg-accent border-accent' : 'bg-dark-800 border-dark-500'
          }`}
        />
        {!isLast && <span className="w-px flex-1 bg-dark-600 mt-1" />}
      </div>

      <article className="flex-1 min-w-0 pb-8">
        <div className="bg-dark-700 border border-dark-600 rounded-2xl p-5 sm:p-6">
          <div className="flex flex-wrap items-start justify-between gap-2 mb-2">
            <div>
              <h3 className="text-base sm:text-lg font-bold">{entry.role}</h3>
              {entry.company && (
                <p className="text-sm text-accent font-mono">{entry.company}</p>
              )}
            </div>
            <div className="text-right flex-shrink-0">
              <span className="text-xs sm:text-sm text-slate-400 font-mono block">
                {entry.period}
              </span>
              {entry.location && (
                <span className="flex items-center justify-end gap-1 text-xs text-slate-600 mt-0.5">
                  <MapPin size={11} />
                  {entry.location}
                </span>
              )}
            </div>
          </div>

          {entry.description && (
            <p className="text-sm text-slate-400 leading-relaxed mb-4">
              {entry.description}
            </p>
          )}

          {visible.length > 0 && (
            <ul className="space-y-2">
              {visible.map((a) => (
                <li key={a} className="flex items-start gap-2 text-sm text-slate-300">
                  <CheckCircle2 size={14} className="text-accent mt-0.5 flex-shrink-0" />
                  <span>{a}</span>
                </li>
              ))}
            </ul>
          )}

          {hasMore && (
            <>
              <ul id={moreId} className={`space-y-2 mt-2 ${revealClass}`}>
                {rest.map((a) => (
                  <li key={a} className="flex items-start gap-2 text-sm text-slate-300">
                    <CheckCircle2 size={14} className="text-accent mt-0.5 flex-shrink-0" />
                    <span>{a}</span>
                  </li>
                ))}
              </ul>

              <button
                type="button"
                onClick={() => setExpanded((e) => !e)}
                aria-expanded={expanded}
                aria-controls={moreId}
                className="mt-3 flex items-center gap-1.5 text-xs font-mono text-accent hover:text-accent-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/60 focus-visible:ring-offset-2 focus-visible:ring-offset-dark-700 rounded transition-colors"
              >
                <ChevronDown
                  size={14}
                  className={`transition-transform ${expanded ? 'rotate-180' : ''}`}
                />
                {expanded ? 'Show Less' : 'Explore My Impact'}
              </button>
            </>
          )}
        </div>
      </article>
    </div>
  )
}

export default function Experience() {
  const profile = useProfile()
  const entries = profile.experience || []

  return (
    <section id="experience" data-testid="experience-section" className="py-20 px-4 sm:px-6 max-w-6xl mx-auto">
      <h2 className="font-mono text-2xl sm:text-3xl font-bold mb-2">
        <span className="text-accent">#</span> Experience &amp; Impact
      </h2>
      <p className="text-slate-500 mb-10 text-sm sm:text-base">
        Automation architecture, technical leadership, and quality engineering
        across healthcare and mission-critical systems
      </p>

      {entries.length > 0 && (
        <div>
          {entries.map((entry, i) => (
            <TimelineEntry
              key={`${entry.company}-${entry.period}`}
              entry={entry}
              isCurrent={i === 0}
              isLast={i === entries.length - 1}
            />
          ))}
        </div>
      )}

      {entries.length === 0 && (
        <div className="flex items-center gap-3 text-slate-500 text-sm">
          <Briefcase size={16} />
          Experience data not available.
        </div>
      )}
    </section>
  )
}
