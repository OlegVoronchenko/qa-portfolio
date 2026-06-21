import { Mail, Github, Linkedin, Send } from 'lucide-react'
import { useProfile } from '../hooks/useProfile'

const iconMap = {
  email: <Mail size={22} />,
  github: <Github size={22} />,
  linkedin: <Linkedin size={22} />,
  telegram: <Send size={22} />,
}

const labelMap = {
  email: 'Email',
  github: 'GitHub',
  linkedin: 'LinkedIn',
  telegram: 'Telegram',
}

function buildHref(key, value) {
  if (key === 'email') return `mailto:${value}`
  if (value.startsWith('http')) return value
  return `https://${value}`
}

function displayValue(key, value) {
  if (key === 'telegram') return `@${value.replace(/.*\//, '').replace('@', '')}`
  return value.replace(/^https?:\/\//, '')
}

export default function Contact() {
  const profile = useProfile()
  const entries = Object.entries(profile.contact).filter(([, v]) => v)

  return (
    <section id="contact" data-testid="contact-section" className="py-20 px-4 sm:px-6 max-w-6xl mx-auto">
      <h2 className="font-mono text-2xl sm:text-3xl font-bold mb-2">
        <span className="text-accent">#</span> Contact
      </h2>
      <p className="text-slate-500 mb-10 text-sm sm:text-base">
        Let's connect and discuss quality engineering
      </p>

      <div className="flex flex-wrap justify-center gap-4">
        {entries.map(([key, value]) => {
          const href = buildHref(key, value)
          return (
            <a
              key={key}
              href={href}
              target={key === 'email' ? undefined : '_blank'}
              rel="noopener noreferrer"
              data-testid="contact-item"
              className="contact-item group bg-dark-700 border border-dark-600 rounded-xl p-5 flex items-center gap-4 hover:border-accent/40 hover:-translate-y-0.5 transition-all duration-200"
            >
              <div className="w-11 h-11 rounded-lg bg-accent-dim flex items-center justify-center text-accent group-hover:bg-accent/20 transition-colors flex-shrink-0">
                {iconMap[key] || <Mail size={22} />}
              </div>
              <div className="min-w-0">
                <div className="text-xs text-slate-500 uppercase tracking-wider mb-0.5">
                  {labelMap[key] || key}
                </div>
                <div className="text-sm text-slate-300 group-hover:text-accent transition-colors truncate">
                  {displayValue(key, value)}
                </div>
              </div>
            </a>
          )
        })}
      </div>
    </section>
  )
}
