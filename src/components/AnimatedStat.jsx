import { useEffect, useRef } from 'react'
import { useCountUp } from '../hooks/useCountUp'

export function AnimatedStat({
  value,
  suffix = '',
  prefix = '',
  label,
  duration = 2000,
}) {
  const ref = useRef(null)
  const { count, start } = useCountUp({
    end: value,
    duration,
    startOnMount: false,
  })

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          start()
          observer.disconnect()
        }
      },
      { threshold: 0.3 }
    )

    if (ref.current) observer.observe(ref.current)
    return () => observer.disconnect()
  }, [])

  const displayValue = value >= 1000
    ? `${Math.floor(count / 1000)}K`
    : count

  return (
    <div ref={ref} className="text-center">
      <div className="text-2xl sm:text-3xl font-bold font-mono tabular-nums text-accent">
        {prefix}
        {displayValue}
        {suffix}
      </div>
      <div className="text-xs text-slate-500 uppercase tracking-wider mt-1">
        {label}
      </div>
    </div>
  )
}
