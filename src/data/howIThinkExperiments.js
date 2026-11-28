/**
 * How I Think: Interactive Scenarios
 * ====================================
 *
 * One compact, interactive decision per card, keyed by scenario id
 * (see howIThink.js). Each scenario is deliberately small: an
 * optional short setup (`intro`), a prompt, a few options, and a
 * reveal shown after the visitor picks one.
 *
 * None of these are scored quizzes. Only the AI scenario has an
 * objectively correct option (`correctOptionId`); the other two are
 * judgment calls, so no option is marked right or wrong, and the
 * reveal applies no matter what was picked.
 *
 * Pure data only, no JSX. `intro` is an ordered list of small typed
 * blocks (`p`, `quote`, `code`) rendered above the prompt. `reveal`
 * holds the explanation (`body`), and, only where applicable, a
 * `correctedCode` sample, a closing `insight`, or a discreet `note`.
 */

export const HOW_I_THINK_EXPERIMENTS = {
  'quality-strategy': {
    prompt: 'Which suite would you trust more?',
    options: [
      {
        id: 'a',
        label: 'Suite A (1,000 tests)',
        detail: 'Strong coverage of a few workflows. Significant overlap.',
      },
      {
        id: 'b',
        label: 'Suite B (200 tests)',
        detail: 'Broader coverage of different failure modes. Some workflows may still be missing.',
      },
      { id: 'unknown', label: 'I need more evidence' },
    ],
    reveal: {
      body: [
        "The test count doesn't settle it.",
        "I'd want to know which risks each suite covers, what both might miss, and how much independent evidence the tests provide.",
        'More tests can help. More meaningful evidence helps us decide.',
      ],
    },
  },

  'engineering-decisions': {
    intro: [{ type: 'p', text: 'One hour remains before release.' }],
    prompt: "What's your next move?",
    options: [
      { id: 'a', label: 'Run a short regression check on stable functionality.' },
      { id: 'b', label: 'Start a three-hour end-to-end test of a critical transaction.' },
      { id: 'c', label: 'Run a focused check on the riskiest part of the critical transaction.' },
    ],
    reveal: {
      body: [
        'The decision depends on what each check can tell us before the deadline.',
        'A focused check may provide useful evidence quickly, but it cannot replace full coverage.',
        "I'd weigh potential impact, recent changes, execution time, and what remains unknown, then make the residual risk explicit.",
      ],
      note: 'Sometimes the right call is to delay the release.',
    },
  },

  'ai-judgment': {
    intro: [
      { type: 'quote', text: 'Apply a 10% discount to orders over €100.' },
      {
        type: 'code',
        label: 'Generated implementation',
        snippet: 'function finalPrice(total) {\n  return total >= 100 ? total * 0.9 : total;\n}',
      },
      {
        type: 'code',
        label: 'Generated test',
        snippet: 'expect(finalPrice(100)).toBe(90);',
      },
    ],
    prompt: "What's wrong here?",
    options: [
      { id: 'percentage', label: 'The discount percentage' },
      { id: 'boundary', label: 'The boundary condition' },
      { id: 'none', label: 'Nothing is wrong' },
    ],
    correctOptionId: 'boundary',
    reveal: {
      body: [
        'The boundary condition.',
        '"Over €100" means > 100, not >= 100.',
        'The implementation and its test share the same incorrect assumption.',
      ],
      correctedCode: {
        label: 'Corrected condition',
        snippet: 'total > 100',
      },
      insight: [
        'Passing tests are evidence, but only against the assumptions they check.',
        "I'd verify generated code and tests against the original requirement, especially at boundaries.",
      ],
    },
  },
}
