import { Mail, Github, Linkedin, Send } from 'lucide-react'

const items = [
  {
    icon: <Mail size={22} />,
    label: 'Email',
    value: 'oleg.v.qa@gmail.com',
    href: 'mailto:oleg.v.qa@gmail.com',
  },
  {
    icon: <Github size={22} />,
    label: 'GitHub',
    value: 'github.com/oleg-v-qa',
    href: 'https://github.com/oleg-v-qa',
  },
  {
    icon: <Linkedin size={22} />,
    label: 'LinkedIn',
    value: 'linkedin.com/in/oleg-v-qa',
    href: 'https://linkedin.com/in/oleg-v-qa',
  },
  {
    icon: <Send size={22} />,
    label: 'Telegram',
    value: '@oleg_v_qa',
    href: 'https://t.me/oleg_v_qa',
  },
]

export default function Contact() {
  return (
    <section id="contact" data-testid="contact-section" className="py-20 px-4 sm:px-6 max-w-6xl mx-auto">
      <h2 className="font-mono text-2xl sm:text-3xl font-bold mb-2">
        <span className="text-accent">#</span> Contact
      </h2>
      <p className="text-slate-500 mb-10 text-sm sm:text-base">
        Let's connect and discuss quality engineering
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-2xl">
        {items.map((item) => (
          <a
            key={item.label}
            href={item.href}
            target={item.href.startsWith('mailto') ? undefined : '_blank'}
            rel="noopener noreferrer"
            data-testid="contact-item"
            className="contact-item group bg-dark-700 border border-dark-600 rounded-xl p-5 flex items-center gap-4 hover:border-accent/40 hover:-translate-y-0.5 transition-all duration-200"
          >
            <div className="w-11 h-11 rounded-lg bg-accent-dim flex items-center justify-center text-accent group-hover:bg-accent/20 transition-colors flex-shrink-0">
              {item.icon}
            </div>
            <div className="min-w-0">
              <div className="text-xs text-slate-500 uppercase tracking-wider mb-0.5">
                {item.label}
              </div>
              <div className="text-sm text-slate-300 group-hover:text-accent transition-colors truncate">
                {item.value}
              </div>
            </div>
          </a>
        ))}
      </div>
    </section>
  )
}
