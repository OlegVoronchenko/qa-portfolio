#!/usr/bin/env node
/**
 * How I Think — Editorial Content Validator
 * ============================================
 *
 * PURPOSE
 * -------
 * Lightweight, deterministic checks over the approved How I Think
 * content (src/data/howIThink.js, src/data/howIThinkExperiments.js).
 * This intentionally does NOT attempt to judge subjective qualities
 * like tone or "does this sound human" — those require editorial
 * review, not a script. What it does check is mechanical and
 * unambiguous:
 *
 *   1. No em dashes (—) or en dashes (–) anywhere in the content.
 *   2. No employer or client names.
 *   3. No literal unsupported first-person achievement-claim phrases.
 *   4. No generic AI-marketing cliches.
 *   5. A handful of exact, hard-to-accidentally-reproduce phrases
 *      from the approved articles are still present verbatim (a
 *      canary against the content being silently rewritten).
 *   6. Every article has its expected section headings.
 *   7. Every experiment has a non-empty reveal heading + explanation.
 *
 * USAGE
 * -----
 *   node scripts/validate_how_i_think_content.mjs
 */
import { HOW_I_THINK_ARTICLES } from '../src/data/howIThink.js'
import { HOW_I_THINK_EXPERIMENTS } from '../src/data/howIThinkExperiments.js'

const EMPLOYER_NAMES = ['globallogic', 'hitachi']

const ACHIEVEMENT_CLAIM_PATTERNS = [
  /\bi delivered\b/i,
  /\bi reduced execution time by\b/i,
  /\bat globallogic\b/i,
  /\bthis project achieved\b/i,
  /\bi built\b.{0,40}\bfor (our|my) (client|employer)\b/i,
  /\b\d+%\s*(faster|improvement|reduction)\b.{0,20}\b(i|we)\s+(achieved|delivered|shipped)\b/i,
]

const AI_MARKETING_CLICHES = [
  'revolutionize',
  'revolutionary',
  'game-changer',
  'game changer',
  'unlock the power',
  'seamless synergy',
  'cutting-edge',
  'cutting edge',
  'best-in-class',
  'leverage ai',
  'paradigm shift',
  'disruptive innovation',
  'next level',
  'supercharge',
  'state-of-the-art',
  'unparalleled',
]

// A few exact, distinctive phrases from the approved text per article.
// If any of these go missing, the content was likely rewritten rather
// than just reformatted.
const CANARY_PHRASES = {
  'automation-architecture': [
    'What if 8,000 of those tests are checking almost the same thing?',
    'What could still be broken if every test passed?',
  ],
  'release-risk': [
    'Risk ≈ Failure Likelihood × Impact',
    "The most valuable test isn't always the one most likely to find a bug.",
  ],
  'ai-verification': [
    'Apply a 10% discount to orders over €100.',
    "It's that the tests agreed with the mistake.",
  ],
}

const EXPECTED_SECTION_HEADINGS = {
  'automation-architecture': ["Let's try something", 'The hidden problem', 'What changes in practice?', 'One last thought'],
  'release-risk': ['Risk has more than one dimension', 'The decision nobody can make for us', "What I'd want before making the call", 'The surprising part'],
  'ai-verification': ['A tiny example', 'The interesting problem', 'So what changes?', 'The real bottleneck'],
}

const violations = []

function collectStrings(value, out = []) {
  if (typeof value === 'string') {
    out.push(value)
  } else if (Array.isArray(value)) {
    for (const v of value) collectStrings(v, out)
  } else if (value && typeof value === 'object') {
    for (const v of Object.values(value)) collectStrings(v, out)
  }
  return out
}

function checkDashes(label, strings) {
  for (const s of strings) {
    if (/[—–]/.test(s)) {
      violations.push(`${label}: contains an em dash or en dash: "${s}"`)
    }
  }
}

function checkEmployerNames(label, strings) {
  for (const s of strings) {
    const lower = s.toLowerCase()
    for (const name of EMPLOYER_NAMES) {
      if (lower.includes(name)) {
        violations.push(`${label}: mentions a disallowed employer/client name ("${name}"): "${s}"`)
      }
    }
  }
}

function checkAchievementClaims(label, strings) {
  for (const s of strings) {
    for (const pattern of ACHIEVEMENT_CLAIM_PATTERNS) {
      if (pattern.test(s)) {
        violations.push(`${label}: looks like an unsupported first-person achievement claim: "${s}"`)
      }
    }
  }
}

function checkAiMarketingCliches(label, strings) {
  for (const s of strings) {
    const lower = s.toLowerCase()
    for (const phrase of AI_MARKETING_CLICHES) {
      if (lower.includes(phrase)) {
        violations.push(`${label}: contains a generic AI-marketing phrase ("${phrase}"): "${s}"`)
      }
    }
  }
}

function main() {
  if (HOW_I_THINK_ARTICLES.length !== 3) {
    violations.push(`Expected exactly 3 articles, found ${HOW_I_THINK_ARTICLES.length}`)
  }

  for (const article of HOW_I_THINK_ARTICLES) {
    const label = `Article "${article.id}"`
    const allStrings = collectStrings(article)

    checkDashes(label, allStrings)
    checkEmployerNames(label, allStrings)
    checkAchievementClaims(label, allStrings)
    checkAiMarketingCliches(label, allStrings)

    // Canary: exact approved phrases still present verbatim.
    const joined = allStrings.join('\n')
    const canaries = CANARY_PHRASES[article.id] || []
    for (const phrase of canaries) {
      if (!joined.includes(phrase)) {
        violations.push(`${label}: expected approved phrase not found verbatim (content may have been rewritten): "${phrase}"`)
      }
    }

    // Missing article sections.
    const expectedHeadings = EXPECTED_SECTION_HEADINGS[article.id] || []
    const actualHeadings = (article.sections || []).map((s) => s.heading)
    for (const heading of expectedHeadings) {
      if (!actualHeadings.includes(heading)) {
        violations.push(`${label}: missing expected section "${heading}"`)
      }
    }
    if (!article.opening || article.opening.length === 0) {
      violations.push(`${label}: missing opening hook`)
    }
  }

  // Experiments.
  for (const article of HOW_I_THINK_ARTICLES) {
    const experiment = HOW_I_THINK_EXPERIMENTS[article.id]
    const label = `Experiment for "${article.id}"`

    if (!experiment) {
      violations.push(`${label}: no experiment defined`)
      continue
    }

    const allStrings = collectStrings(experiment)
    checkDashes(label, allStrings)
    checkEmployerNames(label, allStrings)
    checkAchievementClaims(label, allStrings)
    checkAiMarketingCliches(label, allStrings)

    if (!experiment.reveal || !experiment.reveal.heading) {
      violations.push(`${label}: missing reveal heading`)
    }
    if (!experiment.reveal || !Array.isArray(experiment.reveal.body) || experiment.reveal.body.length === 0) {
      violations.push(`${label}: missing reveal explanation (empty body)`)
    }
    if (!Array.isArray(experiment.options) || experiment.options.length < 2) {
      violations.push(`${label}: expected at least 2 options`)
    }
  }

  if (violations.length > 0) {
    console.log(`\n${'='.repeat(60)}`)
    console.log('How I Think Content Validation — FAILED')
    console.log('='.repeat(60) + '\n')
    for (const v of violations) console.log(`  ✗ ${v}`)
    console.log(`\n${'='.repeat(60)}\n`)
    process.exit(1)
  }

  console.log(`\n${'='.repeat(60)}`)
  console.log('How I Think Content Validation — PASSED')
  console.log('='.repeat(60))
  console.log('  ✓ No em/en dashes')
  console.log('  ✓ No employer/client names')
  console.log('  ✓ No unsupported achievement-claim patterns')
  console.log('  ✓ No generic AI-marketing cliches')
  console.log('  ✓ Approved canary phrases present verbatim')
  console.log('  ✓ All expected sections present')
  console.log('  ✓ All experiments have a reveal explanation')
  console.log('='.repeat(60) + '\n')
}

main()
