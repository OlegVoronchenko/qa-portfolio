# Requirements & Traceability Matrix

Portfolio QA project — full requirements coverage.

---

## Requirements Index

| ID | Title | Category | Priority | Tests |
|----|-------|----------|----------|-------|
| [REQ-001](REQ-001-smoke.md) | Page Load & Core Rendering | Smoke | Critical | TC-001-1 … TC-001-5 |
| [REQ-002](REQ-002-navigation.md) | Navigation Links | Navigation | High | TC-002-1 … TC-002-6 |
| [REQ-003](REQ-003-content.md) | Page Content & Data Rendering | Content | High | TC-003-1 … TC-003-9 |
| [REQ-004](REQ-004-responsive.md) | Responsive Layout (Mobile) | Responsive | High | TC-004-1 … TC-004-2 |
| [REQ-005](REQ-005-performance.md) | Page Load Performance | Performance | Medium | TC-005-1 |
| [REQ-006](REQ-006-accessibility.md) | Accessibility (WCAG 2.1 AA) | Accessibility | High | TC-006-1 … TC-006-2 |
| [REQ-007](REQ-007-deployment.md) | Production Deployment Verification | Deployment | Critical | TC-007-1 … TC-007-3 |
| [REQ-008](REQ-008-how-i-think.md) | How I Think | How I Think | High | TC-008-1 … TC-008-12 |

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
| TC-002-5 | `test_nav_link_is_visible_with_correct_href[Experience-#experience]` | REQ-002 | AC-002-9, AC-002-10 |
| TC-002-6 | `test_nav_link_is_visible_with_correct_href[Thinking-#how-i-think]` | REQ-002 | AC-002-11, AC-002-12 |
| TC-003-1 | `test_skills_section_contains_core_stack[Python]` | REQ-003 | AC-003-1 |
| TC-003-2 | `test_skills_section_contains_core_stack[Playwright (familiarity)]` | REQ-003 | AC-003-2 |
| TC-003-3 | `test_skills_section_contains_core_stack[pytest]` | REQ-003 | AC-003-3 |
| TC-003-4 | `test_projects_section_has_expected_cards` | REQ-003 | AC-003-4 |
| TC-003-5 | `test_contact_section_has_required_channels` | REQ-003 | AC-003-5 |
| TC-003-6 | `test_test_results_section_renders` | REQ-003 | AC-003-6, AC-003-7, AC-003-8 |
| TC-003-7 | `test_experience_section_shows_all_roles` | REQ-003 | AC-003-9 |
| TC-003-8 | `test_cv_download_link_matches_manifest` | REQ-003 | AC-003-10 |
| TC-003-9 | `test_experience_entry_can_expand_additional_achievements` | REQ-003 | AC-003-11 |
| TC-004-1 | `test_mobile_viewport_no_horizontal_scroll` | REQ-004 | AC-004-1 |
| TC-004-2 | `test_mobile_hero_section_visible` | REQ-004 | AC-004-2 |
| TC-005-1 | `test_page_load_time_within_budget` | REQ-005 | AC-005-1 |
| TC-006-1 | `test_images_have_alt_text` | REQ-006 | AC-006-1 |
| TC-006-2 | `test_headings_hierarchy_is_correct` | REQ-006 | AC-006-2, AC-006-3, AC-006-4 |
| TC-007-1 | `test_assets_load_on_github_pages` | REQ-007 | AC-007-1, AC-007-2, AC-007-3 |
| TC-007-2 | `test_base_path_is_correct` | REQ-007 | AC-007-4 |
| TC-007-3 | `test_no_console_errors_on_production` | REQ-007 | AC-007-5 |
| TC-008-1 | `test_how_i_think_section_is_visible` | REQ-008 | AC-008-1 |
| TC-008-2 | `test_how_i_think_shows_exactly_three_cards` | REQ-008 | AC-008-2 |
| TC-008-3 | `test_how_i_think_card_shows_correct_category_and_title[0]` | REQ-008 | AC-008-3 |
| TC-008-4 | `test_how_i_think_card_shows_correct_category_and_title[1]` | REQ-008 | AC-008-3 |
| TC-008-5 | `test_how_i_think_card_shows_correct_category_and_title[2]` | REQ-008 | AC-008-3 |
| TC-008-6 | `test_how_i_think_card_starts_collapsed` | REQ-008 | AC-008-4 |
| TC-008-7 | `test_how_i_think_card_expands_on_activation` | REQ-008 | AC-008-5 |
| TC-008-8 | `test_how_i_think_accordion_collapses_previous_card` | REQ-008 | AC-008-6 |
| TC-008-9 | `test_how_i_think_experiment_reveals_on_selection[0]` | REQ-008 | AC-008-7 |
| TC-008-10 | `test_how_i_think_experiment_reveals_on_selection[1]` | REQ-008 | AC-008-7 |
| TC-008-11 | `test_how_i_think_experiment_reveals_on_selection[2]` | REQ-008 | AC-008-7 |
| TC-008-12 | `test_how_i_think_ai_experiment_shows_corrected_code` | REQ-008 | AC-008-8 |

---

## Coverage Summary

| Category | Requirements | Acceptance Criteria | Tests | Coverage |
|----------|-------------|--------------------|----|---------|
| Smoke | 1 | 8 | 5 | 100% |
| Navigation | 1 | 12 | 6 | 100% |
| Content | 1 | 11 | 9 | 100% |
| Responsive | 1 | 2 | 2 | 100% |
| Performance | 1 | 1 | 1 | 100% |
| Accessibility | 1 | 4 | 2 | 100% |
| Deployment | 1 | 5 | 3 | 100% |
| How I Think | 1 | 8 | 12 | 100% |
| **Total** | **8** | **51** | **40** | **100%** |
