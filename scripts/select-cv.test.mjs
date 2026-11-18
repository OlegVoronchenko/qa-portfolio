/**
 * CV Selection — Unit Tests
 * =========================
 *
 * Exercises the pure selection logic in cv-select-logic.mjs with
 * synthetic candidates. No filesystem or git calls, no new test
 * framework dependency — uses Node's built-in test runner.
 *
 * Run: node --test scripts/select-cv.test.mjs
 */
import test from 'node:test'
import assert from 'node:assert/strict'

import { isPdf, selectBestCv, buildManifest } from './cv-select-logic.mjs'

test('no PDF -> nothing selected, no warnings', () => {
  const { selected, warnings } = selectBestCv([])
  assert.equal(selected, null)
  assert.deepEqual(warnings, [])
})

test('one PDF -> that one is selected', () => {
  const candidate = { filename: 'CV.pdf', isUncommitted: false, commitTimestamp: 1000, fsMtime: 1000_000 }
  const { selected } = selectBestCv([candidate])
  assert.equal(selected.filename, 'CV.pdf')
})

test('multiple PDFs -> most recent commit timestamp wins', () => {
  const older = { filename: 'old.pdf', isUncommitted: false, commitTimestamp: 1000, fsMtime: 1 }
  const newer = { filename: 'new.pdf', isUncommitted: false, commitTimestamp: 2000, fsMtime: 1 }
  const { selected } = selectBestCv([older, newer])
  assert.equal(selected.filename, 'new.pdf')
})

test('non-PDF files are filtered before reaching selection (isPdf helper)', () => {
  assert.equal(isPdf('resume.pdf'), true)
  assert.equal(isPdf('resume.PDF'), true, 'extension match should be case-insensitive')
  assert.equal(isPdf('resume.docx'), false)
  assert.equal(isPdf('notes.pdf.txt'), false)
  assert.equal(isPdf('.DS_Store'), false)
})

test('an uncommitted edit outranks an older-looking committed timestamp', () => {
  // Committed file has a large, recent-looking commitTimestamp.
  const committed = { filename: 'committed.pdf', isUncommitted: false, commitTimestamp: 9_999_999_999, fsMtime: 1 }
  // Uncommitted file has a tiny fsMtime number, but represents an
  // in-progress local edit and must still win.
  const uncommittedEdit = { filename: 'uncommitted.pdf', isUncommitted: true, commitTimestamp: null, fsMtime: 2 }
  const { selected } = selectBestCv([committed, uncommittedEdit])
  assert.equal(selected.filename, 'uncommitted.pdf')
})

test('among multiple uncommitted files, the most recently touched (fsMtime) wins', () => {
  const a = { filename: 'a.pdf', isUncommitted: true, commitTimestamp: null, fsMtime: 100 }
  const b = { filename: 'b.pdf', isUncommitted: true, commitTimestamp: null, fsMtime: 200 }
  const { selected } = selectBestCv([a, b])
  assert.equal(selected.filename, 'b.pdf')
})

test('missing git history falls back to filesystem mtime and records a warning', () => {
  const candidate = { filename: 'old-shallow.pdf', isUncommitted: false, commitTimestamp: null, fsMtime: 500 }
  const { selected, warnings } = selectBestCv([candidate])
  assert.equal(selected.filename, 'old-shallow.pdf')
  assert.equal(warnings.length, 1)
  assert.match(warnings[0], /fell back to filesystem mtime/)
})

test('ties are broken deterministically by ascending filename', () => {
  const a = { filename: 'z-resume.pdf', isUncommitted: false, commitTimestamp: 1000, fsMtime: 1 }
  const b = { filename: 'a-resume.pdf', isUncommitted: false, commitTimestamp: 1000, fsMtime: 1 }
  const first = selectBestCv([a, b]).selected.filename
  const second = selectBestCv([b, a]).selected.filename
  assert.equal(first, 'a-resume.pdf')
  assert.equal(second, 'a-resume.pdf', 'input order must not affect the result')
})

test('filenames with spaces are preserved verbatim in the manifest filename', () => {
  const candidate = {
    filename: 'Oleg Voronchenko Lead Test Automation Engineer CV.pdf',
    isUncommitted: false,
    commitTimestamp: 1000,
    fsMtime: 1,
  }
  const { selected } = selectBestCv([candidate])
  const manifest = buildManifest(selected, [])
  assert.equal(manifest.filename, 'Oleg Voronchenko Lead Test Automation Engineer CV.pdf')
})

test('the manifest URL percent-encodes spaces and is base-path-relative', () => {
  const candidate = { filename: 'My CV.pdf', isUncommitted: false, commitTimestamp: 1000, fsMtime: 1 }
  const { selected } = selectBestCv([candidate])
  const manifest = buildManifest(selected, [])
  assert.equal(manifest.url, 'cv/My%20CV.pdf')
  assert.ok(!manifest.url.startsWith('/'), 'url must be relative so BASE_URL can be prepended for GitHub Pages')
})

test('no PDF -> manifest has null filename/url (Download CV link must stay hidden)', () => {
  const manifest = buildManifest(null, [])
  assert.equal(manifest.filename, null)
  assert.equal(manifest.url, null)
  assert.equal(manifest.source, 'none')
})

test('manifest preserves warnings so limitations are surfaced, never silently hidden', () => {
  const candidate = { filename: 'resume.pdf', isUncommitted: false, commitTimestamp: null, fsMtime: 1 }
  const { selected, warnings } = selectBestCv([candidate])
  const manifest = buildManifest(selected, warnings)
  assert.equal(manifest.warnings.length, 1)
})
