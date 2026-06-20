import { User, MapPin, Briefcase, Award, BookOpen, Zap } from 'lucide-react'
import { useProfile } from '../hooks/useProfile'

const facts = [
  {
    icon: <BookOpen size={20} />,
    title: 'Shift-Left Advocate',
    text: 'I integrate testing from day one — catching bugs early saves 10x the cost of fixing them post-release.',
  },
  {
    icon: <Zap size={20} />,
    title: 'Automation-First Mindset',
    text: 'From smoke tests to full regression suites, I build frameworks that run in CI on every commit.',
  },
]

export default function About() {
  const profile = useProfile()
  const tags = profile.skills.automation.slice(0, 5)

  const cert = profile.certifications?.[0]

  return (
    <section id="about" className="py-20 px-4 sm:px-6 max-w-6xl mx-auto">
      <h2 className="font-mono text-2xl sm:text-3xl font-bold mb-2">
        <span className="text-accent">#</span> About Me
      </h2>
      <p className="text-slate-500 mb-10 text-sm sm:text-base">
        {profile.personal.role} passionate about quality and reliability
      </p>

      <div className="grid md:grid-cols-2 gap-8 items-start">
        <div className="relative">
          {cert && (
            <div
              className="absolute -top-4 right-4 z-10 flex items-center gap-2 bg-dark-800 border border-accent/40 rounded-lg px-3 py-2 shadow-lg shadow-accent/5"
              data-testid="cert-badge"
            >
              <Award size={16} className="text-accent" />
              <span className="font-mono text-xs text-accent font-semibold">
                {cert.issuer} — {cert.name.includes('Foundation') ? 'CTFL' : cert.name}
              </span>
            </div>
          )}

          <div className="bg-dark-700 border border-dark-600 rounded-2xl p-6 sm:p-8">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 rounded-full bg-accent-dim border-2 border-accent/30 flex items-center justify-center">
                <User size={28} className="text-accent" />
              </div>
              <div>
                <h3 className="text-lg font-bold">{profile.personal.name}</h3>
                <p className="text-sm text-accent font-mono">{profile.personal.role}</p>
                <div className="flex items-center gap-1 text-xs text-slate-500 mt-1">
                  <MapPin size={12} />
                  {profile.personal.location}
                </div>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 mb-6">
              {tags.map((t) => (
                <span
                  key={t}
                  className="bg-accent-dim text-accent text-xs font-mono px-2.5 py-1 rounded-md"
                >
                  {t}
                </span>
              ))}
            </div>

            <p className="text-slate-400 text-sm leading-relaxed">
              {profile.summary}
            </p>
          </div>
        </div>

        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-bold mb-3">Why Quality Matters</h3>
            <p className="text-slate-400 text-sm leading-relaxed mb-3">
              I've spent 15 years watching the same failure modes repeat across
              different companies and domains: test suites that nobody trusts,
              automation that breaks faster than it's written, and releases that
              go out on hope rather than evidence. That's what I actually work against.
            </p>
            <p className="text-slate-400 text-sm leading-relaxed mb-3">
              I focus on building automation that stays stable — not impressive
              coverage numbers that collapse under the first refactor. In medical
              device software this wasn't a preference, it was a requirement.
              FDA-regulated environments taught me that a flaky test is worse than
              no test — it creates noise, erodes confidence, and eventually gets skipped.
            </p>
            <p className="text-slate-400 text-sm leading-relaxed mb-4">
              The same principle applies everywhere else. Good automation is
              invisible — it runs, it catches what matters, and it gets out of the way.
            </p>
            <div className="flex items-center gap-3">
              <Briefcase size={16} className="text-accent" />
              <span className="text-sm text-slate-400">
                {profile.stats.years_experience} years at {profile.experience[0]?.company} across healthcare and medical domains
              </span>
            </div>
          </div>

          {facts.map((f) => (
            <div
              key={f.title}
              className="bg-dark-700 border border-dark-600 rounded-xl p-5 flex gap-4"
            >
              <div className="w-10 h-10 rounded-lg bg-accent-dim flex items-center justify-center flex-shrink-0 text-accent">
                {f.icon}
              </div>
              <div>
                <h4 className="text-sm font-semibold mb-1">{f.title}</h4>
                <p className="text-xs text-slate-500 leading-relaxed">{f.text}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
