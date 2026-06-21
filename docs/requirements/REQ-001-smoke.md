# REQ-001 — Page Load & Core Rendering

**Category:** Smoke  
**Priority:** Critical  
**Status:** Active  

---

## Requirement

The portfolio site must load successfully in a browser,
display the engineer's identity in the browser tab title,
render the hero heading, show a visible navigation bar,
produce no JavaScript errors on load, and confirm that
the React application has fully hydrated into the DOM.

---

## Acceptance Criteria

### AC-001-1 — Browser tab title contains engineer name
The `<title>` element must contain the string `'Oleg'`.  
Rationale: Identifies the owner of the portfolio at a glance.

### AC-001-2 — Browser tab title contains role keyword
The `<title>` element must contain the string `'Automation'`.  
Rationale: Communicates specialisation without opening the page.

### AC-001-3 — Browser tab title contains role type
The `<title>` element must contain the string `'Engineer'`.  
Rationale: Completes the professional identity in the tab.

### AC-001-4 — Hero h1 heading contains engineer name
The first `<h1>` element located by ARIA role `heading level=1`
must contain the string `'Oleg'`.  
Rationale: First visible element must identify the engineer.

### AC-001-5 — Navigation landmark is visible on load
An element with ARIA role `navigation` must exist and be
visible without any user interaction.  
Rationale: Navigation must be immediately accessible.

### AC-001-6 — No uncaught JavaScript exceptions on load
The browser `pageerror` event must not fire during or after
page load. The collected error list must be empty `[]`.  
Rationale: JS errors indicate broken functionality or
missing assets that degrade user experience.

### AC-001-7 — React app renders content into #root
The `#root` element must have at least 1 child element after
page load, confirming React hydrated successfully.  
Rationale: Empty `#root` means the JS bundle failed to execute.

### AC-001-8 — No React error boundary rendered
No element matching `[data-react-error]` must be present.  
Rationale: Error boundary means React crashed during render.

---

## Linked Tests

| Test ID | Test Name | Covers |
|---------|-----------|--------|
| TC-001-1 | `test_page_loads_with_correct_title` | AC-001-1, AC-001-2, AC-001-3 |
| TC-001-2 | `test_hero_heading_displays_name` | AC-001-4 |
| TC-001-3 | `test_navigation_is_present` | AC-001-5 |
| TC-001-4 | `test_page_has_no_javascript_errors` | AC-001-6 |
| TC-001-5 | `test_react_app_hydrated_successfully` | AC-001-7, AC-001-8 |

---

## Out of Scope

- Content accuracy of the title (covered by REQ-003)
- Navigation link destinations (covered by REQ-002)
- Visual appearance of the hero section
