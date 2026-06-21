# REQ-003 — Page Content & Data Rendering

**Category:** Content  
**Priority:** High  
**Status:** Active  

---

## Requirement

All portfolio sections must render data sourced from
`profile.json`. The Skills section must display core
technology tags. The Projects section must show exactly
3 project cards. The Contact section must expose all
required contact channels. The Test Results section
must display loaded data from `test_report.json`.

---

## Acceptance Criteria

### AC-003-1 — Skills section displays "Python" tag
A visible element with exact text `'Python'` must exist
inside the `#skills` section.  
Rationale: Python is the primary language for this test suite.

### AC-003-2 — Skills section displays "Playwright" tag
A visible element with exact text `'Playwright'` must exist
inside the `#skills` section.  
Rationale: Playwright is the primary automation tool demonstrated.

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
The `#contact` section must contain at least 3 visible links
representing distinct contact channels (email, GitHub, LinkedIn).

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

---

## Linked Tests

| Test ID | Test Name | Covers |
|---------|-----------|--------|
| TC-003-1 | `test_skills_section_contains_core_stack[Python]` | AC-003-1 |
| TC-003-2 | `test_skills_section_contains_core_stack[Playwright]` | AC-003-2 |
| TC-003-3 | `test_skills_section_contains_core_stack[pytest]` | AC-003-3 |
| TC-003-4 | `test_projects_section_has_expected_cards` | AC-003-4 |
| TC-003-5 | `test_contact_section_has_required_channels` | AC-003-5 |
| TC-003-6 | `test_test_results_section_renders` | AC-003-6, AC-003-7, AC-003-8 |

---

## Out of Scope

- Visual design of cards or tags
- Accuracy of contact link destinations
- Content of individual project descriptions
