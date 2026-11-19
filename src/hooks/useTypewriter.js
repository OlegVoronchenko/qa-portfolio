/**
 * Typewriter Hook
 *
 * Types out a phrase character by character. With a single phrase
 * and loop=false it types once and stops (used for the Hero's
 * primary role — it must never be replaced by anything). With
 * multiple phrases and loop=true (default) it cycles: type, pause,
 * delete, move to the next phrase, repeat (used for the Hero's
 * supporting specialization line).
 *
 * Respects prefers-reduced-motion: skips the animation and renders
 * a meaningful static fallback instead — the first phrase for a
 * single-shot instance, or all phrases joined for a cycling one.
 *
 * @param {string[]} phrases - pass a stable (module-level or memoized)
 *   array reference; a new array identity on every render restarts
 *   the animation.
 * @param {{ loop?: boolean }} [options]
 * @returns {string} the currently visible text
 */
import { useState, useEffect } from 'react'
import { prefersReducedMotion } from '../utils/motion'

const TYPE_SPEED_MS = 55
const DELETE_SPEED_MS = 30
const PAUSE_MS = 1400

export function useTypewriter(phrases, { loop = true } = {}) {
  const [text, setText] = useState('')
  const [phraseIdx, setPhraseIdx] = useState(0)
  const [charIdx, setCharIdx] = useState(0)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    if (prefersReducedMotion()) {
      setText(loop ? phrases.join(' · ') : phrases[0])
      return
    }

    const current = phrases[phraseIdx]

    if (!deleting && charIdx === current.length) {
      if (!loop) return // single-shot: fully typed, stop — never replaced
      const t = setTimeout(() => setDeleting(true), PAUSE_MS)
      return () => clearTimeout(t)
    }

    if (deleting && charIdx === 0) {
      setDeleting(false)
      setPhraseIdx((i) => (i + 1) % phrases.length)
      return
    }

    const t = setTimeout(() => {
      const next = deleting ? charIdx - 1 : charIdx + 1
      setText(current.substring(0, next))
      setCharIdx(next)
    }, deleting ? DELETE_SPEED_MS : TYPE_SPEED_MS)

    return () => clearTimeout(t)
  }, [charIdx, deleting, phraseIdx, loop, phrases])

  return text
}
