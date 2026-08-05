---
name: ai-docstring
description: >-
  AI-powered documentation comment generator. Automatically generates docstrings, JSDoc, Python docstrings, JavaDoc,
  and other code documentation from source code. This skill should be used when the user asks to add documentation,
  generate docstrings, "写注释", "生成文档", "add docs", or wants to document functions, classes, or modules.
  Supports all major programming languages and documentation standards.
agent_created: true
---

# AI Docstring Generator

Generate comprehensive, well-structured documentation comments for any programming language.
Understands code logic and produces human-readable documentation that explains WHAT and WHY, not just HOW.

## When to Use

- User asks to add documentation to code
- "generate docstrings" / "add JSDoc" / "写文档注释"
- Documenting a new module, class, or function
- Improving existing documentation
- Migrating between documentation formats

## Workflow

### Step 1: Analyze the Code

Read the target file(s) and understand:
- Function signatures: parameters, return types, exceptions
- Class hierarchy and interfaces
- Module purpose and exports
- Dependencies and side effects
- Algorithm complexity and edge cases

### Step 2: Determine Documentation Standard

Auto-detect based on language, or ask the user:

| Language | Default Standard |
|----------|-----------------|
| Python | Google-style docstring (preferred) or Sphinx/reStructuredText |
| JavaScript/TypeScript | JSDoc |
| Java | JavaDoc |
| Go | Go Doc comments |
| Rust | Rust doc comments (`///` and `//!`) |
| C/C++ | Doxygen |
| Ruby | RDoc or YARD |
| PHP | PHPDoc |
| Swift | Swift Doc comments |
| Kotlin | KDoc |

### Step 3: Generate Documentation

Follow these rules for all languages:

#### Functions / Methods
Document:
- **Summary**: One-line description of what it does (imperative mood)
- **Parameters**: Name, type, description, default value, constraints
- **Returns**: Type and description, including possible null/undefined
- **Raises/Throws**: Exception types and when they occur
- **Examples**: (if complex) Usage examples with expected output
- **Side Effects**: If it modifies global state, DB, filesystem
- **Complexity**: Time/space complexity for algorithmic code
- **Since**: Version when added (if known)
- **Deprecated**: Warning with migration path if applicable

#### Classes
Document:
- **Purpose**: What the class represents
- **Constructor**: Parameter documentation
- **Properties**: Type, mutability, default value
- **Methods**: Public API with full documentation
- **Inheritance**: Parent class and interfaces
- **Thread Safety**: If applicable
- **Usage Example**: Typical instantiation and usage pattern

#### Modules / Files
Document:
- **Module purpose**: What this file/module provides
- **Exports**: Public API surface
- **Dependencies**: Key imports and why
- **Configuration**: Environment variables, config expected
- **Architecture Notes**: Design decisions

### Step 4: Apply with Edit Tool

Use the Edit tool to insert docstrings at the correct positions.
Never modify the actual code logic -- only add documentation.

Preserve existing formatting, indentation, and line endings.

### Step 5: Validate

After adding docstrings, verify:
- All public APIs are documented
- Parameter names match the actual signature
- Return types match the actual return values
- References to other functions/classes are correct
- No TODOs or placeholder text remains

## Format-Specific Examples

### Python (Google Style)

```python
def fetch_user(user_id: int, include_inactive: bool = False) -> dict | None:
    """Retrieve a user by their unique identifier.

    Queries the users table and returns the matching record. The result
    is cached for 5 minutes to reduce database load.

    Args:
        user_id: The unique user identifier. Must be a positive integer.
        include_inactive: If True, include soft-deleted and suspended users.
            Defaults to False.

    Returns:
        A dictionary with user fields (id, name, email, status) or None
        if no matching user is found.

    Raises:
        ValueError: If user_id is not a positive integer.
        DatabaseError: If the database connection fails.

    Example:
        >>> user = fetch_user(42)
        >>> print(user["name"])
        'Alice'
    """
```

### JavaScript (JSDoc)

```javascript
/**
 * Retrieves a user by their unique identifier.
 *
 * Queries the users table and returns the matching record. The result
 * is cached for 5 minutes to reduce database load.
 *
 * @param {number} userId - The unique user identifier. Must be positive.
 * @param {Object} [options] - Query options.
 * @param {boolean} [options.includeInactive=false] - Include soft-deleted users.
 * @returns {Promise<User|null>} The user object, or null if not found.
 * @throws {ValidationError} If userId is not a valid positive integer.
 * @throws {DatabaseError} If the database connection fails.
 * @since 2.1.0
 *
 * @example
 * const user = await fetchUser(42);
 * console.log(user.name); // "Alice"
 */
async function fetchUser(userId, options = {}) { ... }
```

### Go

```go
// FetchUser retrieves a user by their unique identifier.
//
// It queries the users table and returns the matching record.
// The result is cached for 5 minutes to reduce database load.
//
// The includeInactive parameter controls whether soft-deleted
// and suspended users are included in the results.
//
// Returns ErrNotFound if no user matches the given ID.
// Returns ErrInvalidID if the ID is not a positive integer.
func FetchUser(ctx context.Context, userID int64, includeInactive bool) (*User, error) { ... }
```

### Java (JavaDoc)

```java
/**
 * Retrieves a user by their unique identifier.
 *
 * <p>Queries the users table and returns the matching record.
 * The result is cached for 5 minutes to reduce database load.</p>
 *
 * @param userId      the unique user identifier; must be positive
 * @param includeInactive  if {@code true}, include soft-deleted users
 * @return the user object, or {@code null} if not found
 * @throws IllegalArgumentException if userId is not positive
 * @throws DataAccessException if the database query fails
 * @since 2.1.0
 */
public User fetchUser(long userId, boolean includeInactive) { ... }
```

## Tips

- Keep the summary line under 80 characters
- Document edge cases: null inputs, empty collections, boundary values
- Don't state the obvious: `x += 1` doesn't need "Increments x by 1"
- Focus on WHY: "Sorts results by relevance to avoid pagination issues" > "Sorts the results array"
- For inherited methods, use `@inheritDoc` or equivalent instead of copying
- Update docstrings when code changes -- stale docs are worse than no docs
