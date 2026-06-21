# Requirements & Traceability Matrix

Portfolio QA project — full requirements coverage.

---

## Requirements Index

| ID | Title | Category | Priority | Tests |
|----|-------|----------|----------|-------|
| [REQ-001](REQ-001-smoke.md) | Page Load & Core Rendering | Smoke | Critical | TC-001-1 … TC-001-5 |
| [REQ-002](REQ-002-navigation.md) | Navigation Links | Navigation | High | TC-002-1 … TC-002-4 |
| [REQ-003](REQ-003-content.md) | Page Content & Data Rendering | Content | High | TC-003-1 … TC-003-6 |
| [REQ-004](REQ-004-responsive.md) | Responsive Layout (Mobile) | Responsive | High | TC-004-1 … TC-004-2 |
| [REQ-005](REQ-005-performance.md) | Page Load Performance | Performance | Medium | TC-005-1 |
| [REQ-006](REQ-006-accessibility.md) | Accessibility (WCAG 2.1 AA) | Accessibility | High | TC-006-1 … TC-006-2 |
| [REQ-007](REQ-007-deployment.md) | Production Deployment Verification | Deployment | Critical | TC-007-1 … TC-007-3 |

---

## Full Traceability Matrix

| Test ID | Test Name | REQ | Acceptance Criteria |
|---------|-----------|-----|---------------------|
| TC-001-1 | `test_page_loads_with_correct_title` | REQ-001 | AC-001-1, AC-001-2, AC-001-3 |
| TC-001-2 | `test_hero_heading_displays_name` | REQ-001 | AC-001-4 |
| TC-001-3 | `test_navigation_is_present` | REQ-001 | AC-001-5 |
| TC-001-4 | `test_page_has_no_javascript_errors` | REQ-001 | AC-001-6 |
| TC-001-5 | `test_react_app_hydrated_successfully` | REQ-001 | AC-001-7, AC-001-8 |
| TC-002-1 | `test_nav_link_is_visible_with_correct_href[About-#about]` | REQ-002 | AC-002-1, AC-002-2 |
| TC-002-2 | `test_nav_link_is_visible_with_correct_href[Skills-#skills]` | REQ-002 | AC-002-3, AC-002-4 |
| TC-002-3 | `test_nav_link_is_visible_with_correct_href[Projects-#projects]` | REQ-002 | AC-002-5, AC-002-6 |
| TC-002-4 | `test_nav_link_is_visible_with_correct_href[Contact-#contact]` | REQ-002 | AC-002-7, AC-002-8 |
| TC-003-1 | `test_skills_section_contains_core_stack[Python]` | REQ-003 | AC-003-1 |
| TC-003-2 | `test_skills_section_contains_core_stack[Playwright]` | REQ-003 | AC-003-2 |
| TC-003-3 | `test_skills_section_contains_core_stack[pytest]` | REQ-003 | AC-003-3 |
| TC-003-4 | `test_projects_section_has_expected_cards` | REQ-003 | AC-003-4 |
| TC-003-5 | `test_contact_section_has_required_channels` | REQ-003 | AC-003-5 |
| TC-003-6 | `test_test_results_section_renders` | REQ-003 | AC-003-6, AC-003-7, AC-003-8 |
| TC-004-1 | `test_mobile_viewport_no_horizontal_scroll` | REQ-004 | AC-004-1 |
| TC-004-2 | `test_mobile_hero_section_visible` | REQ-004 | AC-004-2 |
| TC-005-1 | `test_page_load_time_within_budget` | REQ-005 | AC-005-1 |
| TC-006-1 | `test_images_have_alt_text` | REQ-006 | AC-006-1 |
| TC-006-2 | `test_headings_hierarchy_is_correct` | REQ-006 | AC-006-2, AC-006-3, AC-006-4 |
| TC-007-1 | `test_assets_load_on_github_pages` | REQ-007 | AC-007-1, AC-007-2, AC-007-3 |
| TC-007-2 | `test_base_path_is_correct` | REQ-007 | AC-007-4 |
| TC-007-3 | `test_no_console_errors_on_production` | REQ-007 | AC-007-5 |

---

## Coverage Summary

| Category | Requirements | Acceptance Criteria | Tests | Coverage |
|----------|-------------|--------------------|----|---------|
| Smoke | 1 | 8 | 5 | 100% |
| Navigation | 1 | 8 | 4 | 100% |
| Content | 1 | 8 | 6 | 100% |
| Responsive | 1 | 2 | 2 | 100% |
| Performance | 1 | 1 | 1 | 100% |
| Accessibility | 1 | 4 | 2 | 100% |
| Deployment | 1 | 5 | 3 | 100% |
| **Total** | **7** | **36** | **23** | **100%** |
