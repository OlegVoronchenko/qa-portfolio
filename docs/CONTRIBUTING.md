# Code Standards & Review Checklist

## Before Every Commit

Run these checks locally:

```bash
python scripts/check_hardcoded.py
python scripts/check_test_standards.py
npm run build
```

## React Component Standards

### Data must come from profile.json

```jsx
const profile = useProfile()
<h1>{profile.personal.name}</h1>     // correct
<h1>Oleg Voronchenko</h1>            // FORBIDDEN
```

### No hardcoded contact info

```jsx
{profile.contact.email}              // correct
"oleg.v.qa@gmail.com"               // FORBIDDEN in JSX
```

### No hardcoded stats

```jsx
{profile.stats.years_experience}     // correct
"15+ years"                          // FORBIDDEN in JSX
```

### No hardcoded tool names in skill cards

```jsx
{profile.tools.map(t => t.items)}    // correct
["Java", "Selenium", "Appium"]       // FORBIDDEN in JSX
```

## Test Standards

### Every test must have:

- Docstring explaining what is verified
- `@pytest.mark.{category}` decorator
- AAA pattern (Arrange / Act / Assert)
- Descriptive assertion message with actual vs expected
- At least one screenshot at assertion point

### Every assertion must show values:

```python
assert "Oleg" in title, \            # correct
    f"Expected 'Oleg' in title, got: '{title}'"

assert is_visible()                  # WRONG (no message)
```

### No hardcoded URLs in tests:

```python
portfolio.navigate()                 # correct (uses CONFIG)
page.goto("localhost:8080")         # FORBIDDEN
```

### Locator priority:

```
get_by_role()     <- always first
get_by_text()     <- second
get_by_label()    <- third
CSS id (#section) <- acceptable
CSS class         <- FORBIDDEN
XPath             <- FORBIDDEN
```

## Pull Request Checklist

- [ ] `check_hardcoded.py` passes
- [ ] `check_test_standards.py` passes
- [ ] `npm run build` succeeds
- [ ] All tests pass locally
- [ ] No new hardcoded strings in React components
- [ ] New tests have docstrings and marks
- [ ] `profile.default.json` updated if new data fields added
