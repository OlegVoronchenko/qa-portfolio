/**
 * CV Selection — Pure Decision Logic
 * ==================================
 *
 * PURPOSE
 * -------
 * Picks the "best" CV PDF out of a set of candidates. Contains no
 * filesystem or git calls so it can be unit-tested with synthetic
 * input (see select-cv.test.mjs) independently of the real repo state.
 *
 * CANDIDATE SHAPE
 * ----------------
 *   {
 *     filename: string,
 *     isUncommitted: boolean,   // untracked or has uncommitted local edits
 *     commitTimestamp: number | null,  // unix seconds of last commit touching the file
 *     fsMtime: number,          // filesystem mtime in ms, used as a fallback
 *   }
 *
 * RANKING
 * -------
 * 1. Uncommitted files always outrank committed ones (a local edit in
 *    progress is, by definition, the most recent intent) — ranked
 *    among themselves by filesystem mtime.
 * 2. Committed files are ranked by the timestamp of the last commit
 *    that touched that path. If that is unavailable (e.g. a shallow
 *    clone whose history doesn't reach the commit that introduced the
 *    file), the file falls back to filesystem mtime and a warning is
 *    recorded — never silently assumed to be reliable.
 * 3. Ties (identical effective timestamp within the same tier) are
 *    broken deterministically by ascending filename.
 */

export function isPdf(filename) {
  return filename.toLowerCase().endsWith('.pdf')
}

/**
 * @param {Array<{filename: string, isUncommitted: boolean, commitTimestamp: number|null, fsMtime: number}>} candidates
 * @returns {{ selected: object|null, warnings: string[] }}
 */
export function selectBestCv(candidates) {
  if (!candidates || candidates.length === 0) {
    return { selected: null, warnings: [] }
  }

  const warnings = []

  const ranked = candidates.map((c) => {
    if (c.isUncommitted) {
      return { ...c, tier: 2, value: c.fsMtime, source: 'uncommitted' }
    }
    if (c.commitTimestamp != null) {
      return { ...c, tier: 1, value: c.commitTimestamp * 1000, source: 'git' }
    }
    warnings.push(
      `${c.filename}: no usable git history for this path (shallow clone, or ` +
      `the commit that introduced it is outside the fetched range) — fell back ` +
      `to filesystem mtime, which is not guaranteed reliable across environments.`
    )
    return { ...c, tier: 1, value: c.fsMtime, source: 'filesystem' }
  })

  ranked.sort((a, b) => {
    if (a.tier !== b.tier) return b.tier - a.tier
    if (a.value !== b.value) return b.value - a.value
    return a.filename.localeCompare(b.filename)
  })

  return { selected: ranked[0], warnings }
}

/**
 * Build the manifest object written to src/data/cv-manifest.json.
 * The filename is preserved verbatim (so the browser downloads it
 * under its real name, spaces and all); the url is percent-encoded
 * and deliberately base-path-relative ("cv/<name>") — the consuming
 * component is responsible for prefixing import.meta.env.BASE_URL,
 * exactly like the existing test_report.json fetch in TestResults.jsx.
 *
 * @param {object|null} selected
 * @param {string[]} warnings
 */
export function buildManifest(selected, warnings = []) {
  if (!selected) {
    return { filename: null, url: null, source: 'none', warnings: [] }
  }
  return {
    filename: selected.filename,
    url: `cv/${encodeURIComponent(selected.filename)}`,
    source: selected.source,
    warnings,
  }
}
