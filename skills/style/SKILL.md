---
name: style
description: Apply Kent Beck's simple design and incremental refactoring principles when writing, changing, reviewing, or refactoring code. Keep intent clear, avoid duplication and speculative complexity, and improve design in small steps.
---

# Kent Beck Style

## Overview

Use Kent Beck's refactoring philosophy and simple design principles while writing or changing code, as well as when reviewing it. Look for code smells, choose focused refactorings, and improve design incrementally.

> "Any fool can write code that a computer can understand. Good programmers write code that humans can understand." - Martin Fowler (Refactoring, foreword by Kent Beck)

## When to Use

- When the user asks you to write, implement, or change code
- When user requests "code smell" detection or "refactoring" guidance
- When asked about "code quality", "readability", or "maintainability"
- When reviewing code for improvement opportunities
- When asked about "YAGNI", "KISS", or "simple design"
- When improving naming, extracting methods, or removing duplication

## Core Design Principles

### Simple Design (4 Rules of Simple Design)

Kent Beck's rules in priority order:

1. **Passes the Tests** - Code must work correctly
2. **Reveals Intent** - Code should clearly express its purpose
3. **No Duplication** - DRY (Don't Repeat Yourself)
4. **Fewest Elements** - Minimize classes, methods, and code

### YAGNI (You Aren't Gonna Need It)

- Don't add functionality until it's actually needed
- Avoid speculative generality
- Build for today's requirements, not imagined futures

```typescript
// Bad: Speculative generality
interface DataProcessor<T, U, V> {
  process(input: T, options: U): V;
  processAsync(input: T, options: U): Promise<V>;
  processBatch(inputs: T[], options: U): V[];
  // We only need one sync method right now!
}

// Good: Build what you need
interface DataProcessor {
  process(input: string): Result;
}
```

### KISS (Keep It Simple, Stupid)

- Prefer simple solutions over clever ones
- Complexity is the enemy of maintainability
- If it's hard to explain, it's probably too complex

### Incremental Design

- Make small, safe changes
- Refactor continuously as you code
- Design emerges through refactoring

## Smells and refactorings

When a review needs the named smell or refactoring for something you found, read
[references/catalog.md](references/catalog.md). It covers the bloaters, object-orientation
abusers, change preventers, dispensables and couplers, with the refactorings that fix each.

## Intention-Revealing Code

### Magic Numbers and Literals

**Always replace magic numbers with named constants.**

```typescript
// Bad
if (response.status === 200) { ... }
if (password.length < 8) { ... }
const timeout = 30000;

// Good
const HTTP_OK = 200;
const MIN_PASSWORD_LENGTH = 8;
const DEFAULT_TIMEOUT_MS = 30000;

if (response.status === HTTP_OK) { ... }
if (password.length < MIN_PASSWORD_LENGTH) { ... }
const timeout = DEFAULT_TIMEOUT_MS;
```

### Naming Guidelines

- **Variables**: Nouns describing what they hold
- **Functions**: Verbs describing what they do
- **Booleans**: Questions that can be answered yes/no
- **Classes**: Nouns describing what they represent

```typescript
// Bad naming
const d = new Date();
const flag = true;
function calc() { ... }

// Good naming
const currentDate = new Date();
const isUserAuthenticated = true;
function calculateShippingCost() { ... }
```

### Self-Documenting Code

Code should express its intent without comments.

```typescript
// Bad: Needs comment to explain
// Check if user can access premium content
if (user.subscription !== null &&
    user.subscription.endDate > new Date() &&
    user.subscription.tier === 'premium') { ... }

// Good: Self-documenting
if (user.hasPremiumAccess()) { ... }

class User {
  hasPremiumAccess(): boolean {
    return this.subscription?.isActive() &&
           this.subscription?.tier === SubscriptionTier.PREMIUM;
  }
}
```

## Working in Small Steps

### The Rhythm of Refactoring

1. **Make a small change**
2. **Run tests**
3. **Commit if green**
4. **Repeat**

### Safe Refactoring Steps

- Change one thing at a time
- Keep the code working at all times
- If tests fail, revert and try smaller steps
- Commit frequently

### Example: Extract Method in Small Steps

```typescript
// Step 1: Identify code to extract
function printOwing() {
  printBanner();

  // START: Code to extract
  console.log(`name: ${name}`);
  console.log(`amount: ${getOutstanding()}`);
  // END: Code to extract
}

// Step 2: Create new method with extracted code
function printDetails() {
  console.log(`name: ${name}`);
  console.log(`amount: ${getOutstanding()}`);
}

// Step 3: Call new method from original location
function printOwing() {
  printBanner();
  printDetails();
}

// Step 4: Run tests, commit
```

## Output Format

Provide review results in this format:

```markdown
# Kent Beck Style Code Review Report

## Summary
- Overall Code Health: [Good/Needs Improvement/Critical]
- Key findings summary

## Code Smells Detected

### [Smell Category]: [Specific Smell]
- **Location**: file:line
- **Description**: What the problem is
- **Impact**: Why it matters
- **Suggested Refactoring**: How to fix it

## Refactoring Recommendations

### High Priority
1. [Most impactful improvements]

### Medium Priority
1. [Moderate improvements]

### Low Priority (Nice to Have)
1. [Minor improvements]

## Positive Aspects
- What the code does well
```

## Language-Specific Examples

### TypeScript/JavaScript

```typescript
// Code Smell: Primitive Obsession + Magic Numbers
function createDiscount(percent: number, startDate: string, endDate: string) {
  if (percent < 0 || percent > 100) throw new Error('Invalid');
  // ...
}

// Refactored
const MIN_DISCOUNT_PERCENT = 0;
const MAX_DISCOUNT_PERCENT = 100;

class DiscountPercent {
  constructor(private value: number) {
    if (value < MIN_DISCOUNT_PERCENT || value > MAX_DISCOUNT_PERCENT) {
      throw new InvalidDiscountError(value);
    }
  }
}

class DateRange {
  constructor(
    private start: Date,
    private end: Date
  ) {
    if (start > end) throw new InvalidDateRangeError();
  }
}

function createDiscount(percent: DiscountPercent, period: DateRange) { ... }
```

### Python

```python
# Code Smell: Long Method + Feature Envy
def process_order(order):
    # Validation (should be in Order)
    if order['items'] is None or len(order['items']) == 0:
        raise ValueError('Empty order')

    # Calculation (should be in Order)
    total = 0
    for item in order['items']:
        total += item['price'] * item['quantity']

    # More processing...

# Refactored
class Order:
    def __init__(self, items: list[OrderItem]):
        self._validate_items(items)
        self.items = items

    def _validate_items(self, items):
        if not items:
            raise EmptyOrderError()

    def calculate_total(self) -> Money:
        return sum(item.subtotal for item in self.items)

def process_order(order: Order):
    total = order.calculate_total()
    # Processing with clear responsibilities...
```

### Java/Kotlin

```kotlin
// Code Smell: Switch Statement + Primitive Obsession
fun calculateShipping(type: String, weight: Double): Double {
    return when (type) {
        "standard" -> weight * 1.5
        "express" -> weight * 3.0
        "overnight" -> weight * 5.0
        else -> throw IllegalArgumentException()
    }
}

// Refactored
sealed class ShippingMethod {
    abstract fun calculateCost(weight: Weight): Money

    object Standard : ShippingMethod() {
        private const val RATE_PER_KG = 1.5
        override fun calculateCost(weight: Weight) =
            Money(weight.kilograms * RATE_PER_KG)
    }

    object Express : ShippingMethod() {
        private const val RATE_PER_KG = 3.0
        override fun calculateCost(weight: Weight) =
            Money(weight.kilograms * RATE_PER_KG)
    }

    object Overnight : ShippingMethod() {
        private const val RATE_PER_KG = 5.0
        override fun calculateCost(weight: Weight) =
            Money(weight.kilograms * RATE_PER_KG)
    }
}
```

## References

- [Refactoring: Improving the Design of Existing Code - Martin Fowler (with Kent Beck)](https://refactoring.com/)
- [Implementation Patterns - Kent Beck](https://www.amazon.com/Implementation-Patterns-Kent-Beck/dp/0321413091)
- [Refactoring Catalog](https://refactoring.com/catalog/)
- [Code Smells](https://refactoring.guru/refactoring/smells)
