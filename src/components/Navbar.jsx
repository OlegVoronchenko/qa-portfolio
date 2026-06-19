import { useState } from 'react'
import { Menu, X, Play } from 'lucide-react'
import TestRunnerModal from './TestRunnerModal'

const links = [
  { label: 'About', href: '#about' },
  { label: 'Skills', href: '#skills' },
  { label: 'Projects', href: '#projects' },
  { label: 'Tests', href: '#test-results' },
  { label: 'Contact', href: '#contact' },
]

export default function Navbar() {
  const [open, setOpen] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)

  const scrollTo = (href) => {
    setOpen(false)
    document.querySelector(href)?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <>
      <nav className="fixed top-0 inset-x-0 z-50 bg-dark-900/90 backdrop-blur-xl border-b border-dark-600/50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <a href="#" className="flex items-center gap-1.5 font-mono text-lg font-bold tracking-tight">
            <span className="text-accent">OV</span>
            <span className="text-slate-400">QA</span>
          </a>

          <div data-testid="navbar-links" className="nav-links hidden md:flex items-center gap-6">
            {links.map((l) => (
              <a
                key={l.href}
                href={l.href}
                data-testid={`nav-link-${l.href.replace('#', '')}`}
                onClick={(e) => { e.preventDefault(); scrollTo(l.href) }}
                className="text-sm text-slate-400 hover:text-accent transition-colors"
              >
                {l.label}
              </a>
            ))}
            <button
              onClick={() => setModalOpen(true)}
              className="relative ml-2 flex items-center gap-2 bg-accent text-dark-900 px-4 py-2 rounded-lg font-mono text-sm font-semibold hover:bg-accent/90 transition-colors animate-pulse-ring"
            >
              <Play size={14} fill="currentColor" />
              Test Runner
            </button>
          </div>

          <button
            className="md:hidden text-slate-300"
            onClick={() => setOpen(!open)}
            aria-label="Toggle menu"
          >
            {open ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {open && (
          <div className="md:hidden bg-dark-900/98 border-t border-dark-600/50 px-4 py-4 space-y-3">
            {links.map((l) => (
              <a
                key={l.href}
                href={l.href}
                onClick={(e) => { e.preventDefault(); scrollTo(l.href) }}
                className="block text-sm text-slate-400 hover:text-accent py-1"
              >
                {l.label}
              </a>
            ))}
            <button
              onClick={() => { setOpen(false); setModalOpen(true) }}
              className="flex items-center gap-2 bg-accent text-dark-900 px-4 py-2 rounded-lg font-mono text-sm font-semibold w-full justify-center"
            >
              <Play size={14} fill="currentColor" />
              Test Runner
            </button>
          </div>
        )}
      </nav>

      <TestRunnerModal isOpen={modalOpen} onClose={() => setModalOpen(false)} />
    </>
  )
}
