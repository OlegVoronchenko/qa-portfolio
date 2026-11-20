import { useId, useState } from 'react'
import { ChevronDown, HelpCircle, Lightbulb, Layers, Scale, Sparkles } from 'lucide-react'
import { HOW_I_THINK_ARTICLES } from '../data/howIThink'
import { prefersReducedMotion } from '../utils/motion'

const ICONS = { Layers, Scale, Sparkles }

function Comparison({ comparison }) {
  if (!comparison) return null
  return (
    <div className="mt-3 mb-2">
      <div className="grid sm:grid-cols-2 gap-3">
        <div className="bg-dark-800/60 border border-dark-600 rounded-xl p-4">
          <p className="text-xs font-mono text-accent mb-1.5">{comparison.left.label}</p>
          <p className="text-sm text-slate-400 leading-relaxed">{comparison.left.body}</p>
        </div>
        <div className="bg-dark-800/60 border border-dark-600 rounded-xl p-4">
          <p className="text-xs font-mono text-accent mb-1.5">{comparison.right.label}</p>
          <p className="text-sm text-slate-400 leading-relaxed">{comparison.right.body}</p>
        </div>
      </div>
      {comparison.note && (
        <p className="text-xs text-slate-600 italic mt-2">{comparison.note}</p>
      )}
    </div>
  )
}

function ArticleCard({ article }) {
  const [expanded, setExpanded] = useState(false)
  const contentId = useId()
  const Icon = ICONS[article.icon] || Lightbulb
  const revealClass = expanded
    ? prefersReducedMotion() ? '' : 'animate-fade-in'
    : 'hidden'

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
          {article.category}
        </span>
      </div>

      <h3 data-testid="how-i-think-title" className="text-lg sm:text-xl font-bold mb-3">
        {article.title}
      </h3>

      <p className="flex items-start gap-2 text-sm text-slate-300 italic mb-3 max-w-2xl">
        <HelpCircle size={15} className="text-accent/70 mt-0.5 flex-shrink-0" aria-hidden="true" />
        <span>{article.question}</span>
      </p>

      <p className="flex items-start gap-2 text-sm text-slate-500 mb-4 max-w-2xl">
        <Lightbulb size={15} className="text-accent/70 mt-0.5 flex-shrink-0" aria-hidden="true" />
        <span>{article.insight}</span>
      </p>

      <button
        type="button"
        onClick={() => setExpanded((e) => !e)}
        aria-expanded={expanded}
        aria-controls={contentId}
        className="flex items-center gap-1.5 text-xs font-mono text-accent hover:text-accent-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/60 focus-visible:ring-offset-2 focus-visible:ring-offset-dark-700 rounded transition-colors"
      >
        <ChevronDown
          size={14}
          aria-hidden="true"
          className={`transition-transform ${expanded ? 'rotate-180' : ''}`}
        />
        {expanded ? 'Collapse' : 'Explore Idea'}
      </button>

      <div
        id={contentId}
        data-testid="how-i-think-expanded"
        className={`mt-5 pt-5 border-t border-dark-600/70 max-w-2xl ${revealClass}`}
      >
        {article.sections.map((s) => (
          <div key={s.heading} className="mb-5 last:mb-0">
            <h4 className="text-[11px] font-mono font-semibold text-accent tracking-wider uppercase mb-2">
              {s.heading}
            </h4>
            {s.body.map((p, i) => (
              <p key={i} className="text-sm text-slate-300 leading-relaxed mb-2 last:mb-0">
                {p}
              </p>
            ))}
            {s.formula && (
              <div className="my-3 px-4 py-3 bg-dark-800/80 border border-accent/20 rounded-lg font-mono text-sm sm:text-base text-accent text-center">
                {s.formula}
              </div>
            )}
            {s.formulaNote && (
              <p className="text-xs text-slate-600 italic mb-2">{s.formulaNote}</p>
            )}
            <Comparison comparison={s.comparison} />
          </div>
        ))}
      </div>
    </article>
  )
}

export default function HowIThink() {
  return (
    <section
      id="how-i-think"
      data-testid="how-i-think-section"
      // scroll-mt-16 matches the fixed Navbar's height (h-16 = 64px) so an
      // anchor jump / scrollIntoView lands below it instead of under it.
      className="py-20 px-4 sm:px-6 max-w-6xl mx-auto scroll-mt-16"
    >
      <h2 className="font-mono text-2xl sm:text-3xl font-bold mb-2">
        <span className="text-accent">#</span> How I Think
      </h2>
      <p className="text-slate-400 text-sm sm:text-base mb-1 max-w-2xl">
        Engineering ideas, practical models, and the decisions behind reliable systems.
      </p>
      <p className="text-slate-500 text-sm sm:text-base mb-10 max-w-2xl">
        Three short explorations of automation architecture, release risk, and AI-assisted engineering.
      </p>

      <div className="space-y-5">
        {HOW_I_THINK_ARTICLES.map((article) => (
          <ArticleCard key={article.id} article={article} />
        ))}
      </div>
    </section>
  )
}
