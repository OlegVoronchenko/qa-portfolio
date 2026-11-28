# REQ-008 — How I Think

**Category:** Content
**Priority:** High
**Status:** Active

---

## Requirement

The portfolio must include a "How I Think" section presenting three
compact, interactive engineering decision scenarios (quality
strategy, engineering decisions under constraints, and AI-assisted
engineering judgment) sourced from `src/data/howIThink.js` and
`src/data/howIThinkExperiments.js`. Each scenario renders as a
compact card showing its category, title, a short two-line hook, and
a CTA, with a native, keyboard-accessible control that reveals the
scenario in place. Only one card may be expanded at a time
(single-open accordion). Expanding a card shows its interactive
decision immediately, no separate long-form article precedes it. The
section must be reachable from the primary navigation.

---

## Acceptance Criteria

### AC-008-1 — "How I Think" section is present and visible
A section with heading text containing `'How I Think'` must be
visible on the page without user interaction.

### AC-008-2 — Exactly 3 scenario cards render
Elements matching the How I Think card locator must number exactly
3, one per entry in `src/data/howIThink.js`.

### AC-008-3 — Each card shows its correct category, title, and CTA
For each of the three scenarios, the collapsed card must display the
exact category label, title text, and CTA label defined in the data
module.

### AC-008-4 — Cards start collapsed
Each card's expand control must report `aria-expanded="false"` on
initial render, and the expanded detail content must not be visible.

### AC-008-5 — Expand control reveals the scenario immediately
Activating a card's CTA must set `aria-expanded="true"`, make that
card's expanded content visible, and show the scenario's answer
options immediately, without affecting the other two cards or
requiring any further interaction to reach the decision.

### AC-008-6 — Expanding a card collapses the previously expanded one
With one card already expanded, activating a different card's
expand control must set that card's `aria-expanded="true"` and
return the first card's control to `aria-expanded="false"` (single-
open accordion, not independent per-card state).

### AC-008-7 — No long-form article content
The section must not render the long-form article prose and named
subsections used by a previous iteration of this section.

### AC-008-8 — Each scenario reveals an explanation on selection
Each card's scenario starts with its reveal panel hidden, including
the AI scenario (the correct answer must not be visible before a
selection is made). Selecting any answer option must make the reveal
panel visible.

### AC-008-9 — The release-risk scenario marks no option as correct
Regardless of which option is selected in the engineering-decisions
scenario, no correctness indicator may appear — this scenario is a
judgment call with legitimate trade-offs, not a graded question.

### AC-008-10 — AI scenario reveals the corrected boundary as correct
Selecting the "boundary condition" option in the AI scenario (the
one scenario with an objectively correct answer) must show a
correctness indicator on that option and reveal the corrected
condition using `total > 100`.

---

## Linked Tests

| Test ID | Test Name | Covers |
|---------|-----------|--------|
| TC-008-1 | `test_how_i_think_section_is_visible` | AC-008-1 |
| TC-008-2 | `test_how_i_think_shows_exactly_three_cards` | AC-008-2 |
| TC-008-3 | `test_how_i_think_card_shows_correct_category_title_and_cta[0]` | AC-008-3 |
| TC-008-4 | `test_how_i_think_card_shows_correct_category_title_and_cta[1]` | AC-008-3 |
| TC-008-5 | `test_how_i_think_card_shows_correct_category_title_and_cta[2]` | AC-008-3 |
| TC-008-6 | `test_how_i_think_card_starts_collapsed` | AC-008-4 |
| TC-008-7 | `test_how_i_think_card_expands_on_activation` | AC-008-5 |
| TC-008-8 | `test_how_i_think_accordion_collapses_previous_card` | AC-008-6 |
| TC-008-9 | `test_how_i_think_no_long_form_article_content` | AC-008-7 |
| TC-008-10 | `test_how_i_think_experiment_reveals_on_selection[0]` | AC-008-8 |
| TC-008-11 | `test_how_i_think_experiment_reveals_on_selection[1]` | AC-008-8 |
| TC-008-12 | `test_how_i_think_experiment_reveals_on_selection[2]` | AC-008-8 |
| TC-008-13 | `test_how_i_think_release_risk_scenario_has_no_correct_answer_marking` | AC-008-9 |
| TC-008-14 | `test_how_i_think_ai_experiment_shows_corrected_code` | AC-008-10 |

The "Thinking" navigation link itself is covered under REQ-002
(AC-002-11, AC-002-12), consistent with how every other section's
nav link is tested as a navigation concern, not a content concern.

---

## Out of Scope

- Exact wording/editorial review of scenario copy (reviewed manually at authoring time, not asserted character-for-character; see also `scripts/validate_how_i_think_content.mjs` for deterministic editorial checks)
- Visual design of the card grid and reveal panels
- Reduced-motion and mobile-layout behavior, verified manually (see implementation report) rather than as a permanent pytest assertion, consistent with how reduced-motion is handled elsewhere in this suite
- Keyboard-interaction and focus-visible verification, verified manually rather than as a permanent pytest assertion, consistent with how these are handled elsewhere in this suite
