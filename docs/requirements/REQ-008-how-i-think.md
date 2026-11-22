# REQ-008 — How I Think

**Category:** Content
**Priority:** High
**Status:** Active

---

## Requirement

The portfolio must include a "How I Think" section presenting three
illustrative engineering essays (automation architecture, engineering
leadership / release risk, and AI-assisted engineering) sourced from
`src/data/howIThink.js`. Each essay renders as a compact card showing
its category, title, central question, and one-sentence insight by
default, with a native, keyboard-accessible control that reveals the
full article in place. Only one card may be expanded at a time
(single-open accordion). Each expanded article includes a small
interactive experiment, sourced from `src/data/howIThinkExperiments.js`,
that lets a visitor pick an answer and reveals an explanation
afterward. The section must be reachable from the primary navigation.

---

## Acceptance Criteria

### AC-008-1 — "How I Think" section is present and visible
A section with heading text containing `'How I Think'` must be
visible on the page without user interaction.

### AC-008-2 — Exactly 3 article cards render
Elements matching the How I Think card locator must number exactly
3, one per entry in `src/data/howIThink.js`.

### AC-008-3 — Each card shows its correct category and title
For each of the three articles, the card must display the exact
category label and title text defined in the data module.

### AC-008-4 — Cards start collapsed
Each card's expand control must report `aria-expanded="false"` on
initial render, and the expanded detail content must not be visible.

### AC-008-5 — Expand control reveals the full article
Activating a card's "Explore Idea" control must set
`aria-expanded="true"` and make that card's expanded detail content
visible, without affecting the other two cards.

### AC-008-6 — Expanding a card collapses the previously expanded one
With one card already expanded, activating a different card's
expand control must set that card's `aria-expanded="true"` and
return the first card's control to `aria-expanded="false"` (single-
open accordion, not independent per-card state).

### AC-008-7 — Each experiment reveals an explanation on selection
Each article's experiment starts with its reveal panel hidden.
Selecting any answer option must make the reveal panel visible.

### AC-008-8 — AI-verification experiment reveals corrected code
Selecting the "boundary condition" option on the AI-verification
experiment must reveal both a corrected code sample using
`total > 100` and a boundary check against exactly €100.

---

## Linked Tests

| Test ID | Test Name | Covers |
|---------|-----------|--------|
| TC-008-1 | `test_how_i_think_section_is_visible` | AC-008-1 |
| TC-008-2 | `test_how_i_think_shows_exactly_three_cards` | AC-008-2 |
| TC-008-3 | `test_how_i_think_card_shows_correct_category_and_title[0]` | AC-008-3 |
| TC-008-4 | `test_how_i_think_card_shows_correct_category_and_title[1]` | AC-008-3 |
| TC-008-5 | `test_how_i_think_card_shows_correct_category_and_title[2]` | AC-008-3 |
| TC-008-6 | `test_how_i_think_card_starts_collapsed` | AC-008-4 |
| TC-008-7 | `test_how_i_think_card_expands_on_activation` | AC-008-5 |
| TC-008-8 | `test_how_i_think_accordion_collapses_previous_card` | AC-008-6 |
| TC-008-9 | `test_how_i_think_experiment_reveals_on_selection[0]` | AC-008-7 |
| TC-008-10 | `test_how_i_think_experiment_reveals_on_selection[1]` | AC-008-7 |
| TC-008-11 | `test_how_i_think_experiment_reveals_on_selection[2]` | AC-008-7 |
| TC-008-12 | `test_how_i_think_ai_experiment_shows_corrected_code` | AC-008-8 |

The "Thinking" navigation link itself is covered under REQ-002
(AC-002-11, AC-002-12), consistent with how every other section's
nav link is tested as a navigation concern, not a content concern.

---

## Out of Scope

- Exact wording/editorial review of article prose (reviewed manually at authoring time, not asserted character-for-character; see also `scripts/validate_how_i_think_content.mjs` for deterministic editorial checks)
- Visual design of the comparison/formula blocks and experiment illustrations
- Reduced-motion and mobile-layout behavior, verified manually (see Phase 2 final report) rather than as a permanent pytest assertion, consistent with how reduced-motion is handled elsewhere in this suite
