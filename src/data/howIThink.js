/**
 * How I Think: Scenario Identity
 * =================================
 *
 * Three compact decision scenarios demonstrating engineering
 * judgment. These are illustrative, generalized scenarios, not
 * claims about specific employers, clients, or historical projects.
 *
 * This file holds only what a collapsed card needs to render: the
 * category, title, a short two-line hook, and the CTA label. The
 * interactive scenario itself (setup, options, reveal) lives in
 * src/data/howIThinkExperiments.js, keyed by the same `id`.
 *
 * The wording here is approved canonical copy. Only formatting,
 * line breaks, and presentation-specific labels should be adapted
 * when rendering this data; the prose itself should not be
 * rewritten. See scripts/validate_how_i_think_content.mjs.
 *
 * Pure data only, no JSX. `icon` is a string key resolved to a
 * lucide-react component by the consuming component.
 */

export const HOW_I_THINK_SCENARIOS = [
  {
    id: 'quality-strategy',
    category: 'QUALITY STRATEGY',
    icon: 'Layers',
    title: "When Green Isn't Good Enough",
    hook: [
      '10,000 tests passed. Everything looks great.',
      'But what would make you question that result?',
    ],
    cta: 'Look closer',
  },
  {
    id: 'engineering-decisions',
    category: 'ENGINEERING DECISIONS',
    icon: 'Scale',
    title: 'One Hour. One Decision.',
    hook: [
      "The release is in an hour. You can't test everything.",
      'Where would you spend the time?',
    ],
    cta: 'Make the call',
  },
  {
    id: 'ai-judgment',
    category: 'AI & ENGINEERING JUDGMENT',
    icon: 'Sparkles',
    title: 'When AI Agrees With Itself',
    hook: [
      'AI wrote the code. AI wrote the tests. All green.',
      'What if they share the same mistake?',
    ],
    cta: 'Spot the catch',
  },
]
