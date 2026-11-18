/**
 * Shared prefers-reduced-motion check.
 *
 * Used anywhere an animation should be skipped (or jump straight to
 * its end state) for users who have requested reduced motion at the
 * OS/browser level — the stat counters (useCountUp), the Hero
 * typewriter, and the Experience timeline's expand/collapse transition.
 */
export function prefersReducedMotion() {
  return (
    typeof window !== 'undefined' &&
    window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  )
}
