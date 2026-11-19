/**
 * ESLint Configuration — Regression Tests
 * =========================================
 *
 * Exercises the real eslint.config.js (via the ESLint Node API, not
 * real files on disk) to confirm two things that broke silently
 * before this fix: ESLint 9 actually loads a working flat config at
 * all, and a genuine violation produces a nonzero-equivalent result
 * (errorCount > 0) rather than being silently swallowed.
 *
 * Run: node --test scripts/eslint-config.test.mjs
 */
import test from 'node:test'
import assert from 'node:assert/strict'
import { ESLint } from 'eslint'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const CONFIG_PATH = path.join(__dirname, '..', 'eslint.config.js')

function makeLinter() {
  return new ESLint({ overrideConfigFile: CONFIG_PATH })
}

test('eslint.config.js loads and lints a clean React component with zero errors', async () => {
  const eslint = makeLinter()
  const clean = `
    export default function Widget() {
      return <div className="widget">Hello</div>
    }
  `
  const [result] = await eslint.lintText(clean, { filePath: 'src/components/Widget.jsx' })
  assert.equal(result.errorCount, 0, JSON.stringify(result.messages))
})

test('eslint.config.js reports a genuine violation (unused variable)', async () => {
  const eslint = makeLinter()
  const broken = `
    const unused = 42
    export default function Widget() {
      return <div>Hello</div>
    }
  `
  const [result] = await eslint.lintText(broken, { filePath: 'src/components/Broken.jsx' })
  assert.ok(result.errorCount > 0, 'expected at least one lint error for an unused variable')
  assert.ok(
    result.messages.some((m) => m.ruleId === 'no-unused-vars'),
    'expected a no-unused-vars violation to be reported'
  )
})

test('eslint.config.js parses JSX without a React import (automatic runtime)', async () => {
  // react/react-in-jsx-scope must stay off — Vite's @vitejs/plugin-react
  // uses the automatic JSX runtime, so this must NOT be flagged.
  const eslint = makeLinter()
  const noReactImport = `
    export default function Widget() {
      return <div>No React import needed</div>
    }
  `
  const [result] = await eslint.lintText(noReactImport, { filePath: 'src/components/NoImport.jsx' })
  const reactScopeErrors = result.messages.filter((m) => m.ruleId === 'react/react-in-jsx-scope')
  assert.equal(reactScopeErrors.length, 0)
})
