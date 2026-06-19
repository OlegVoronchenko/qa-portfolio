import { useState } from 'react'
import { Mail, Github, Linkedin } from 'lucide-react'
import { useProfile } from '../hooks/useProfile'

const navLinks = [
  { label: 'About', href: '#about' },
  { label: 'Skills', href: '#skills' },
  { label: 'Projects', href: '#projects' },
  { label: 'Tests', href: '#test-results' },
  { label: 'Contact', href: '#contact' },
]

const BADGE_URL = [
  'https://hits.seeyoufarm.com/api/count/incr/badge.svg',
  '?url=https%3A%2F%2Folegvoronchenko.github.io%2Fqa-portfolio%2F',
  '&count_bg=%2310b981',
  '&title_bg=%23111827',
  '&icon=github.svg',
  '&icon_color=%23FFFFFF',
  '&title=visitors',
  '&edge_flat=true',
].join('')

function VisitorBadge() {
  const [loaded, setLoaded] = useState(false)
  const [error, setError] = useState(false)

  if (error) return null

  return (
    <div className="flex justify-center mt-6 pt-4 border-t border-white/5">
      <img
        src={BADGE_URL}
        alt="Visitor count"
        height={20}
        style={{ height: '20px', display: loaded ? 'block' : 'none' }}
        onLoad={() => setLoaded(true)}
        onError={() => setError(true)}
      />
      {!loaded && !error && (
        <span className="text-xs text-slate-600">loading visitors...</span>
      )}
    </div>
  )
}

export default function Footer() {
  const profile = useProfile()

  const socials = [
    { icon: <Mail size={18} />, href: `mailto:${profile.contact.email}`, label: 'Email' },
    { icon: <Linkedin size={18} />, href: profile.contact.linkedin, label: 'LinkedIn' },
    { icon: <Github size={18} />, href: profile.contact.github, label: 'GitHub' },
  ]

  return (
    <footer className="border-t border-dark-600/50 py-12 px-4 sm:px-6">
      <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-1.5 font-mono text-lg font-bold tracking-tight">
          <span className="text-accent">OV</span>
          <span className="text-slate-500">QA</span>
        </div>

        <div className="flex flex-wrap justify-center gap-4 sm:gap-6">
          {navLinks.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="text-xs text-slate-500 hover:text-accent transition-colors"
            >
              {l.label}
            </a>
          ))}
        </div>

        <div className="flex items-center gap-3">
          {socials.map((s) => (
            <a
              key={s.label}
              href={s.href}
              target={s.href.startsWith('mailto') ? undefined : '_blank'}
              rel="noopener noreferrer"
              aria-label={s.label}
              className="w-9 h-9 rounded-lg bg-dark-700 border border-dark-600 flex items-center justify-center text-slate-500 hover:text-accent hover:border-accent/40 transition-colors"
            >
              {s.icon}
            </a>
          ))}
        </div>
      </div>

      <div className="text-center text-xs text-slate-600 mt-8">
        &copy; {new Date().getFullYear()} {profile.personal.name} — Built with React, tested with Playwright.
      </div>

      <VisitorBadge />
    </footer>
  )
}
