/**
 * CV Manifest Hook
 *
 * Returns the build-time CV manifest produced by
 * scripts/select-cv.mjs (see that file for the selection rules).
 * `filename`/`url` are null when no PDF exists in public/cv/ —
 * components must treat that as "hide the Download CV control",
 * never fall back to a placeholder.
 */
import cvManifest from '../data/cv-manifest.json'

/** @returns {{ filename: string|null, url: string|null, source: string, warnings: string[] }} */
export function useCv() {
  return cvManifest
}
