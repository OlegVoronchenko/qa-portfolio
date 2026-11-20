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
full article in place. The section must be reachable from the
primary navigation.

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

The "Thinking" navigation link itself is covered under REQ-002
(AC-002-11, AC-002-12), consistent with how every other section's
nav link is tested as a navigation concern, not a content concern.

---

## Out of Scope

- Exact wording/editorial review of article prose (reviewed manually at authoring time, not asserted character-for-character)
- Visual design of the comparison/formula blocks
- Reduced-motion and mobile-layout behavior, verified manually (see Phase 2 final report) rather than as a permanent pytest assertion, consistent with how reduced-motion is handled elsewhere in this suite
