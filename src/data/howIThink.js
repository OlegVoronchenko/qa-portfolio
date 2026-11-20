/**
 * How I Think — Content Data
 * ===========================
 *
 * Three illustrative engineering essays demonstrating analytical
 * thinking and engineering judgment. These are generalized,
 * illustrative scenarios — not claims about specific employers,
 * clients, or historical projects. See each article's framing below
 * and docs/requirements/REQ-008-how-i-think.md for the editorial
 * constraints this content was written under.
 *
 * Pure data only — no JSX, no rendering logic — so content can be
 * reviewed/edited independently of src/components/HowIThink.jsx.
 * `icon` is a string key resolved to a lucide-react component by the
 * consuming component, keeping this module framework-agnostic.
 *
 * Each article follows the same six-part structure: The Question,
 * The Intuition, The Hidden Problem, A Practical Model, The
 * Engineering Decision, The Takeaway. "A Practical Model" may include
 * a `comparison` — a compact two-sided illustrative thought
 * experiment, not a measured result.
 */

export const HOW_I_THINK_ARTICLES = [
  {
    id: 'automation-architecture',
    category: 'AUTOMATION ARCHITECTURE',
    icon: 'Layers',
    title: 'Why More Tests Can Mean Less Confidence',
    question: 'Can adding tests actually make an automation strategy less effective?',
    insight: 'Confidence comes from the independence of evidence, not the size of the suite.',
    sections: [
      {
        heading: 'The Question',
        body: [
          'A team doubles its test count over a year. Releases still break in production. Did testing fail, or was the wrong thing measured?',
        ],
      },
      {
        heading: 'The Intuition',
        body: [
          'More tests feels like more safety. Each new test is another checkpoint, so a bigger suite should mean a release is checked more thoroughly than a smaller one.',
        ],
      },
      {
        heading: 'The Hidden Problem',
        body: [
          'Test count is a weak proxy for confidence because tests are not independent. Many UI-heavy tests exercise the same underlying code paths through slightly different screens — when that shared path breaks, a dozen tests fail together and report one fact, not a dozen.',
          'That is duplicated coverage, not duplicated evidence. It also has a real cost: redundant end-to-end tests are typically the slowest and most flaky, so a large correlated suite can quietly discourage the team from running it often — the opposite of its intended effect.',
        ],
      },
      {
        heading: 'A Practical Model',
        body: [
          'Picture two suites protecting the same checkout flow.',
        ],
        comparison: {
          note: 'An illustrative thought experiment, not a claim that smaller is always better.',
          left: {
            label: 'Suite A — 200 tests',
            body: 'Mostly end-to-end variations of the same checkout path across browsers and layouts. Highly correlated: one shared-service regression fails dozens of tests at once.',
          },
          right: {
            label: 'Suite B — 40 tests',
            body: 'Each targets a distinct failure mode — a payment timeout, a currency rounding edge case, a permissions boundary, a partial-write on crash. Failures are largely independent.',
          },
        },
      },
      {
        heading: 'The Engineering Decision',
        body: [
          'Choose tests by the failure mode each one would uniquely reveal, not by how many can be added cheaply. In practice that means layering: fast, isolated tests for logic and boundaries; a deliberately small set of end-to-end tests for the journeys that actually matter; and periodically asking whether a failing test would tell you something a different failing test has not already told you.',
          'This is not an argument against large suites — a large system with many genuinely distinct risk areas may legitimately need many tests. The point is that size should track distinct risk, not habit.',
        ],
      },
      {
        heading: 'The Takeaway',
        body: [
          'Confidence comes from the quality and independence of evidence, not merely its quantity. More tests do not inherently reduce confidence — but a suite that grows without asking what each new test would uniquely catch can accumulate cost and correlated noise faster than it accumulates real signal.',
        ],
      },
    ],
  },
  {
    id: 'release-risk',
    category: 'ENGINEERING LEADERSHIP',
    icon: 'Scale',
    title: 'The Mathematics of Release Risk',
    question: 'How should a team decide what to test when time is limited?',
    insight: 'A good release decision needs clarity about which uncertainty matters most, not zero uncertainty.',
    sections: [
      {
        heading: 'The Question',
        body: [
          'Two weeks before a release, ten features are still only partially tested. Time allows thoroughly covering three. Which three, and on what basis?',
        ],
      },
      {
        heading: 'The Intuition',
        body: [
          'The instinct is to keep testing until the team feels certain — as if enough hours of testing eventually produce a provably safe release.',
        ],
      },
      {
        heading: 'The Hidden Problem',
        body: [
          'Complete certainty is not available for any nontrivial system; the space of inputs, environments, and interactions is too large to exhaust, no matter how much time is spent. Treating every untested path as equally risky also wastes the limited time available, because failures differ enormously in both how likely they are and how much they would cost if they happened — a team that tests breadth-first, in the order features were built, is implicitly deciding that recency matters more than consequence.',
        ],
      },
      {
        heading: 'A Practical Model',
        body: [
          'A simple lens for prioritizing attention:',
        ],
        formula: 'Risk ≈ Probability of Failure × Impact',
        formulaNote:
          'A simplified decision aid for comparing priorities, not a precise or universally measurable calculation — probability and impact are usually estimated qualitatively, not computed.',
        comparison: {
          note: 'A small illustrative comparison of two competing priorities under the same deadline.',
          left: {
            label: 'A rarely used settings toggle',
            body: 'A cosmetic display bug. Low probability of being hit, low impact if it is. Lower priority even though it is easy to test.',
          },
          right: {
            label: 'A data-export feature',
            body: 'An uncommon encoding edge case. Lower probability than the toggle bug, but the impact of silently corrupted exported data is severe — it deserves disproportionate attention.',
          },
        },
      },
      {
        heading: 'The Engineering Decision',
        body: [
          'Treat limited testing time as an allocation problem: spend it where probability times impact is highest, and where the team is currently most uncertain — testing something already well understood adds little new information, while testing a genuinely uncertain, high-impact area adds a lot. This is also where leadership communication matters: naming the priority order out loud, and why, turns an implicit gamble into a decision the team can review and disagree with. Whatever remains untested should be stated plainly as residual risk, not implied away by a passing test run.',
        ],
      },
      {
        heading: 'The Takeaway',
        body: [
          'A good release decision does not require zero uncertainty; it requires understanding which uncertainty matters most. Risk ≈ Probability × Impact is a useful way to compare priorities in conversation — it is not a complete or precise model of release risk, and real decisions still require judgment about impacts and probabilities that resist clean measurement.',
        ],
      },
    ],
  },
  {
    id: 'ai-verification',
    category: 'AI-ASSISTED ENGINEERING',
    icon: 'Sparkles',
    title: 'The Verification Paradox of AI',
    question: 'What happens when generating code becomes faster than verifying it?',
    insight: 'When producing solutions becomes cheap, the ability to distinguish reliable ones becomes more valuable.',
    sections: [
      {
        heading: 'The Question',
        body: [
          'An AI assistant produces a working-looking function in seconds. Shipping it takes one more step: deciding whether "working-looking" is the same as "correct."',
        ],
      },
      {
        heading: 'The Intuition',
        body: [
          'Faster code generation reads as a straightforward win — if writing code takes less time, delivery should simply speed up.',
        ],
      },
      {
        heading: 'The Hidden Problem',
        body: [
          'Producing plausible code is not the same as establishing correctness. A generated function can be fluent, idiomatic, and confidently wrong in a way that is easy to miss on a quick read — AI changes the relative cost of implementation and review far more than it changes the cost of verification itself. When generation gets dramatically cheaper and verification does not, verification becomes the real bottleneck, and convincing-but-incorrect output becomes more likely to slip through specifically because it looks authoritative.',
        ],
      },
      {
        heading: 'A Practical Model',
        body: [
          'Two ways of using the same AI assistant on the same task.',
        ],
        comparison: {
          note: 'An illustrative contrast between two workflows, not a general claim that one is always correct.',
          left: {
            label: 'Fast generation, weak validation',
            body: 'Accept the output, skim it for obvious problems, ship. Review effort does not scale with how much code was generated.',
          },
          right: {
            label: 'AI-assisted iteration with verification gates',
            body: 'Generate, then explicitly check against requirements, require tests for the new logic, and focus human review on the highest-risk parts rather than re-reading everything line by line.',
          },
        },
      },
      {
        heading: 'The Engineering Decision',
        body: [
          'Design the workflow so verification capacity does not lag generation capacity: keep requirements explicit enough to check against, maintain real test coverage for AI-assisted changes, use architecture and interfaces that limit the blast radius of a wrong suggestion, and reserve careful human attention for the decisions that are hardest to verify automatically. AI does not remove the need for tests, requirements, and review — it changes how that effort should be allocated.',
        ],
      },
      {
        heading: 'The Takeaway',
        body: [
          'When producing solutions becomes cheap, the ability to distinguish reliable solutions becomes more valuable. This does not mean AI-assisted development always increases total verification cost — for well-scoped tasks with good tests and tooling already in place, it can be faster and safer than before. The outcome depends on task complexity, the quality of the generated output, and whether review practices actually keep pace with generation speed.',
        ],
      },
    ],
  },
]
