---
name: ai-code-explainer
description: >-
  AI-powered code explanation. Analyzes and explains complex code in plain language, producing structured
  explanations with diagrams, flow descriptions, and architectural insights. This skill should be used when
  the user asks to explain code, understand how something works, "解释这段代码", "这段代码是什么意思", "what does
  this code do", or wants to onboard to an unfamiliar codebase. Supports all programming languages.
agent_created: true
---

# AI Code Explainer

Transform opaque code into clear, structured explanations. Goes beyond line-by-line translation to reveal
design intent, data flow, architectural patterns, and potential pitfalls.

## When to Use

- User asks to explain code or a codebase
- "what does this do?" / "explain this function" / "这段代码是什么意思"
- Onboarding to a new project or module
- Understanding legacy or complex code
- Code walkthrough for learning or review
- "how does X work?" questions about specific implementations

## Workflow

### Step 1: Understand the Target

Determine the scope:
- A single function or method
- A class or component
- A file or module
- A flow spanning multiple files
- An entire subsystem or architecture

Read the relevant code thoroughly. For larger scopes, trace execution paths across files.

### Step 2: Analyze Deeply

Build a mental model of:
- **Purpose**: What problem does this code solve?
- **Input/Output**: What goes in, what comes out?
- **Data Flow**: How does data move through the system?
- **Control Flow**: Decision points, loops, recursion, async patterns
- **Dependencies**: What does it call, what calls it?
- **State Management**: What state exists, how does it change?
- **Edge Cases**: What happens with unusual inputs?
- **Design Patterns**: Factory, Observer, Strategy, etc.
- **Performance Characteristics**: Time/space complexity, bottlenecks
- **Potential Issues**: Race conditions, memory leaks, security concerns

### Step 3: Generate Explanation

Structure the explanation from high-level to detail. Use this template order:

#### Template

```
## Overview
One-paragraph summary: what this code does, why it exists.

## Architecture / Structure
How the pieces fit together. Include a simple ASCII diagram if helpful.

## Key Components
For each major piece:
- **Name**: Purpose and responsibility
- **Signature**: Key inputs and outputs
- **Behavior**: What happens step by step (at a high level)
- **Notable Details**: Important implementation choices

## Data Flow
How data enters, transforms, and exits the system.

## Control Flow
The main execution path through the code.

## Design Decisions
Notable choices and trade-offs:
- Why approach A instead of B?
- What constraints drove these decisions?

## Edge Cases and Gotchas
- What happens with null/empty/error inputs?
- Known limitations or subtle behaviors

## Dependencies
- What does this code depend on?
- What depends on this code?

## Usage Example
Simple example of how to use or call this code.
```

### Step 4: Add Visuals

When appropriate, use the Visualizer to create:
- Flowcharts for control flow
- Sequence diagrams for multi-component interactions
- Component diagrams for architecture
- State diagrams for state machines

### Step 5: Adapt to Audience

Detect the user's expertise level from context:

| Level | Approach |
|-------|----------|
| **Beginner** | Explain concepts, avoid jargon, use analogies |
| **Intermediate** | Standard technical terms, focus on patterns |
| **Advanced** | Skip basics, focus on design decisions and trade-offs |
| **Mixed** | Ask the user what level of detail they want |

## Explanation Examples

### Function-Level Explanation

```
## Overview
`debounce(fn, delay)` creates a new function that delays invoking `fn`
until after `delay` milliseconds have elapsed since the last invocation.
Used to optimize performance for rapid-fire events like keystrokes,
window resizing, and scroll events.

## Key Behavior
1. When the debounced function is called, it clears any pending timer
2. It sets a new timer for `delay` ms
3. If called again before the timer fires, repeat from step 1
4. When the timer finally fires, the original `fn` is called with
   the most recent arguments

## Gotchas
- The `this` context and arguments from the LAST call are used
- If `fn` returns a value, that value is lost when debounced
- Memory: each debounced function holds a closure with a timer reference
```

### Module-Level Explanation

```
## Overview
`auth/` module handles all authentication and authorization for the API.
It provides JWT-based session management, role-based access control,
and OAuth2 integration for third-party login.

## Architecture
  [Client] → [AuthMiddleware] → [AuthService] → [UserStore]
                  ↓                    ↓
           [JWT Validator]      [OAuth2 Provider]

## Key Components
- **AuthMiddleware**: Express middleware that validates JWT on every request.
  Rejects with 401 if token is missing/invalid, attaches user to `req.user`.
- **AuthService**: Business logic for login, logout, token refresh.
  Generates access tokens (15min TTL) and refresh tokens (7day TTL).
- **JWT Validator**: Verifies token signature and expiration.
  Uses RS256 with key rotation every 24 hours.
- **OAuth2 Provider**: Handles Google and GitHub OAuth2 flows.
  Creates local user accounts on first login.

## Design Decisions
- JWT over sessions: stateless, no server-side storage, scales horizontally
- Separate access/refresh tokens: short-lived access tokens limit damage
  from token theft; refresh token rotation adds security
- RS256 over HS256: allows other services to verify tokens without
  sharing the signing secret
```

## Tips

- **Start with WHY**: Before explaining HOW, explain WHY this code exists
- **Use analogies**: "A Promise is like a restaurant buzzer -- you don't stand at the counter, you get notified when your order is ready"
- **Highlight surprises**: "Note the `+ 1` on line 23 -- this handles the fencepost problem"
- **Call out anti-patterns**: If you see issues, mention them constructively
- **Keep it relevant**: Skip details the user already knows based on their level
- **One concept at a time**: Build understanding progressively
