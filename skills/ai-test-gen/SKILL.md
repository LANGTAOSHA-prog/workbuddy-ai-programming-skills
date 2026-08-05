---
name: ai-test-gen
description: >-
  AI-powered unit test generator. Automatically generates comprehensive test cases from source code, covering
  edge cases, error paths, and boundary conditions. This skill should be used when the user asks to generate tests,
  write unit tests, "生成测试", "写测试用例", "add tests", or wants to improve test coverage. Supports Jest, Mocha,
  pytest, unittest, JUnit, Go testing, and more.
agent_created: true
---

# AI Test Generator

Generate high-quality unit tests that cover happy paths, edge cases, error conditions, and boundary values.
Targets meaningful coverage -- not just line counting, but behavioral verification.

## When to Use

- User asks to generate tests for code
- "write tests" / "生成测试" / "写单元测试"
- Improving test coverage for a module
- Adding tests for a new feature
- Refactoring and needing regression tests

## Workflow

### Step 1: Understand the Code Under Test

Read the target source file and identify:
- **Public API**: Functions, methods, classes to test
- **Dependencies**: What needs mocking/stubbing
- **Input domain**: Valid inputs, invalid inputs, edge cases
- **Side effects**: Database, filesystem, network, state changes
- **Error conditions**: What exceptions are thrown and when
- **Async behavior**: Promises, callbacks, events, streams

### Step 2: Determine Test Framework

Auto-detect from project configuration, or infer from language:

| Language | Default Framework | Config File |
|----------|------------------|-------------|
| JavaScript/TypeScript | Jest | `jest.config.*`, `package.json` |
| TypeScript (alternative) | Vitest | `vitest.config.*` |
| Python | pytest | `pytest.ini`, `pyproject.toml`, `conftest.py` |
| Python (stdlib) | unittest | N/A |
| Java | JUnit 5 + Mockito | `pom.xml`, `build.gradle` |
| Go | testing (stdlib) | `*_test.go` files |
| Rust | cargo test | `Cargo.toml` |
| Ruby | RSpec / Minitest | `Gemfile` |
| C# | xUnit / NUnit | `.csproj` |

Check existing test files for established patterns and conventions.
Match the project's existing style: naming, assertions, setup/teardown patterns.

### Step 3: Design Test Cases

For each function/method, generate tests covering:

#### Essential Test Categories

1. **Happy Path**: Normal inputs producing expected outputs
2. **Edge Cases**: Empty inputs, null/undefined, boundary values (0, -1, MAX_INT, etc.)
3. **Error Cases**: Invalid inputs, missing required fields, type mismatches
4. **State Transitions**: Verify state before and after operation
5. **Async Behavior**: Resolved promises, rejected promises, timeouts
6. **Integration Points**: Mock interactions with dependencies

#### Test Case Template

Each test should follow AAA pattern:

```
// Arrange: Set up test data and mocks
// Act: Execute the code under test
// Assert: Verify the result
```

### Step 4: Generate Test Code

Write the test file. Follow these principles:

- **One assertion concept per test**: Don't test multiple behaviors in one `it`/`test`
- **Descriptive names**: `it('returns null when user is not found')` not `it('test case 1')`
- **Independent tests**: Each test sets up and tears down its own state
- **Mock externals**: Database, API, filesystem, time -- anything non-deterministic
- **Test behavior, not implementation**: Verify outputs and side effects, not internal calls

### Step 5: Run and Verify

After writing tests, run them:

```bash
# JavaScript/TypeScript
npx jest <test-file>
npx vitest run <test-file>

# Python
python -m pytest <test-file> -v

# Go
go test ./... -v -run <TestName>

# Java (Maven)
mvn test -Dtest=<TestClass>
```

If tests fail, analyze failures:
- Actual bug in source code → report to user
- Test setup incorrect → fix the test
- Mock not matching real behavior → update mock

## Language-Specific Examples

### JavaScript (Jest)

```javascript
// Source: src/utils/math.js
export function divide(a, b) {
  if (b === 0) throw new Error('Division by zero');
  return a / b;
}

// Test: src/utils/math.test.js
import { divide } from './math';

describe('divide', () => {
  it('returns the correct quotient for positive numbers', () => {
    expect(divide(10, 2)).toBe(5);
  });

  it('returns a negative result when one operand is negative', () => {
    expect(divide(-10, 2)).toBe(-5);
  });

  it('returns a decimal for non-divisible numbers', () => {
    expect(divide(1, 3)).toBeCloseTo(0.333, 3);
  });

  it('throws an error when dividing by zero', () => {
    expect(() => divide(5, 0)).toThrow('Division by zero');
  });

  it('handles very large numbers', () => {
    expect(divide(Number.MAX_SAFE_INTEGER, 1))
      .toBe(Number.MAX_SAFE_INTEGER);
  });
});
```

### Python (pytest)

```python
# Source: src/services/user.py
class UserService:
    def __init__(self, db):
        self.db = db

    def get_active_users(self, min_age: int = 0):
        if min_age < 0:
            raise ValueError("min_age must be non-negative")
        users = self.db.query("SELECT * FROM users WHERE active = 1")
        return [u for u in users if u["age"] >= min_age]

# Test: tests/services/test_user.py
import pytest
from src.services.user import UserService

class TestUserService:
    def test_returns_users_above_min_age(self, mocker):
        db = mocker.Mock()
        db.query.return_value = [
            {"id": 1, "name": "Alice", "age": 25},
            {"id": 2, "name": "Bob", "age": 17},
        ]
        svc = UserService(db)
        result = svc.get_active_users(min_age=18)
        assert len(result) == 1
        assert result[0]["name"] == "Alice"

    def test_returns_all_when_min_age_is_zero(self, mocker):
        db = mocker.Mock()
        db.query.return_value = [
            {"id": 1, "name": "Alice", "age": 25},
        ]
        svc = UserService(db)
        result = svc.get_active_users(min_age=0)
        assert len(result) == 1

    def test_raises_on_negative_min_age(self, mocker):
        svc = UserService(mocker.Mock())
        with pytest.raises(ValueError, match="non-negative"):
            svc.get_active_users(min_age=-1)

    def test_returns_empty_when_no_users_match(self, mocker):
        db = mocker.Mock()
        db.query.return_value = []
        svc = UserService(db)
        result = svc.get_active_users(min_age=18)
        assert result == []

    def test_filters_empty_database(self, mocker):
        db = mocker.Mock()
        db.query.return_value = []
        svc = UserService(db)
        result = svc.get_active_users()
        assert result == []
```

### Go

```go
// Source: pkg/math/divide.go
package math

import "errors"

var ErrDivisionByZero = errors.New("division by zero")

func Divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, ErrDivisionByZero
    }
    return a / b, nil
}

// Test: pkg/math/divide_test.go
package math

import "testing"

func TestDivide(t *testing.T) {
    tests := []struct {
        name    string
        a, b    float64
        want    float64
        wantErr error
    }{
        {"positive numbers", 10, 2, 5, nil},
        {"negative result", -10, 2, -5, nil},
        {"decimal result", 1, 3, 0.3333333333333333, nil},
        {"divide by zero", 5, 0, 0, ErrDivisionByZero},
        {"zero numerator", 0, 5, 0, nil},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := Divide(tt.a, tt.b)
            if tt.wantErr != nil {
                if err == nil {
                    t.Fatal("expected error, got nil")
                }
                if err.Error() != tt.wantErr.Error() {
                    t.Fatalf("expected %v, got %v", tt.wantErr, err)
                }
                return
            }
            if err != nil {
                t.Fatalf("unexpected error: %v", err)
            }
            if got != tt.want {
                t.Fatalf("Divide(%v, %v) = %v, want %v",
                    tt.a, tt.b, got, tt.want)
            }
        })
    }
}
```

## Test Quality Checklist

Before presenting generated tests, verify:

- [ ] All public functions have at least one test
- [ ] Happy path is covered
- [ ] Each error/exception path is tested
- [ ] Boundary values are tested (null, empty, 0, -1, max)
- [ ] Async operations handle both resolve and reject
- [ ] Mocks/stubs are used for external dependencies
- [ ] Test names clearly describe what is being tested
- [ ] Tests are independent (no shared mutable state)
- [ ] No test-only code added to source files
- [ ] Tests follow the project's existing conventions
