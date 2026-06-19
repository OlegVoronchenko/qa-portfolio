import { useState } from 'react'
import {
  ChevronDown,
  Code2,
  Network,
  Smartphone,
  Zap,
  BarChart2,
  BookOpen,
  Code,
  Bug,
  GitBranch,
  ShieldCheck,
  BarChart,
  Wrench,
} from 'lucide-react'
import { useProfile } from '../hooks/useProfile'

const SECTION_META = {
  automation: {
    label: 'Test Automation',
    icon: Code2,
    description: 'Frameworks & languages',
  },
  api_testing: {
    label: 'API & Integration',
    icon: Network,
    description: 'REST, contract testing',
  },
  mobile: {
    label: 'Mobile Testing',
    icon: Smartphone,
    description: 'iOS, Android automation',
  },
  cicd: {
    label: 'CI/CD & Pipelines',
    icon: Zap,
    description: 'Build & deploy automation',
  },
  reporting: {
    label: 'Test Management',
    icon: BarChart2,
    description: 'Tracking & reporting',
  },
  methodologies: {
    label: 'Methodologies',
    icon: BookOpen,
    description: 'Process & compliance',
  },
}

const CATEGORY_ICONS = {
  'Test Automation': Code,
  'API Testing': Network,
  'Mobile Testing': Smartphone,
  'Bug Tracking': Bug,
  'Version Control': GitBranch,
  'CI/CD': Zap,
  'Reporting': BarChart,
  'Regulated Testing': ShieldCheck,
}

export default function Skills() {
  const profile = useProfile()
  const [openIdx, setOpenIdx] = useState(null)

  const skillEntries = Object.entries(profile.skills || {}).filter(
    ([key]) => SECTION_META[key]
  )

  const tools = profile.tools || []

  return (
    <section id="skills" data-testid="skills-section" className="py-20 px-4 sm:px-6 max-w-6xl mx-auto">
      <h2 className="font-mono text-2xl sm:text-3xl font-bold mb-2">
        <span className="text-accent">#</span> Skills
      </h2>
      <p className="text-slate-500 mb-10 text-sm sm:text-base">
        Technologies and practices I work with daily
      </p>

      {/* QA Practices */}
      <h3 className="font-mono text-sm text-accent mb-4">// QA Practices</h3>

      {/* Desktop grid */}
      <div className="hidden sm:grid grid-cols-2 lg:grid-cols-3 gap-4 mb-12">
        {skillEntries.map(([key, items]) => {
          const meta = SECTION_META[key]
          const Icon = meta.icon
          return (
            <div
              key={key}
              className="bg-dark-700 border border-dark-600 border-l-2 border-l-transparent rounded-xl p-5 hover:border-accent/40 hover:border-l-accent transition-colors group"
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-lg bg-accent-dim flex items-center justify-center text-accent group-hover:bg-accent/20 transition-colors">
                  <Icon size={20} />
                </div>
                <div>
                  <h4 className="text-sm font-semibold">{meta.label}</h4>
                  <span className="text-[11px] text-slate-600">{meta.description} ({items.length})</span>
                </div>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {items.map((item, i) => (
                  <span
                    key={item}
                    data-testid="skill-tag"
                    className={`text-xs font-mono px-2 py-0.5 rounded ${
                      i < 3
                        ? 'bg-accent-dim text-accent'
                        : 'bg-dark-600 text-slate-400'
                    }`}
                  >
                    {item}
                  </span>
                ))}
              </div>
            </div>
          )
        })}
      </div>

      {/* Mobile accordion */}
      <div className="sm:hidden space-y-2 mb-12">
        {skillEntries.map(([key, items], i) => {
          const meta = SECTION_META[key]
          const Icon = meta.icon
          return (
            <div
              key={key}
              className="bg-dark-700 border border-dark-600 rounded-xl overflow-hidden"
            >
              <button
                onClick={() => setOpenIdx(openIdx === i ? null : i)}
                className="w-full flex items-center justify-between p-4 text-left"
              >
                <div className="flex items-center gap-3">
                  <span className="text-accent"><Icon size={20} /></span>
                  <span className="text-sm font-semibold">{meta.label}</span>
                  <span className="text-[11px] text-slate-600">({items.length})</span>
                </div>
                <ChevronDown
                  size={16}
                  className={`text-slate-500 transition-transform ${openIdx === i ? 'rotate-180' : ''}`}
                />
              </button>
              {openIdx === i && (
                <div className="px-4 pb-4">
                  <div className="flex flex-wrap gap-1.5">
                    {items.map((item, j) => (
                      <span
                        key={item}
                        data-testid="skill-tag"
                        className={`text-xs font-mono px-2 py-0.5 rounded ${
                          j < 3
                            ? 'bg-accent-dim text-accent'
                            : 'bg-dark-600 text-slate-400'
                        }`}
                      >
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Tools & Technologies */}
      <h3 className="font-mono text-sm text-accent mb-4">// Tools & Technologies</h3>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {tools.map((t) => {
          const Icon = CATEGORY_ICONS[t.category] || Wrench
          return (
            <div
              key={t.category}
              className="bg-dark-700 border border-dark-600 rounded-xl p-4 hover:border-accent/40 transition-colors group"
            >
              <div className="flex items-center gap-2 mb-3">
                <Icon size={16} className="text-accent group-hover:text-accent-teal transition-colors" />
                <span className="text-xs font-semibold">{t.category}</span>
                <span className="text-[10px] text-slate-600">({t.items.length})</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {t.items.map((item, i) => (
                  <span
                    key={item}
                    data-testid="skill-tag"
                    className={`text-[11px] font-mono px-1.5 py-0.5 rounded ${
                      i < 2
                        ? 'bg-accent-dim text-accent'
                        : 'bg-dark-600 text-slate-400'
                    }`}
                  >
                    {item}
                  </span>
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
