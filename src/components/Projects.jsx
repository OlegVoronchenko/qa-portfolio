import { ExternalLink, ShoppingCart, Server, Monitor } from 'lucide-react'
import { useProfile } from '../hooks/useProfile'

const iconMap = {
  'E2E Testing': <ShoppingCart size={20} />,
  'API Testing': <Server size={20} />,
  'Live Demo': <Monitor size={20} />,
}

const imageMap = {
  'E2E Testing': 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&q=80',
  'API Testing': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&q=80',
  'Live Demo': 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&q=80',
}

export default function Projects() {
  const profile = useProfile()

  return (
    <section id="projects" data-testid="projects-section" className="py-20 px-4 sm:px-6 max-w-6xl mx-auto">
      <h2 className="font-mono text-2xl sm:text-3xl font-bold mb-2">
        <span className="text-accent">#</span> Projects
      </h2>
      <p className="text-slate-500 mb-10 text-sm sm:text-base">
        Selected test automation projects
      </p>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {profile.projects.map((p) => (
          <div
            key={p.name}
            role="article"
            className="project-card group bg-dark-700 border border-dark-600 rounded-2xl overflow-hidden hover:border-accent/40 hover:-translate-y-1 transition-all duration-300"
          >
            <div className="relative h-44 overflow-hidden">
              <img
                src={imageMap[p.type] || imageMap['Live Demo']}
                alt={`${p.name} project screenshot`}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-dark-700 via-dark-700/40 to-transparent" />
              <span className="absolute top-3 left-3 bg-dark-900/80 backdrop-blur text-accent text-[11px] font-mono font-semibold px-2.5 py-1 rounded-md border border-accent/20">
                {p.type}
              </span>
              <div className="absolute bottom-3 right-3 w-10 h-10 rounded-full bg-dark-800/90 border border-dark-600 flex items-center justify-center text-accent">
                {iconMap[p.type] || <Monitor size={20} />}
              </div>
            </div>

            <div className="p-5">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-base font-bold">{p.name}</h3>
                <ExternalLink size={14} className="text-slate-600 group-hover:text-accent transition-colors" />
              </div>
              <p className="text-xs text-slate-500 leading-relaxed mb-4">{p.description}</p>
              <div className="flex flex-wrap gap-2">
                {p.stack.map((m) => (
                  <span
                    key={m}
                    className="bg-accent-dim text-accent text-[11px] font-mono px-2 py-0.5 rounded"
                  >
                    {m}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
