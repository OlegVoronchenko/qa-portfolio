# REQ-002 — Navigation Links

**Category:** Navigation  
**Priority:** High  
**Status:** Active  

---

## Requirement

The navigation bar must contain six visible links — About,
Experience, Thinking, Skills, Projects, and Contact — each
pointing to the correct anchor section on the same page via an
`href` attribute.

---

## Acceptance Criteria

### AC-002-1 — "About" link is visible in navbar
A link with accessible name `'About'` inside the `navigation`
landmark must be visible on screen.

### AC-002-2 — "About" link href equals `#about`
The `href` attribute of the About link must equal `'#about'`
exactly (case-sensitive).

### AC-002-3 — "Skills" link is visible in navbar
A link with accessible name `'Skills'` inside the `navigation`
landmark must be visible on screen.

### AC-002-4 — "Skills" link href equals `#skills`
The `href` attribute of the Skills link must equal `'#skills'`.

### AC-002-5 — "Projects" link is visible in navbar
A link with accessible name `'Projects'` inside the `navigation`
landmark must be visible on screen.

### AC-002-6 — "Projects" link href equals `#projects`
The `href` attribute of the Projects link must equal `'#projects'`.

### AC-002-7 — "Contact" link is visible in navbar
A link with accessible name `'Contact'` inside the `navigation`
landmark must be visible on screen.

### AC-002-8 — "Contact" link href equals `#contact`
The `href` attribute of the Contact link must equal `'#contact'`.

### AC-002-9 — "Experience" link is visible in navbar
A link with accessible name `'Experience'` inside the `navigation`
landmark must be visible on screen.

### AC-002-10 — "Experience" link href equals `#experience`
The `href` attribute of the Experience link must equal
`'#experience'` exactly.

### AC-002-11 — "Thinking" link is visible in navbar
A link with accessible name `'Thinking'` inside the `navigation`
landmark must be visible on screen. This links to the "How I
Think" section (REQ-008); the shortened label keeps the navbar
uncrowded while the section itself keeps its full heading.

### AC-002-12 — "Thinking" link href equals `#how-i-think`
The `href` attribute of the Thinking link must equal
`'#how-i-think'` exactly.

---

## Linked Tests

| Test ID | Test Name | Covers |
|---------|-----------|--------|
| TC-002-1 | `test_nav_link_is_visible_with_correct_href[About-#about]` | AC-002-1, AC-002-2 |
| TC-002-2 | `test_nav_link_is_visible_with_correct_href[Skills-#skills]` | AC-002-3, AC-002-4 |
| TC-002-3 | `test_nav_link_is_visible_with_correct_href[Projects-#projects]` | AC-002-5, AC-002-6 |
| TC-002-4 | `test_nav_link_is_visible_with_correct_href[Contact-#contact]` | AC-002-7, AC-002-8 |
| TC-002-5 | `test_nav_link_is_visible_with_correct_href[Experience-#experience]` | AC-002-9, AC-002-10 |
| TC-002-6 | `test_nav_link_is_visible_with_correct_href[Thinking-#how-i-think]` | AC-002-11, AC-002-12 |

---

## Out of Scope

- Smooth scroll behaviour when link is clicked
- Active state highlighting of current section
- Mobile hamburger menu behaviour
