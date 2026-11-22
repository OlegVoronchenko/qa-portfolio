/**
 * How I Think: Interactive Experiments
 * ======================================
 *
 * One small, single-choice experiment per article, keyed by article
 * id (see howIThink.js). Each experiment is deliberately simple:
 * a prompt, a few options, and a reveal panel shown after the
 * visitor picks one. None of these are scored quizzes with a single
 * "winning" answer to chase; the reveal text is written to explain
 * the reasoning, not to declare one choice universally correct.
 *
 * All figures and suite sizes are illustrative, not measured data.
 *
 * Pure data only, no JSX. `visual` is a string key the consuming
 * component uses to pick which small illustration to render
 * (overlap bars, scenario cards, or a code boundary check) since the
 * three experiments are not visually interchangeable.
 */

export const HOW_I_THINK_EXPERIMENTS = {
  'automation-architecture': {
    visual: 'overlap',
    prompt: 'Which suite gives you more confidence?',
    options: [
      { id: 'a', label: 'Suite A (1,000 tests)' },
      { id: 'b', label: 'Suite B (200 tests)' },
      { id: 'unknown', label: 'Not enough information' },
    ],
    reveal: {
      heading: 'Not enough information.',
      body: [
        "Whichever you picked, the honest answer is the same: a test count and a short description cannot tell you how much a suite overlaps itself, how independent its checks really are, or whether it covers the workflows your business cares about most.",
        'Suite A could be full of essential regression checks. Suite B could be missing an entire business workflow. Both are plausible from the description alone.',
        'The illustration below is a simplified picture of why: Suite A leans on many checks that share the same underlying path (shown in one shade), while Suite B spreads its smaller number of checks across more distinct failure modes (shown in several shades). More shades is not automatically better. It depends on which failure modes actually matter.',
      ],
    },
    illustration: {
      suiteA: {
        label: 'Suite A',
        count: '1,000 tests',
        note: 'Mostly repeated coverage of a few workflows',
        segments: ['shared', 'shared', 'shared', 'shared', 'shared', 'unique'],
      },
      suiteB: {
        label: 'Suite B',
        count: '200 tests',
        note: 'Smaller, spread across distinct failure modes',
        segments: ['unique', 'unique', 'unique', 'unique', 'shared', 'unique'],
      },
    },
  },

  'release-risk': {
    visual: 'scenario',
    prompt: 'What would you do?',
    scenario: {
      timebox: 'One hour remains before release.',
      options: [
        {
          id: 'a',
          label: 'Run Test A',
          detail: 'Cosmetic issue. A few minutes. Low consequence if it ships broken.',
        },
        {
          id: 'b',
          label: 'Start Test B',
          detail: 'Critical transaction. About three hours to run. Severe consequence if it ships broken.',
        },
        {
          id: 'focused',
          label: 'Find a focused, feasible check for the critical transaction',
          detail: 'Narrower than Test B. Designed to fit inside the hour.',
        },
      ],
    },
    options: [
      { id: 'a', label: 'Run Test A' },
      { id: 'b', label: 'Start Test B' },
      { id: 'focused', label: 'Find a focused, feasible check' },
    ],
    reveal: {
      heading: 'There is no universally correct choice here, only trade-offs.',
      body: [
        'Running Test A is fast and certain, but it spends your only hour on the lower-consequence problem.',
        "Starting Test B targets the right risk category, but a three-hour test will not finish before a one-hour release window closes. Its result cannot inform a decision that has already been made.",
        'A focused, feasible check on the critical transaction trades completeness for timeliness: it will verify less than the full Test B would, but if it finishes in time, its result can still change what the team decides to do.',
        "That third option is not automatically right either. It only works if a meaningfully narrower check actually exists and can be trusted. This example does not give you enough detail to know that for certain, and neither will most real release decisions.",
      ],
    },
  },

  'ai-verification': {
    visual: 'code',
    prompt: 'Can you spot the problem?',
    requirement: 'Apply a 10% discount to orders over €100.',
    code: {
      label: 'Generated implementation',
      language: 'javascript',
      snippet: 'function finalPrice(total) {\n  return total >= 100 ? total * 0.9 : total;\n}',
    },
    options: [
      { id: 'percentage', label: 'The discount percentage' },
      { id: 'boundary', label: 'The boundary condition' },
      { id: 'none', label: 'There is no problem' },
    ],
    correctOptionId: 'boundary',
    reveal: {
      heading: 'The boundary condition is incorrect.',
      body: [
        '"Over €100" means total > 100, not total >= 100. An order of exactly €100 should not receive the discount, and the generated implementation gives it one anyway.',
        'The generated test did not catch this because it only checked total = 100 against the same assumption that produced the bug. A test built on the same misunderstanding as the code will confirm the code, not verify it.',
      ],
      correctedCode: {
        label: 'Corrected implementation',
        language: 'javascript',
        snippet: 'function finalPrice(total) {\n  return total > 100 ? total * 0.9 : total;\n}',
      },
      boundaryCheck: {
        label: 'Boundary check that would have caught it',
        language: 'javascript',
        snippet: 'expect(finalPrice(100)).toBe(100); // exactly 100: no discount',
      },
    },
  },
}
