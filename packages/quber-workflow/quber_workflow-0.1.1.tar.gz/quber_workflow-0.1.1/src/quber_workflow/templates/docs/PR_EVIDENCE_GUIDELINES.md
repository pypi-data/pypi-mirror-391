# Pull Request Evidence Guidelines

> **Principle:** Test Evidence ≠ Functional Evidence
>
> Unit tests passing is necessary but NOT sufficient to demonstrate acceptance criteria are met.

## Overview

When creating a Pull Request, you must provide **functional evidence** that demonstrates each acceptance criterion is satisfied through **real usage examples**, not just test results.

## Why This Matters

**Problem:** "All tests pass ✓" doesn't prove the feature works in production.

**Solution:** Show the feature working with real data, real workflows, and real usage patterns.

---

## Evidence Standards

### ❌ Insufficient Evidence

```markdown
## Test Evidence

### AC1: JSON loader successfully loads table data
- ✅ test_load_tables_success PASSED
- ✅ test_load_file_not_found PASSED

### AC2: All unit tests pass
```bash
$ pytest tests/
======================== 50 passed ========================
```
```

**Why insufficient:**
- Doesn't show the feature actually works with production data
- Only proves test fixtures pass
- No demonstration of real-world usage
- No proof downstream workflows work

---

### ✅ Sufficient Evidence

```markdown
## Functional Evidence

### AC1: [Your specific acceptance criterion]

**Real Example: [Demonstrating the feature with realistic data]**

```python
# Code showing the feature working with production/realistic data
# Include concrete, measurable results
```

**Results:**
- ✓ [Specific outcome with measurable details]
- ✓ [File names, sizes, counts - whatever is relevant]
- ✓ [Sample output showing it works]

**Note:** The format above is generic. See "Examples of Good Evidence" section below for real examples from PR #59 and #60.
```

**Why sufficient:**
- Shows feature works with REAL production/realistic data
- Demonstrates ACTUAL usage patterns relevant to the feature
- Proves functionality meets acceptance criteria
- Provides concrete examples anyone can verify

---

## Evidence Requirements by Acceptance Criteria Type

### 1. Feature Functionality

**Generic Requirements:**
- ✅ Demonstrate with REAL production/realistic data (not test fixtures)
- ✅ Show concrete, measurable results relevant to the feature
- ✅ Display sample output that proves it works
- ✅ Verify data/results are correct and usable

**How to apply this:**
- For file processing: show file names, sizes, processing results
- For API endpoints: show request/response with realistic data
- For UI features: show workflows with actual user data
- For configurations: show settings applied with real values

---

### 2. Code Removal

**Acceptance Criterion Example:**
> All PDF processing code removed

**Required Evidence:**
- ✅ Prove old modules cannot be imported
- ✅ Show what modules ARE available
- ✅ Verify file structure confirms deletion

**Example:**
```python
# Attempt to import removed modules
import quber_analyst.document.pdf_processor
# ModuleNotFoundError ✓ (cannot import anymore)

# Show what IS available
from quber_analyst import document
dir(document)  # ['DocumentProcessor', 'JSONTableLoader']
✓ Only new modules present

# File system verification
$ ls src/quber_analyst/document/
json_loader.py  __init__.py
✓ Old files physically removed
```

---

### 3. Dependency Changes

**Acceptance Criterion Example:**
> docling dependency removed

**Required Evidence:**
- ✅ Prove dependency cannot be imported
- ✅ Show it's not in pyproject.toml
- ✅ Verify lock file doesn't include it

**Example:**
```python
import docling
# ModuleNotFoundError ✓

$ grep docling pyproject.toml
(no output) ✓

$ grep docling uv.lock
(no output) ✓
```

---

### 4. Configuration Settings

**Acceptance Criterion Example:**
> Configuration allows specifying JSON file path

**Required Evidence:**
- ✅ Show default value works
- ✅ Demonstrate override via environment variable
- ✅ Prove it's actually used in the application

**Example:**
```python
# Default configuration
config = AppConfig()
print(config.tables_json_path)
# Output: 'inputs/tables.json' ✓

# Override via environment
os.environ['TABLES_JSON_PATH'] = 'custom/data.json'
config = AppConfig()
print(config.tables_json_path)
# Output: 'custom/data.json' ✓

# Used in application
processor = DocumentProcessor()
# Internally uses config.tables_json_path ✓
```

---

### 5. Version Upgrades

**Acceptance Criterion Example:**
> Application runs on Python 3.13

**Required Evidence:**
- ✅ Show actual Python version running
- ✅ Run real application code (not just tests)
- ✅ Verify all dependencies work
- ✅ Demonstrate production workloads succeed

**Example:**
```python
import sys
print(sys.version)
# 3.13.8 (main, Oct 8 2025) ✓

# Run real application workflow
processor = DocumentProcessor()
tables = await processor.load_tables('inputs/production_data.json')
# ✓ Loaded 8 tables (all on Python 3.13)

# Verify dependencies
import pydantic  # 2.12.0 ✓
import fastapi   # 0.118.3 ✓
import pandas    # 2.3.3 ✓
```

---

### 6. Integration/Compatibility

**Generic Requirements:**
- ✅ Show the feature integrates with existing systems
- ✅ Demonstrate workflows continue to function
- ✅ Verify all necessary interfaces/fields exist
- ✅ Prove no regressions in dependent functionality

**How to apply this:**
- For API changes: show existing clients still work
- For data structure changes: verify downstream consumers unaffected
- For library updates: demonstrate dependent code functions
- For UI changes: show existing workflows continue

---

## PR Description Template

Use this template structure for PR descriptions:

```markdown
## Summary
[Brief description of changes]

## Acceptance Criteria - Functional Evidence

### ✅ AC1: [Criterion Title]

**Real Example: [Specific usage scenario]**

```[language]
[Actual code demonstrating the feature]
```

**Results:**
- ✓ [Concrete outcome 1]
- ✓ [Concrete outcome 2]

**Production Data Tested:**
- [File 1]: [size] → [results]
- [File 2]: [size] → [results]

---

### ✅ AC2: [Next Criterion]

[Repeat pattern...]

---

## Summary

**Production Files Tested:** [list real files used]
**Workloads Verified:** [list real workflows executed]
**No Issues Found** - All acceptance criteria met through real usage.
```

---

## Examples of Good Evidence

**NOTE:** The examples below are from specific PRs (#59 and #60) to illustrate what good evidence looks like. **DO NOT copy these verbatim** - your evidence should demonstrate YOUR specific acceptance criteria with data appropriate to YOUR feature.

### Example 1: Feature Implementation (PR #59 - JSON Loader)

**What made this evidence good:**
- Used 3 real production files (not minimal test fixtures)
- Showed concrete, measurable results (21+ tables extracted)
- Demonstrated integration (search/filter workflows continued to work)
- Proved removal (old code cannot be imported)
- Verified configuration (settings work as specified)

**Key takeaway:** Evidence was specific to the acceptance criteria for that feature.

🔗 [See Full Example](https://github.com/xmandeng/quber-analyst/pull/59#issuecomment-3403510175)

---

### Example 2: Version Upgrade (PR #60 - Python 3.13)

**What made this evidence good:**
- Verified actual Python version running (concrete, verifiable)
- Demonstrated real workloads functioning (not just tests)
- Checked all dependencies compatible (integration verification)
- Showed configuration enforcement across all relevant files

**Key takeaway:** For version upgrades, showed the new version actually working with real application code.

🔗 [See Full Example](https://github.com/xmandeng/quber-analyst/pull/60#issuecomment-3403510245)

---

## Quick Checklist

Before submitting your PR, verify you have:

- [ ] Demonstrated each AC with **real production data** (not fixtures)
- [ ] Shown **actual usage patterns** (not just "tests pass")
- [ ] Proved **downstream workflows** still function
- [ ] Used **concrete examples** anyone can verify
- [ ] Provided **file names, sizes, and results** for production data tested
- [ ] Showed **real commands** and their **actual output**
- [ ] Demonstrated feature works **end-to-end** in application context

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Only showing test results
```markdown
✅ test_load_json PASSED
✅ test_extract_tables PASSED
```
**Fix:** Show loading real production files, not test fixtures.

---

### ❌ Mistake 2: Using sample/mock data
```markdown
tables = await loader.load('tests/fixtures/sample.json')
✓ Loaded 2 tables
```
**Fix:** Use actual production data from `inputs/` directory.

---

### ❌ Mistake 3: Not showing usage workflows
```markdown
✅ Feature implemented
✅ All tests pass
```
**Fix:** Demonstrate searching, filtering, extracting - real workflows.

---

### ❌ Mistake 4: No concrete results
```markdown
✅ JSON loader works
✅ Configuration functional
```
**Fix:** Show actual file sizes, table counts, extracted data samples.

---

## Questions?

- **Q: Do I still need to run tests?**
  - A: YES! Tests must pass. But passing tests alone are not evidence of acceptance criteria.

- **Q: What if production data doesn't exist yet?**
  - A: Create realistic production-like data, not simple fixtures. Document what real data will look like.

- **Q: How much evidence is enough?**
  - A: Each acceptance criterion needs at least one concrete example with real data showing it works.

- **Q: Can I use multiple examples?**
  - A: Absolutely! 2-3 production examples per AC is ideal.

---

## References

- [CLAUDE.md](../CLAUDE.md) - Project-level agent instructions
- [WORKSTREAM_COMPLETION.md](./WORKSTREAM_COMPLETION.md) - Workstream standards
- [PR #59 Example](https://github.com/xmandeng/quber-analyst/pull/59) - JSON loader functional evidence
- [PR #60 Example](https://github.com/xmandeng/quber-analyst/pull/60) - Python 3.13 functional evidence
