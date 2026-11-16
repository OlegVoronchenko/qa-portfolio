import { Briefcase, MapPin, CheckCircle2 } from 'lucide-react'
import { useProfile } from '../hooks/useProfile'

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

      <div className="space-y-5">
        {entries.map((entry) => (
          <article
            key={`${entry.company}-${entry.period}`}
            className="bg-dark-700 border border-dark-600 rounded-2xl p-5 sm:p-6"
          >
            <div className="flex flex-wrap items-start justify-between gap-2 mb-3">
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

            {entry.achievements?.length > 0 && (
              <ul className="space-y-2">
                {entry.achievements.map((a) => (
                  <li key={a} className="flex items-start gap-2 text-sm text-slate-300">
                    <CheckCircle2 size={14} className="text-accent mt-0.5 flex-shrink-0" />
                    <span>{a}</span>
                  </li>
                ))}
              </ul>
            )}
          </article>
        ))}
      </div>

      {entries.length === 0 && (
        <div className="flex items-center gap-3 text-slate-500 text-sm">
          <Briefcase size={16} />
          Experience data not available.
        </div>
      )}
    </section>
  )
}
