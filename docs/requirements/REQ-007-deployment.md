# REQ-007 — Production Deployment Verification

**Category:** Deployment  
**Priority:** Critical  
**Status:** Active  

---

## Requirement

After every deployment to GitHub Pages, the production
URL must be verified to confirm that all static assets
load without 404 errors, all asset paths include the
correct repository base path prefix, and the browser
console is free of JavaScript errors.

These tests run exclusively in CI after the deploy step,
against the live URL:
`https://olegvoronchenko.github.io/qa-portfolio/`

They are skipped locally when `GITHUB_PAGES_URL` is not set.

---

## Acceptance Criteria

### AC-007-1 — No JS/CSS/image assets return 404
During page load, no network response for files with
extensions `.js`, `.css`, `.png`, `.jpg`, `.woff`, `.woff2`
must return HTTP status 404.

Excluded from this check (expected to be optional):
- `test_report.json`
- `version.txt`
- `favicon.ico`

Defined in:
```
qa/constants.py → DeploymentConfig.CHECKED_ASSET_EXTENSIONS
qa/constants.py → DeploymentConfig.EXCLUDED_404_PATHS
```

Rationale: A 404 for a JS or CSS file means the Vite base
path was not set correctly during the CI build, or a file
was not included in the deployment.

### AC-007-2 — Navigation is visible on production URL
After loading `GITHUB_PAGES_URL` with `wait_until='networkidle'`,
an element with ARIA role `navigation` must exist (`count > 0`)
and be visible (`is_visible() == True`).  
Rationale: Confirms React hydrated on the live site, not just
in local test environment.

### AC-007-3 — Exactly one h1 with non-empty text on production
The production page must have exactly 1 element with
`role='heading' level=1` and its `inner_text()` must not
be empty or whitespace-only.  
Rationale: Empty h1 means the page loaded but React did not
render content — hydration succeeded structurally but data
failed to load.

### AC-007-4 — All asset src/href use the repo base path
No `<script src>` or `<link href>` attribute on the production
page may start with `/assets/` without the `/qa-portfolio/`
prefix. All paths must start with `/qa-portfolio/assets/`.

Measured by:
```javascript
document.querySelectorAll('script[src], link[href]')
  .forEach(el => {
    const val = el.getAttribute('src') || el.getAttribute('href')
    if (val && val.startsWith('/assets/')) bad.push(val)
  })
```
Result must be an empty array `[]`.

Rationale: This is the most common deployment failure for
Vite apps on GitHub Pages — base path not injected at build time.

### AC-007-5 — No JavaScript errors on production
The `pageerror` event must not fire during or after loading
the production URL. Error list must be empty `[]`.  
Rationale: Production JS environment may differ from local
(different env variables, CDN caching, browser version on
GitHub Actions runner).

---

## Linked Tests

| Test ID | Test Name | Covers |
|---------|-----------|--------|
| TC-007-1 | `test_assets_load_on_github_pages` | AC-007-1, AC-007-2, AC-007-3 |
| TC-007-2 | `test_base_path_is_correct` | AC-007-4 |
| TC-007-3 | `test_no_console_errors_on_production` | AC-007-5 |

---

## Environment

```
GITHUB_PAGES_URL: https://olegvoronchenko.github.io/qa-portfolio/
Runs:             CI only (after deploy step in workflow)
Skipped locally:  Yes — when GITHUB_PAGES_URL is not set
```

---

## Out of Scope

- SSL certificate validity
- DNS resolution time
- CDN cache behaviour
- Cross-browser compatibility on production
