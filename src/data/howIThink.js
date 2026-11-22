/**
 * How I Think: Approved Article Content
 * =======================================
 *
 * Three illustrative engineering essays demonstrating analytical
 * thinking and engineering judgment. These are generalized,
 * illustrative scenarios, not claims about specific employers,
 * clients, or historical projects.
 *
 * The wording and reasoning below are the approved canonical content
 * for this section. Only formatting, line breaks, semantic HTML, and
 * presentation-specific labels (e.g. section id, icon key) should be
 * adapted when rendering this data; the prose itself should not be
 * rewritten. See scripts/validate_how_i_think_content.mjs, which
 * checks for accidental replacement and a few deterministic content
 * rules (no em/en dashes, no employer names, etc).
 *
 * Pure data only, no JSX, so content can be reviewed independently
 * of src/components/HowIThink.jsx. `icon` is a string key resolved to
 * a lucide-react component by the consuming component.
 *
 * Each article is a short opening hook (no heading) followed by its
 * own named sections, deliberately not a uniform template, since a
 * repeated structure across all three would read as formulaic.
 *
 * A section's `blocks` is an ordered list of typed content pieces:
 *   { type: 'p', text }              - a paragraph
 *   { type: 'formula', text }        - a short highlighted formula line
 *   { type: 'choices', items }       - a lettered list of options (prose)
 *   { type: 'quote', text }          - a short quoted requirement/line
 *   { type: 'code', label, language, snippet } - a code sample
 *   { type: 'list', items }          - a plain bullet list
 */

export const HOW_I_THINK_ARTICLES = [
  {
    id: 'automation-architecture',
    category: 'AUTOMATION ARCHITECTURE',
    icon: 'Layers',
    title: 'Why More Tests Can Mean Less Confidence',
    excerpt: 'What if 8,000 of those tests are checking almost the same thing?',
    description:
      "A green dashboard tells us the tests passed. It doesn't tell us how much of the system we actually understand.",
    opening: [
      '10,000 tests passed. Zero failures. Beautiful dashboard.',
      'Time to celebrate?',
      'Maybe. But first, a question.',
      'What if 8,000 of those tests are checking almost the same thing?',
      "A green dashboard tells us that the tests passed. It doesn't tell us how much of the system we actually understand.",
    ],
    sections: [
      {
        heading: "Let's try something",
        blocks: [
          { type: 'p', text: 'Imagine two test suites.' },
          { type: 'p', text: 'Suite A: 1,000 tests.' },
          { type: 'p', text: "Most exercise variations of a handful of workflows. They're reliable, fast enough, and almost always green." },
          { type: 'p', text: 'Suite B: 200 tests.' },
          { type: 'p', text: 'These cover fewer scenarios, but deliberately explore different failure modes: invalid inputs, API boundaries, state transitions, recovery behavior, and critical user journeys.' },
          { type: 'p', text: 'Which suite would you trust?' },
          { type: 'p', text: "Here's the catch: we don't have enough information to choose." },
          { type: 'p', text: 'Suite A might contain essential regression checks. Suite B might miss an entire business workflow.' },
          { type: 'p', text: 'The numbers alone tell us remarkably little.' },
        ],
      },
      {
        heading: 'The hidden problem',
        blocks: [
          { type: 'p', text: "Tests aren't necessarily independent pieces of evidence." },
          { type: 'p', text: 'A hundred tests can share the same assumptions, test data, dependencies, and blind spots.' },
          { type: 'p', text: 'If an important requirement was misunderstood, all hundred might pass while the product remains wrong.' },
          { type: 'p', text: "That's why I like asking a slightly uncomfortable question:" },
          { type: 'p', text: 'What could still be broken if every test passed?' },
          { type: 'p', text: "It's often more revealing than looking at the pass rate." },
        ],
      },
      {
        heading: 'What changes in practice?',
        blocks: [
          { type: 'p', text: 'I would examine the risks behind the tests, not just their number.' },
          { type: 'p', text: 'Which failures are we trying to detect? Where are the important boundaries? Are we testing behavior or merely repeating implementation assumptions?' },
          { type: 'p', text: 'Some overlap is useful. Critical behavior may deserve multiple checks at different levels.' },
          { type: 'p', text: 'But duplication should have a reason.' },
        ],
      },
      {
        heading: 'One last thought',
        blocks: [
          { type: 'p', text: 'Adding tests can improve confidence. It can also increase maintenance costs without telling us much more.' },
          { type: 'p', text: "The interesting metric isn't how many tests we have." },
          { type: 'p', text: 'It is how much useful evidence they provide.' },
        ],
      },
    ],
  },
  {
    id: 'release-risk',
    category: 'ENGINEERING LEADERSHIP',
    icon: 'Scale',
    title: 'The Mathematics of Release Risk',
    excerpt: 'You have time for one more test. Which one gets your attention?',
    description: "The most valuable test isn't always the one most likely to find a bug.",
    opening: [
      'The release is in an hour. You have time for one more test.',
      'Two candidates remain.',
      'Test A: A feature that occasionally displays the wrong icon.',
      'Test B: A critical transaction that rarely fails, but could cause serious trouble if it does.',
      'Which one gets your attention?',
      'Most engineers would lean toward B.',
      'Now imagine that B takes three hours to execute.',
      'Things just got interesting.',
    ],
    sections: [
      {
        heading: 'Risk has more than one dimension',
        blocks: [
          { type: 'p', text: 'A familiar starting point is:' },
          { type: 'formula', text: 'Risk ≈ Failure Likelihood × Impact' },
          { type: 'p', text: 'Simple. Useful. Incomplete.' },
          { type: 'p', text: 'We rarely know the real probability of failure. We make estimates based on recent changes, defect history, complexity, and whatever evidence we have.' },
          { type: 'p', text: 'And even if we could estimate risk perfectly, we would still need to consider the cost and usefulness of each test.' },
          { type: 'p', text: 'A test that takes five minutes and reveals a critical integration failure might be a great investment.' },
          { type: 'p', text: 'A three-hour test that repeats evidence we already have might not be.' },
        ],
      },
      {
        heading: 'The decision nobody can make for us',
        blocks: [
          { type: 'p', text: "Let's change the scenario." },
          { type: 'p', text: 'You can either:' },
          {
            type: 'choices',
            items: [
              'A. Run a broad regression suite that usually passes.',
              'B. Investigate a recently changed integration that has limited coverage.',
            ],
          },
          { type: 'p', text: 'Neither choice is automatically correct.' },
          { type: 'p', text: "The answer depends on what we know, what we don't know, and how much the result could influence the release decision." },
          { type: 'p', text: 'This is where testing becomes more interesting than checking boxes.' },
          { type: 'p', text: "We're deciding where additional information is worth the time it takes to obtain." },
        ],
      },
      {
        heading: "What I'd want before making the call",
        blocks: [
          { type: 'p', text: "I'd ask what could go wrong, how serious the consequences would be, and which available check could reduce the most important uncertainty." },
          { type: 'p', text: "Then I'd make the remaining risks visible to the people responsible for the release." },
          { type: 'p', text: "A test result can inform a decision. It shouldn't quietly make that decision on everyone's behalf." },
        ],
      },
      {
        heading: 'The surprising part',
        blocks: [
          { type: 'p', text: "The most valuable test isn't always the one most likely to find a bug." },
          { type: 'p', text: "Sometimes it's the one whose result could change what the team decides to do next." },
          { type: 'p', text: "That's where testing starts to look like engineering judgment." },
        ],
      },
    ],
  },
  {
    id: 'ai-verification',
    category: 'AI-ASSISTED ENGINEERING',
    icon: 'Sparkles',
    title: 'The Verification Paradox of AI',
    excerpt: 'Who checked that they were testing the right thing?',
    description: "The problem isn't that the tests failed. It's that the tests agreed with the mistake.",
    opening: [
      'The AI wrote the code. The AI wrote the tests. All tests passed.',
      'Sounds efficient.',
      "But here's a question: who checked that they were testing the right thing?",
    ],
    sections: [
      {
        heading: 'A tiny example',
        blocks: [
          { type: 'p', text: 'Imagine asking an AI assistant to implement a discount rule:' },
          { type: 'quote', text: 'Apply a 10% discount to orders over €100.' },
          { type: 'p', text: 'The assistant writes the implementation:' },
          {
            type: 'code',
            label: 'Generated implementation',
            language: 'javascript',
            snippet: 'function finalPrice(total) {\n  return total >= 100 ? total * 0.9 : total;\n}',
          },
          { type: 'p', text: 'Then it generates a test:' },
          {
            type: 'code',
            label: 'Generated test',
            language: 'javascript',
            snippet: 'expect(finalPrice(100)).toBe(90);',
          },
          { type: 'p', text: 'The test passes.' },
          { type: 'p', text: 'Everything looks fine.' },
          { type: 'p', text: 'Except the requirement says over €100, not €100 or more.' },
          { type: 'p', text: 'The implementation is wrong at the boundary.' },
          { type: 'p', text: 'And the AI-generated test confidently confirms the same mistake.' },
        ],
      },
      {
        heading: 'The interesting problem',
        blocks: [
          { type: 'p', text: "This isn't really about AI being bad at coding." },
          { type: 'p', text: 'Humans make similar mistakes.' },
          { type: 'p', text: 'The difference is that AI can produce a convincing implementation, supporting tests, and a reassuring explanation in seconds.' },
          { type: 'p', text: 'When all three share the same incorrect assumption, they can create a surprisingly persuasive illusion of correctness.' },
          { type: 'p', text: "The problem isn't that the tests failed." },
          { type: 'p', text: "It's that the tests agreed with the mistake." },
        ],
      },
      {
        heading: 'So what changes?',
        blocks: [
          { type: 'p', text: 'When I use AI-assisted development, I want verification to be independent of the assumptions that produced the solution.' },
          { type: 'p', text: 'For example:' },
          {
            type: 'list',
            items: [
              'Define important behavior before implementation.',
              'Check boundaries and negative cases.',
              'Review generated tests against requirements.',
              'Keep changes small enough to understand.',
              'Use independent checks where the risk justifies them.',
            ],
          },
          { type: 'p', text: 'AI can help with these activities too. The important part is not to confuse generated agreement with independent evidence.' },
        ],
      },
      {
        heading: 'The real bottleneck',
        blocks: [
          { type: 'p', text: 'Generating code is becoming easier.' },
          { type: 'p', text: 'Understanding whether that code satisfies the intended behavior still takes engineering work.' },
          { type: 'p', text: 'Sometimes AI reduces that work. Sometimes it creates new things to verify.' },
          { type: 'p', text: "Either way, speed at the keyboard isn't the whole story." },
          { type: 'p', text: "The interesting question isn't how fast we can generate a solution. It is how confidently we can verify it." },
        ],
      },
    ],
  },
]
