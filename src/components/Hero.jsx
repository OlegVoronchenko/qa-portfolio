import { useState, useEffect } from 'react'
import { ArrowRight, Mail, ChevronDown } from 'lucide-react'
import { useProfile } from '../hooks/useProfile'

const EXTRA_ROLES = [
  'Mobile & Web QA Architect',
  'Healthcare QA Specialist',
  'CI/CD Quality Guardian',
]

export default function Hero() {
  const profile = useProfile()
  const roles = [profile.personal.role, ...EXTRA_ROLES]
  const [text, setText] = useState('')
  const [roleIdx, setRoleIdx] = useState(0)
  const [charIdx, setCharIdx] = useState(0)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    const current = roles[roleIdx]
    const speed = deleting ? 35 : 70

    if (!deleting && charIdx === current.length) {
      const t = setTimeout(() => setDeleting(true), 1800)
      return () => clearTimeout(t)
    }
    if (deleting && charIdx === 0) {
      setDeleting(false)
      setRoleIdx((i) => (i + 1) % roles.length)
      return
    }

    const t = setTimeout(() => {
      const next = deleting ? charIdx - 1 : charIdx + 1
      setText(current.substring(0, next))
      setCharIdx(next)
    }, speed)
    return () => clearTimeout(t)
  }, [charIdx, deleting, roleIdx])

  const stats = [
    { value: profile.stats.years_experience, label: 'Years Experience' },
    { value: profile.stats.projects, label: 'Projects Delivered' },
    { value: profile.stats.tests_written, label: 'Tests Written' },
    { value: profile.stats.suite_stability, label: 'Suite Stability' },
  ]

  return (
    <section
      id="hero"
      data-testid="hero-section"
      className="relative min-h-screen flex items-center justify-center overflow-hidden"
    >
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{
          backgroundImage:
            "url('https://images.unsplash.com/photo-1518770660439-4636190af475?w=1920&q=80')",
        }}
      />
      <div className="absolute inset-0 bg-gradient-to-b from-dark-900/[0.93] via-dark-900/[0.88] to-dark-900" />
      <div className="absolute inset-0 dot-grid" />

      <div className="relative z-10 text-center px-4 max-w-3xl mx-auto pt-16">
        <div className="inline-flex items-center gap-2 border border-accent/40 bg-accent-dim rounded-full px-4 py-1.5 mb-8 font-mono text-xs text-accent">
          <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
          {profile.personal.availability}
        </div>

        <p className="text-sm md:text-lg text-slate-400 font-normal mb-1 tracking-wide">
          Hi, I'm
        </p>
        <h1 data-testid="hero-name" className="text-4xl md:text-6xl lg:text-7xl font-extrabold tracking-tight leading-none mb-4">
          <span className="text-white">Oleg </span>
          <span className="bg-gradient-to-r from-accent to-accent-teal bg-clip-text text-transparent">
            Voronchenko
          </span>
        </h1>

        <div data-testid="hero-typewriter" className="font-mono text-lg sm:text-xl text-accent mb-4 h-8">
          {text}
          <span className="animate-typewriter-blink">|</span>
        </div>

        <p className="text-slate-400 text-base sm:text-lg max-w-xl mx-auto mb-8 leading-relaxed">
          15+ years designing and scaling automation across Web, Mobile, API,
          and Embedded systems in healthcare and regulated environments.
        </p>

        <div className="flex flex-wrap gap-3 justify-center mb-14">
          <a
            href="#projects"
            className="flex items-center gap-2 bg-accent hover:bg-accent/90 text-dark-900 font-semibold px-6 py-3 rounded-lg transition-colors"
          >
            View Projects
            <ArrowRight size={16} />
          </a>
          <a
            href="#contact"
            className="flex items-center gap-2 border border-accent/40 text-accent hover:bg-accent-dim font-semibold px-6 py-3 rounded-lg transition-colors"
          >
            <Mail size={16} />
            Get in Touch
          </a>
        </div>

        <div className="flex justify-center gap-8 sm:gap-14">
          {stats.map((s) => (
            <div key={s.label} className="text-center">
              <div className="text-2xl sm:text-3xl font-bold font-mono text-accent">
                {s.value}
              </div>
              <div className="text-xs text-slate-500 uppercase tracking-wider mt-1">
                {s.label}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-14 flex justify-center">
          <ChevronDown size={24} className="text-accent/50 animate-bounce-slow" />
        </div>
      </div>
    </section>
  )
}
