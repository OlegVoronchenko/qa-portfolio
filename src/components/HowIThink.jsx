import { useId, useState } from 'react'
import { ChevronDown, Layers, Scale, Sparkles } from 'lucide-react'
import { HOW_I_THINK_ARTICLES } from '../data/howIThink'
import { HOW_I_THINK_EXPERIMENTS } from '../data/howIThinkExperiments'
import { prefersReducedMotion } from '../utils/motion'
import CoverageExperiment from './experiments/CoverageExperiment'
import ReleaseRiskExperiment from './experiments/ReleaseRiskExperiment'
import AIVerificationExperiment from './experiments/AIVerificationExperiment'

const ICONS = { Layers, Scale, Sparkles }

const EXPERIMENT_COMPONENTS = {
  'automation-architecture': CoverageExperiment,
  'release-risk': ReleaseRiskExperiment,
  'ai-verification': AIVerificationExperiment,
}

function Block({ block }) {
  switch (block.type) {
    case 'formula':
      return (
        <div className="my-3 px-4 py-3 bg-dark-800/80 border border-accent/20 rounded-lg font-mono text-sm sm:text-base text-accent text-center">
          {block.text}
        </div>
      )
    case 'quote':
      return (
        <p className="text-sm text-slate-300 italic border-l-2 border-accent/40 pl-3 my-3">
          &ldquo;{block.text}&rdquo;
        </p>
      )
    case 'choices':
      return (
        <ul className="my-3 space-y-1.5">
          {block.items.map((item) => (
            <li key={item} className="text-sm text-slate-300 font-mono">
              {item}
            </li>
          ))}
        </ul>
      )
    case 'list':
      return (
        <ul className="my-3 space-y-1.5 list-disc list-inside marker:text-accent">
          {block.items.map((item) => (
            <li key={item} className="text-sm text-slate-300 leading-relaxed">
              {item}
            </li>
          ))}
        </ul>
      )
    case 'code':
      return (
        <div className="my-3">
          {block.label && (
            <p className="text-[11px] font-mono text-slate-500 uppercase tracking-wider mb-1.5">
              {block.label}
            </p>
          )}
          <pre className="px-3 py-2.5 bg-dark-900/80 border border-dark-600/50 rounded-lg text-[12px] sm:text-sm leading-relaxed text-accent/90 font-mono overflow-x-auto">
            {block.snippet}
          </pre>
        </div>
      )
    case 'p':
    default:
      return <p className="text-sm text-slate-300 leading-relaxed mb-3 last:mb-0">{block.text}</p>
  }
}

function ArticleCard({ article, isExpanded, onToggle }) {
  const contentId = useId()
  const Icon = ICONS[article.icon] || Layers
  const ExperimentComponent = EXPERIMENT_COMPONENTS[article.id]
  const experiment = HOW_I_THINK_EXPERIMENTS[article.id]
  const revealClass = isExpanded
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

      <p className="text-sm text-slate-300 italic mb-2 max-w-2xl">{article.excerpt}</p>
      <p className="text-sm text-slate-500 mb-4 max-w-2xl">{article.description}</p>

      <button
        type="button"
        data-testid="how-i-think-toggle"
        onClick={onToggle}
        aria-expanded={isExpanded}
        aria-controls={contentId}
        className="flex items-center gap-1.5 text-xs font-mono text-accent hover:text-accent-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/60 focus-visible:ring-offset-2 focus-visible:ring-offset-dark-700 rounded transition-colors"
      >
        <ChevronDown
          size={14}
          aria-hidden="true"
          className={`transition-transform ${isExpanded ? 'rotate-180' : ''}`}
        />
        {isExpanded ? 'Collapse' : 'Explore Idea'}
      </button>

      <div
        id={contentId}
        data-testid="how-i-think-expanded"
        className={`mt-5 pt-5 border-t border-dark-600/70 max-w-2xl ${revealClass}`}
      >
        <div className="mb-5">
          {article.opening.map((line, i) => (
            <p key={i} className="text-sm sm:text-base text-slate-200 leading-relaxed mb-3 last:mb-0">
              {line}
            </p>
          ))}
        </div>

        {article.sections.map((section) => (
          <div key={section.heading} className="mb-5 last:mb-0">
            <h4 className="text-[11px] font-mono font-semibold text-accent tracking-wider uppercase mb-2">
              {section.heading}
            </h4>
            {section.blocks.map((block, i) => (
              <Block key={i} block={block} />
            ))}
          </div>
        ))}

        {ExperimentComponent && experiment && (
          <div className="mt-6">
            <h4 className="text-[11px] font-mono font-semibold text-slate-500 tracking-wider uppercase mb-2">
              Try it yourself
            </h4>
            <ExperimentComponent experiment={experiment} />
          </div>
        )}
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
      <p className="text-slate-400 text-sm sm:text-base mb-1 max-w-2xl">
        Engineering problems worth thinking about.
      </p>
      <p className="text-slate-500 text-sm sm:text-base mb-2 max-w-2xl">
        Three short explorations of test architecture, release decisions, and AI-assisted engineering.
      </p>
      <p className="text-slate-600 text-xs italic mb-10 max-w-2xl">
        Illustrative scenarios, not accounts of specific projects.
      </p>

      <div className="space-y-5">
        {HOW_I_THINK_ARTICLES.map((article) => (
          <ArticleCard
            key={article.id}
            article={article}
            isExpanded={expandedId === article.id}
            onToggle={() => toggle(article.id)}
          />
        ))}
      </div>
    </section>
  )
}
