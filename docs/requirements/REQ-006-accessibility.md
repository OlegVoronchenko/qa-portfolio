# REQ-006 — Accessibility (WCAG 2.1 AA)

**Category:** Accessibility  
**Priority:** High  
**Status:** Active  

---

## Requirement

The portfolio must meet baseline WCAG 2.1 Level AA
accessibility requirements. All images must have
descriptive alternative text. Heading elements must
follow a logical hierarchy with no skipped levels
and exactly one `<h1>` per page.

---

## Acceptance Criteria

### AC-006-1 — All non-decorative images have alt text
Every `<img>` element that is not marked as decorative
(`aria-hidden="true"`) must have an `alt` attribute
with a non-empty, non-whitespace value.

Decorative images (visitor counter badge) are explicitly
excluded via `aria-hidden="true"` and are not checked.

Measured by JavaScript evaluation:
```javascript
Array.from(document.querySelectorAll('img'))
  .filter(img =>
    img.getAttribute('aria-hidden') !== 'true'
    && (!img.alt || img.alt.trim() === '')
  )
```
Result must be an empty array `[]`.

WCAG reference: Success Criterion 1.1.1 Non-text Content (Level A)

### AC-006-2 — Exactly one h1 element on the page
`document.querySelectorAll('h1').length` must equal `1`.  
Defined in: `qa/constants.py → ExpectedCounts.H1_HEADINGS = 1`

WCAG reference: Best practice for document structure;
also required by most SEO guidelines.

### AC-006-3 — h1 appears before the first h2
The DOM position of the `<h1>` element must precede
the first `<h2>` element in document order.

### AC-006-4 — No heading levels are skipped
For each consecutive pair of headings `(h[n], h[n+1])`,
the level difference must not exceed 1.  
Example violations: `h1 → h3` (skips h2), `h2 → h4` (skips h3).

WCAG reference: Success Criterion 1.3.1 Info and Relationships (Level A)

---

## Linked Tests

| Test ID | Test Name | Covers |
|---------|-----------|--------|
| TC-006-1 | `test_images_have_alt_text` | AC-006-1 |
| TC-006-2 | `test_headings_hierarchy_is_correct` | AC-006-2, AC-006-3, AC-006-4 |

---

## Out of Scope

- Colour contrast ratio (WCAG 1.4.3)
- Keyboard navigation and focus order
- ARIA landmark completeness
- Screen reader testing (NVDA, VoiceOver)
- Form label association (no forms in this portfolio)
