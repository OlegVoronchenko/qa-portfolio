#!/usr/bin/env node
/**
 * CV Discovery — Build-Time Script
 * =================================
 *
 * PURPOSE
 * -------
 * Scans public/cv/ for PDF resumes and writes the selected one to
 * src/data/cv-manifest.json, which the React app imports via
 * useCv() exactly like profile.json / requirements.json. No runtime
 * API, no backend — the frontend just reads whatever this script
 * decided at build time.
 *
 * WHY NOT import.meta.glob
 * -------------------------
 * import.meta.glob only sees files Vite controls at bundle time and
 * can't rank them by git history — this needs real `git log`/`git
 * status` calls, which only make sense in a plain Node build step.
 *
 * SELECTION RULES
 * ----------------
 * See cv-select-logic.mjs for the ranking algorithm itself. In short:
 * non-PDF files are ignored; zero PDFs means no Download CV link;
 * one PDF is used as-is; multiple PDFs are ranked by git commit
 * history (falling back to filesystem mtime only when git history is
 * unavailable or insufficient — e.g. a shallow clone — which is
 * recorded as an explicit warning, not silently assumed correct).
 *
 * The original filename is preserved verbatim (including spaces) so
 * the browser downloads it under its real name; only the URL embedded
 * in the href is percent-encoded.
 *
 * RUN
 * ---
 *   node scripts/select-cv.mjs
 *
 * Wired into `npm run build` / `npm run dev` via the `prebuild` /
 * `predev` lifecycle scripts in package.json.
 */
import { readdirSync, statSync, existsSync, mkdirSync, writeFileSync } from 'node:fs'
import { execFileSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { isPdf, selectBestCv, buildManifest } from './cv-select-logic.mjs'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const PROJECT_ROOT = path.resolve(__dirname, '..')
const CV_DIR = path.join(PROJECT_ROOT, 'public', 'cv')
const MANIFEST_PATH = path.join(PROJECT_ROOT, 'src', 'data', 'cv-manifest.json')

function isGitAvailable() {
  try {
    execFileSync('git', ['rev-parse', '--is-inside-work-tree'], {
      cwd: PROJECT_ROOT,
      stdio: ['ignore', 'ignore', 'ignore'],
    })
    return true
  } catch {
    return false
  }
}

function isUncommittedOrUntracked(relPath) {
  try {
    const out = execFileSync('git', ['status', '--porcelain', '--', relPath], {
      cwd: PROJECT_ROOT,
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
    })
    return out.trim().length > 0
  } catch {
    return false
  }
}

function gitFileCommitTimestamp(relPath) {
  try {
    const out = execFileSync('git', ['log', '-1', '--format=%ct', '--', relPath], {
      cwd: PROJECT_ROOT,
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
    }).trim()
    return out ? parseInt(out, 10) : null
  } catch {
    return null
  }
}

function gatherCandidates() {
  if (!existsSync(CV_DIR)) return []

  const gitAvailable = isGitAvailable()

  return readdirSync(CV_DIR, { withFileTypes: true })
    .filter((entry) => entry.isFile() && isPdf(entry.name))
    .map((entry) => {
      const filename = entry.name
      const absPath = path.join(CV_DIR, filename)
      const relPath = path.relative(PROJECT_ROOT, absPath)
      const fsMtime = statSync(absPath).mtimeMs

      if (!gitAvailable) {
        return { filename, isUncommitted: false, commitTimestamp: null, fsMtime }
      }

      const uncommitted = isUncommittedOrUntracked(relPath)
      const commitTimestamp = uncommitted ? null : gitFileCommitTimestamp(relPath)
      return { filename, isUncommitted: uncommitted, commitTimestamp, fsMtime }
    })
}

function main() {
  const candidates = gatherCandidates()
  const { selected, warnings } = selectBestCv(candidates)
  const manifest = buildManifest(selected, warnings)

  mkdirSync(path.dirname(MANIFEST_PATH), { recursive: true })
  writeFileSync(MANIFEST_PATH, JSON.stringify(manifest, null, 2) + '\n')

  if (selected) {
    console.log(`[select-cv] Selected "${selected.filename}" (source: ${manifest.source}) out of ${candidates.length} PDF(s).`)
  } else {
    console.log('[select-cv] No PDF found in public/cv/ — Download CV link will be hidden.')
  }
  for (const w of warnings) {
    console.warn(`[select-cv] WARNING: ${w}`)
  }
}

main()
