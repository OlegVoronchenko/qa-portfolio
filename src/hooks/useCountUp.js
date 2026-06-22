import { useState, useEffect, useRef } from 'react'

export function useCountUp({ end, duration = 2000, startOnMount = false }) {
  const [count, setCount] = useState(startOnMount ? 0 : end)
  const [hasStarted, setHasStarted] = useState(startOnMount)
  const frameRef = useRef()

  useEffect(() => {
    if (!hasStarted) return

    let startTime

    const animate = (timestamp) => {
      if (!startTime) startTime = timestamp
      const elapsed = timestamp - startTime
      const progress = Math.min(elapsed / duration, 1)

      const eased = 1 - Math.pow(1 - progress, 3)
      const current = Math.floor(end * eased)

      setCount(current)

      if (progress < 1) {
        frameRef.current = requestAnimationFrame(animate)
      } else {
        setCount(end)
      }
    }

    frameRef.current = requestAnimationFrame(animate)

    return () => {
      if (frameRef.current) cancelAnimationFrame(frameRef.current)
    }
  }, [hasStarted, end, duration])

  const start = () => setHasStarted(true)

  return { count, start }
}
