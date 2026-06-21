# REQ-005 — Page Load Performance

**Category:** Performance  
**Priority:** Medium  
**Status:** Active  

---

## Requirement

The portfolio page must complete its full load cycle within
a defined time budget. Load time is measured using the
browser Navigation Timing API as the difference between
`performance.timing.loadEventEnd` and
`performance.timing.navigationStart`.

---

## Acceptance Criteria

### AC-005-1 — Full page load completes under 3000ms
The value of `loadEventEnd - navigationStart` must be
less than `3000` milliseconds.  

Budget defined in:
```
qa/constants.py → PerformanceBudget.MAX_LOAD_TIME_MS = 3000
```

Rationale: Google's research shows that pages loading over
3 seconds lose a significant portion of mobile visitors.
A QA portfolio page has no excuse for being slow — it is
a static site with no server-side rendering.

Measurement method:
```python
timing = page.evaluate('JSON.stringify(performance.timing)')
load_ms = timing['loadEventEnd'] - timing['navigationStart']
assert load_ms < 3000
```

---

## Linked Tests

| Test ID | Test Name | Covers |
|---------|-----------|--------|
| TC-005-1 | `test_page_load_time_within_budget` | AC-005-1 |

---

## Notes

- Test runs against the local `dist/` build served on port 8080
- CI environment (GitHub Actions, Linux) may differ from
  production CDN delivery times
- Network latency to external resources (Unsplash images,
  hits badge) is excluded from the measurement
- If this test becomes flaky, consider increasing budget to
  5000ms for CI and keeping 3000ms for production monitoring

---

## Out of Scope

- Core Web Vitals (LCP, FID, CLS)
- Time to First Byte (TTFB)
- Performance under slow network conditions (3G simulation)
