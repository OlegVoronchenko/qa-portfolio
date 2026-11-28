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
 * like tone, length, or "does this sound human" — those require
 * editorial review, not a script, and a line-count or word-count
 * check would be brittle against any legitimate future rewording.
 * What it does check is mechanical and unambiguous:
 *
 *   1. Exactly 3 scenarios, with the required titles present.
 *   2. No em dashes (—) or en dashes (–) anywhere in the content.
 *   3. No employer or client names.
 *   4. No literal unsupported first-person achievement-claim phrases.
 *   5. No generic AI-marketing cliches.
 *   6. A handful of exact, hard-to-accidentally-reproduce phrases
 *      from the approved copy are still present verbatim (a canary
 *      against the content being silently rewritten).
 *   7. Every scenario's reveal has a non-empty explanation.
 *   8. The AI scenario specifically has a corrected-code sample.
 *
 * USAGE
 * -----
 *   node scripts/validate_how_i_think_content.mjs
 */
import { HOW_I_THINK_SCENARIOS } from '../src/data/howIThink.js'
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

const EXPECTED_SCENARIOS = {
  'quality-strategy': {
    title: "When Green Isn't Good Enough",
    canaries: [
      '10,000 tests passed. Everything looks great.',
      "The test count doesn't settle it.",
    ],
  },
  'engineering-decisions': {
    title: 'One Hour. One Decision.',
    canaries: [
      "The release is in an hour. You can't test everything.",
      'Sometimes the right call is to delay the release.',
    ],
  },
  'ai-judgment': {
    title: 'When AI Agrees With Itself',
    canaries: [
      'AI wrote the code. AI wrote the tests. All green.',
      'The implementation and its test share the same incorrect assumption.',
    ],
  },
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
  if (HOW_I_THINK_SCENARIOS.length !== 3) {
    violations.push(`Expected exactly 3 scenarios, found ${HOW_I_THINK_SCENARIOS.length}`)
  }

  for (const scenario of HOW_I_THINK_SCENARIOS) {
    const label = `Scenario "${scenario.id}"`
    const expected = EXPECTED_SCENARIOS[scenario.id]

    if (!expected) {
      violations.push(`${label}: unexpected scenario id (not in the approved set)`)
      continue
    }

    const allStrings = collectStrings(scenario)
    checkDashes(label, allStrings)
    checkEmployerNames(label, allStrings)
    checkAchievementClaims(label, allStrings)
    checkAiMarketingCliches(label, allStrings)

    if (scenario.title !== expected.title) {
      violations.push(`${label}: expected title "${expected.title}", got "${scenario.title}"`)
    }

    if (!scenario.hook || scenario.hook.length === 0) {
      violations.push(`${label}: missing collapsed hook text`)
    }

    if (!scenario.cta || !scenario.cta.trim()) {
      violations.push(`${label}: missing CTA label`)
    }

    // Canary: exact approved phrases still present verbatim, across
    // both the collapsed identity and the interactive content.
    const experiment = HOW_I_THINK_EXPERIMENTS[scenario.id]
    const joined = [...allStrings, ...collectStrings(experiment)].join('\n')
    for (const phrase of expected.canaries) {
      if (!joined.includes(phrase)) {
        violations.push(`${label}: expected approved phrase not found verbatim (content may have been rewritten): "${phrase}"`)
      }
    }
  }

  // Experiments.
  for (const scenario of HOW_I_THINK_SCENARIOS) {
    const experiment = HOW_I_THINK_EXPERIMENTS[scenario.id]
    const label = `Experiment for "${scenario.id}"`

    if (!experiment) {
      violations.push(`${label}: no experiment defined`)
      continue
    }

    const allStrings = collectStrings(experiment)
    checkDashes(label, allStrings)
    checkEmployerNames(label, allStrings)
    checkAchievementClaims(label, allStrings)
    checkAiMarketingCliches(label, allStrings)

    if (!experiment.prompt || !experiment.prompt.trim()) {
      violations.push(`${label}: missing prompt`)
    }
    if (!Array.isArray(experiment.options) || experiment.options.length < 2) {
      violations.push(`${label}: expected at least 2 options`)
    }
    if (!experiment.reveal || !Array.isArray(experiment.reveal.body) || experiment.reveal.body.length === 0) {
      violations.push(`${label}: missing reveal explanation (empty body)`)
    }

    // Only the AI scenario is a graded question with one objectively
    // correct answer; the other two must NOT grade a choice.
    if (scenario.id === 'ai-judgment') {
      if (!experiment.correctOptionId) {
        violations.push(`${label}: AI scenario must declare a correctOptionId`)
      }
      if (!experiment.reveal?.correctedCode?.snippet) {
        violations.push(`${label}: AI scenario must include a corrected code sample`)
      }
    } else if (experiment.correctOptionId) {
      violations.push(`${label}: this scenario is a judgment call and must not declare a correctOptionId`)
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
  console.log('  ✓ Exactly 3 scenarios with the required titles')
  console.log('  ✓ No em/en dashes')
  console.log('  ✓ No employer/client names')
  console.log('  ✓ No unsupported achievement-claim patterns')
  console.log('  ✓ No generic AI-marketing cliches')
  console.log('  ✓ Approved canary phrases present verbatim')
  console.log('  ✓ Every scenario has a non-empty reveal explanation')
  console.log('  ✓ Only the AI scenario grades a correct answer')
  console.log('='.repeat(60) + '\n')
}

main()
