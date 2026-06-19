import { Mail, Github, Linkedin } from 'lucide-react'

const navLinks = [
  { label: 'About', href: '#about' },
  { label: 'Skills', href: '#skills' },
  { label: 'Projects', href: '#projects' },
  { label: 'Tests', href: '#test-results' },
  { label: 'Contact', href: '#contact' },
]

const socials = [
  { icon: <Mail size={18} />, href: 'mailto:oleg.v.qa@gmail.com', label: 'Email' },
  { icon: <Linkedin size={18} />, href: 'https://linkedin.com/in/oleg-v-qa', label: 'LinkedIn' },
  { icon: <Github size={18} />, href: 'https://github.com/oleg-v-qa', label: 'GitHub' },
]

export default function Footer() {
  return (
    <footer className="border-t border-dark-600/50 py-12 px-4 sm:px-6">
      <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
        {/* Logo */}
        <div className="flex items-center gap-1.5 font-mono text-lg font-bold tracking-tight">
          <span className="text-accent">OV</span>
          <span className="text-slate-500">QA</span>
        </div>

        {/* Nav */}
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

        {/* Social icons */}
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
        &copy; 2024 Oleg V. — Built with React, tested with Playwright.
      </div>
    </footer>
  )
}
