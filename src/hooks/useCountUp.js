/**
 * Animated Counter Hook
 *
 * Counts from 0 to a target value using requestAnimationFrame
 * with ease-out cubic easing (starts fast, decelerates at end).
 * Designed to be paired with IntersectionObserver — call start()
 * when the element scrolls into view.
 *
 * @param {object} options
 * @param {number} options.end - Target value to count up to
 * @param {number} [options.duration=2000] - Animation duration in ms
 * @param {boolean} [options.startOnMount=false] - If true, counts immediately
 * @returns {{ count: number, start: () => void }}
 */
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
