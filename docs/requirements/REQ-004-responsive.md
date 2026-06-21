# REQ-004 — Responsive Layout (Mobile)

**Category:** Responsive  
**Priority:** High  
**Status:** Active  

---

## Requirement

The portfolio must be fully usable on a mobile viewport
of 390×844 pixels (iPhone 14). No horizontal scrollbar
must appear and the hero heading must remain visible
without zooming or scrolling horizontally.

---

## Acceptance Criteria

### AC-004-1 — No horizontal overflow at 390px width
At viewport size 390×844, `document.documentElement.scrollWidth`
must not exceed `window.innerWidth` (390px).  
Rationale: Horizontal scroll on mobile is a critical UX failure.
Any overflow means a layout element has a fixed width wider
than the viewport.

### AC-004-2 — Hero h1 heading is visible at 390px
At viewport size 390×844, the element located by
`get_by_role('heading', level=1)` must return `is_visible() == True`.  
Rationale: The hero heading is the first thing a recruiter sees.
If it is hidden or pushed off-screen on mobile, the portfolio
fails its primary purpose on the most common device type.

---

## Linked Tests

| Test ID | Test Name | Covers |
|---------|-----------|--------|
| TC-004-1 | `test_mobile_viewport_no_horizontal_scroll` | AC-004-1 |
| TC-004-2 | `test_mobile_hero_section_visible` | AC-004-2 |

---

## Test Viewport Configuration

```
Width:  390px  (iPhone 14 logical pixels)
Height: 844px  (iPhone 14 logical pixels)
Defined in: qa/config.py → CONFIG.mobile_width / mobile_height
```

---

## Out of Scope

- Tablet viewports (768px, 1024px)
- Landscape orientation
- Touch interaction behaviour
- Font scaling / dynamic type
