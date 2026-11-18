# REQ-003 — Page Content & Data Rendering

**Category:** Content  
**Priority:** High  
**Status:** Active  

---

## Requirement

All portfolio sections must render data sourced from
`profile.json`. The Skills section must display core
technology tags. The Experience section must render every
career entry from `profile.json`. The Projects section must
show exactly 3 project cards. The Contact section must expose
all required contact channels. The Test Results section
must display loaded data from `test_report.json`.

---

## Acceptance Criteria

### AC-003-1 — Skills section displays "Python" tag
A visible element with exact text `'Python'` must exist
inside the `#skills` section.  
Rationale: Python is the primary language for this test suite.

### AC-003-2 — Skills section displays "Playwright (familiarity)" tag
A visible element with exact text `'Playwright (familiarity)'` must
exist inside the `#skills` section.  
Rationale: this matches the professional profile's own stated
experience level. Distinguish this from the separate, true claim
that Playwright is one of the tools used to *build and run this
portfolio's own test suite* (see the Test Results environment
panel) — that is a tooling fact about this repository, not a
commercial-experience claim about the candidate.

### AC-003-3 — Skills section displays "pytest" tag
A visible element with exact text `'pytest'` (lowercase) must
exist inside the `#skills` section.  
Rationale: pytest is the test runner used in this project.

### AC-003-4 — Projects section renders exactly 3 cards
Elements with `role='article'` inside `#projects` must
number exactly 3.  
Rationale: Three real projects are defined in `profile.json`.
Any deviation indicates a data or rendering error.

### AC-003-5 — Contact section renders required channels
The `#contact` section must contain exactly 4 visible links
representing distinct contact channels (email, GitHub, LinkedIn,
Portfolio).

### AC-003-6 — Test results section is visible
The `#test-results` section must be present and visible
without user interaction.

### AC-003-7 — Test results section shows numeric values
The `#test-results` section must contain at least one digit
character after `test_report.json` has been fetched (2000ms
wait). Absence of digits means the JSON failed to load.

### AC-003-8 — Test results section renders at least 1 row
At least one clickable row element must be rendered inside
`#test-results` after the fetch completes.  
Rationale: Empty rows mean `test_report.json` was not deployed
or the fetch URL is using the wrong base path.

### AC-003-9 — Experience section renders all career entries
Elements with `role='article'` inside `#experience` must
number exactly the count of entries in `profile.json`'s
`experience` array (currently 5).  
Rationale: Every documented role must be visible — a mismatch
means an entry was added or removed from `profile.json` without
the component being updated, or vice versa.

### AC-003-10 — Download CV link matches the build-time manifest
The Hero's "Download CV" link must be absent when
`src/data/cv-manifest.json` has no PDF selected, and otherwise
visible with an `href` ending in the manifest's `url` and a
`download` attribute equal to the manifest's `filename`.  
Rationale: the link must never show a stale or placeholder CV —
see scripts/select-cv.mjs for how the manifest is produced.

### AC-003-11 — Experience entries can reveal additional achievements
Any experience entry with more achievements than the default
visible count must expose an "Explore My Impact" control that
toggles `aria-expanded` between `false` and `true` on click.  
Rationale: additional detail must be reachable and its state must
be programmatically determinable for assistive technology.

---

## Linked Tests

| Test ID | Test Name | Covers |
|---------|-----------|--------|
| TC-003-1 | `test_skills_section_contains_core_stack[Python]` | AC-003-1 |
| TC-003-2 | `test_skills_section_contains_core_stack[Playwright (familiarity)]` | AC-003-2 |
| TC-003-3 | `test_skills_section_contains_core_stack[pytest]` | AC-003-3 |
| TC-003-4 | `test_projects_section_has_expected_cards` | AC-003-4 |
| TC-003-5 | `test_contact_section_has_required_channels` | AC-003-5 |
| TC-003-6 | `test_test_results_section_renders` | AC-003-6, AC-003-7, AC-003-8 |
| TC-003-7 | `test_experience_section_shows_all_roles` | AC-003-9 |
| TC-003-8 | `test_cv_download_link_matches_manifest` | AC-003-10 |
| TC-003-9 | `test_experience_entry_can_expand_additional_achievements` | AC-003-11 |

---

## Out of Scope

- Visual design of cards or tags
- Accuracy of contact link destinations
- Content of individual project descriptions
