import { useMemo } from 'react'
import { ArrowRight, Mail, ChevronDown, Download, Linkedin, Github, Briefcase } from 'lucide-react'
import { useProfile } from '../hooks/useProfile'
import { useCv } from '../hooks/useCv'
import { useTypewriter } from '../hooks/useTypewriter'
import { AnimatedStat } from './AnimatedStat'
import { prefersReducedMotion } from '../utils/motion'

// Supporting specialization line, cycled by the typewriter below the
// (permanently static) primary role. These summarize capabilities
// already documented in profile.summary / experience[].achievements
// (framework ownership, mentoring, team leadership, AI-assisted
// engineering practice) — not new claims.
const SUPPORTING_PHRASES = [
  'Senior SDET',
  'QA Architecture',
  'Engineering Leadership',
  'AI-Assisted Engineering',
]

export default function Hero() {
  const profile = useProfile()
  const cv = useCv()
  // Primary role comes from profile.personal.role (single source of
  // truth) rather than being hardcoded here.
  const primaryRole = profile.personal.role

  // Single-shot: types once and stops. Never cycles, never gets
  // replaced by the supporting phrases — the primary job title must
  // always remain visible exactly as typed.
  const roleText = useTypewriter(useMemo(() => [primaryRole], [primaryRole]), { loop: false })

  // Cycling: types, pauses, deletes, moves to the next phrase, loops.
  const supportingText = useTypewriter(SUPPORTING_PHRASES)

  const reducedMotion = prefersReducedMotion()

  const stats = [
    { value: 15, suffix: '+', label: 'Years Experience', duration: 1500 },
    { value: 9, suffix: '+', label: 'Projects Delivered', duration: 1200 },
    { value: 10000, suffix: '+', label: 'Tests Written', duration: 2000 },
    { value: 98, suffix: '%', label: 'Suite Stability', duration: 1800 },
  ]

  return (
    <section
      id="hero"
      data-testid="hero-section"
      className="relative min-h-screen overflow-hidden"
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

      {/*
        Top padding is deliberate, fixed spacing below the fixed navbar
        (h-16 = 64px) rather than a side effect of vertical centering —
        flex-centering alone produced wildly inconsistent gaps across
        viewport heights (measured ~210px on a tall tablet viewport vs
        ~24px on mobile). Values below target ~32px/48px/64px of visible
        gap under the nav at mobile/tablet/desktop widths respectively.
      */}
      <div className="relative z-10 text-center px-4 max-w-3xl mx-auto pt-24 sm:pt-28 lg:pt-32 pb-16">
        <div className="inline-flex items-center gap-2 border border-accent/40 bg-accent-dim rounded-full px-4 py-1.5 mb-8 font-mono text-xs text-accent">
          <span className="w-2 h-2 rounded-full bg-accent animate-pulse" />
          {profile.personal.availability}
        </div>

        <p className="text-sm md:text-lg text-slate-400 font-normal mb-1 tracking-wide">
          Hi, I&rsquo;m
        </p>
        <h1 data-testid="hero-name" className="text-4xl md:text-6xl lg:text-7xl font-extrabold tracking-tight leading-none mb-4">
          <span className="text-white">Oleg </span>
          <span className="bg-gradient-to-r from-accent to-accent-teal bg-clip-text text-transparent">
            Voronchenko
          </span>
        </h1>

        <div data-testid="hero-typewriter" className="font-mono text-base sm:text-xl text-accent mb-1.5 h-7 sm:h-8 overflow-hidden whitespace-nowrap leading-snug px-2">
          {roleText}
          {!reducedMotion && <span className="animate-typewriter-blink">|</span>}
        </div>
        <div
          data-testid="hero-supporting-positioning"
          className={`font-mono text-xs sm:text-sm text-slate-400 mb-4 tracking-wide ${
            reducedMotion ? '' : 'h-5 sm:h-6 overflow-hidden whitespace-nowrap'
          }`}
        >
          {supportingText}
          {!reducedMotion && <span className="animate-typewriter-blink">|</span>}
        </div>

        <p className="text-slate-400 text-base sm:text-lg max-w-xl mx-auto mb-2 leading-relaxed">
          Designing scalable test automation solutions, leading QA teams, and
          improving engineering quality across healthcare, medical devices,
          and mission-critical systems.
        </p>
        <p className="text-slate-500 text-sm max-w-xl mx-auto mb-8 leading-relaxed">
          Combining hands-on engineering, automation architecture, technical
          leadership, and AI-assisted development practices.
        </p>

        <div className="flex flex-wrap gap-3 justify-center mb-6">
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

        <div className="flex flex-wrap items-center justify-center gap-5 mb-14 text-sm">
          <a
            href="#experience"
            className="flex items-center gap-1.5 text-slate-400 hover:text-accent transition-colors"
          >
            <Briefcase size={14} />
            Experience
          </a>
          {cv.filename && (
            <a
              href={`${import.meta.env.BASE_URL}${cv.url}`}
              download={cv.filename}
              className="flex items-center gap-1.5 text-slate-400 hover:text-accent transition-colors"
            >
              <Download size={14} />
              Download CV
            </a>
          )}
          <a
            href={profile.contact.linkedin}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-slate-400 hover:text-accent transition-colors"
          >
            <Linkedin size={14} />
            LinkedIn
          </a>
          <a
            href={profile.contact.github}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-slate-400 hover:text-accent transition-colors"
          >
            <Github size={14} />
            GitHub
          </a>
        </div>

        <div className="flex justify-center gap-8 sm:gap-14">
          {stats.map((s) => (
            <AnimatedStat
              key={s.label}
              value={s.value}
              suffix={s.suffix}
              label={s.label}
              duration={s.duration}
            />
          ))}
        </div>

        <div className="mt-14 flex justify-center">
          <ChevronDown size={24} className="text-accent/50 animate-bounce-slow" />
        </div>
      </div>
    </section>
  )
}
