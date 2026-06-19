import { useState } from 'react'
import {
  ChevronDown,
  Search,
  GitBranch,
  Gauge,
  Smartphone,
  Code2,
  TestTube2,
  FlaskConical,
  Globe,
  Container,
  Settings,
  Bug,
  Terminal,
} from 'lucide-react'

const practices = [
  {
    icon: <Search size={20} />,
    title: 'Test Automation',
    desc: 'Web, mobile, API, desktop, and embedded test frameworks with Selenium, Appium, and TestNG across regulated and commercial products.',
  },
  {
    icon: <GitBranch size={20} />,
    title: 'CI/CD Integration',
    desc: 'GitHub Actions, Maven, and Jenkins pipelines with automated regression gates, quality reports, and release readiness checks.',
  },
  {
    icon: <Gauge size={20} />,
    title: 'Framework Architecture',
    desc: 'Designed and scaled automation frameworks that reduced test execution time by 50% and drove suite stability to 98%.',
  },
  {
    icon: <Smartphone size={20} />,
    title: 'Mobile & Cross-Platform',
    desc: 'Android and iOS automation with Appium for Healthcare-critical workflows across devices and OS versions.',
  },
]

const tools = [
  { icon: <Code2 size={20} />, name: 'Java' },
  { icon: <Globe size={20} />, name: 'Selenium' },
  { icon: <Smartphone size={20} />, name: 'Appium' },
  { icon: <Code2 size={20} />, name: 'Python' },
  { icon: <TestTube2 size={20} />, name: 'Playwright' },
  { icon: <FlaskConical size={20} />, name: 'Pytest' },
  { icon: <Terminal size={20} />, name: 'REST API' },
  { icon: <Settings size={20} />, name: 'GitHub Actions' },
]

export default function Skills() {
  const [openIdx, setOpenIdx] = useState(null)

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
      <div className="hidden sm:grid grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
        {practices.map((p) => (
          <div
            key={p.title}
            className="bg-dark-700 border border-dark-600 rounded-xl p-5 hover:border-accent/40 transition-colors group"
          >
            <div className="w-10 h-10 rounded-lg bg-accent-dim flex items-center justify-center text-accent mb-3 group-hover:bg-accent/20 transition-colors">
              {p.icon}
            </div>
            <h4 className="text-sm font-semibold mb-2">{p.title}</h4>
            <p className="text-xs text-slate-500 leading-relaxed">{p.desc}</p>
          </div>
        ))}
      </div>

      {/* Mobile accordion */}
      <div className="sm:hidden space-y-2 mb-12">
        {practices.map((p, i) => (
          <div
            key={p.title}
            className="bg-dark-700 border border-dark-600 rounded-xl overflow-hidden"
          >
            <button
              onClick={() => setOpenIdx(openIdx === i ? null : i)}
              className="w-full flex items-center justify-between p-4 text-left"
            >
              <div className="flex items-center gap-3">
                <span className="text-accent">{p.icon}</span>
                <span className="text-sm font-semibold">{p.title}</span>
              </div>
              <ChevronDown
                size={16}
                className={`text-slate-500 transition-transform ${openIdx === i ? 'rotate-180' : ''}`}
              />
            </button>
            {openIdx === i && (
              <div className="px-4 pb-4">
                <p className="text-xs text-slate-500 leading-relaxed">{p.desc}</p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Tools */}
      <h3 className="font-mono text-sm text-accent mb-4">// Tools & Technologies</h3>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {tools.map((t) => (
          <div
            key={t.name}
            data-testid="skill-tag"
            className="skill-tag bg-dark-700 border border-dark-600 rounded-xl p-4 flex items-center gap-3 hover:border-accent/40 transition-colors group"
          >
            <span className="text-accent group-hover:text-accent-teal transition-colors">
              {t.icon}
            </span>
            <span className="text-sm font-medium">{t.name}</span>
          </div>
        ))}
      </div>
    </section>
  )
}
