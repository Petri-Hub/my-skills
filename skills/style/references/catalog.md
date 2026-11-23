## Code Smells Catalog

### 1. Bloaters

Code that has grown too large to handle.

#### Long Method
- Methods doing too many things
- Difficult to understand at a glance
- **Refactoring**: Extract Method, Replace Temp with Query

```typescript
// Bad: Long method doing many things
function processOrder(order: Order) {
  // Validate order (10 lines)
  // Calculate discount (15 lines)
  // Apply tax (10 lines)
  // Update inventory (20 lines)
  // Send notification (15 lines)
  // Generate invoice (25 lines)
}

// Good: Extracted into focused methods
function processOrder(order: Order) {
  validateOrder(order);
  const discount = calculateDiscount(order);
  const total = applyTax(order.subtotal - discount);
  updateInventory(order.items);
  sendOrderConfirmation(order);
  generateInvoice(order, total);
}
```

#### Large Class
- Class with too many responsibilities
- Too many instance variables
- **Refactoring**: Extract Class, Extract Subclass

#### Primitive Obsession
- Overuse of primitives instead of small objects
- Using strings for phone numbers, money, etc.
- **Refactoring**: Replace Primitive with Object, Introduce Parameter Object

```typescript
// Bad: Primitive obsession
function createUser(
  name: string,
  email: string,
  phone: string,
  street: string,
  city: string,
  zipCode: string
) { ... }

// Good: Value objects
function createUser(
  name: Name,
  email: Email,
  phone: Phone,
  address: Address
) { ... }
```

#### Long Parameter List
- Methods with too many parameters
- Hard to understand and call correctly
- **Refactoring**: Introduce Parameter Object, Preserve Whole Object

#### Data Clumps
- Groups of data that always appear together
- **Refactoring**: Extract Class, Introduce Parameter Object

### 2. Object-Orientation Abusers

Improper application of OO principles.

#### Switch Statements
- Complex switch/case or if/else chains
- Often indicates missing polymorphism
- **Refactoring**: Replace Conditional with Polymorphism, Replace Type Code with Subclasses

```typescript
// Bad: Switch statement
function calculateArea(shape: Shape): number {
  switch (shape.type) {
    case 'circle':
      return Math.PI * shape.radius ** 2;
    case 'rectangle':
      return shape.width * shape.height;
    case 'triangle':
      return (shape.base * shape.height) / 2;
  }
}

// Good: Polymorphism
interface Shape {
  calculateArea(): number;
}

class Circle implements Shape {
  calculateArea(): number {
    return Math.PI * this.radius ** 2;
  }
}
```

#### Temporary Field
- Fields only set in certain circumstances
- **Refactoring**: Extract Class, Introduce Null Object

#### Refused Bequest
- Subclass doesn't use inherited methods
- **Refactoring**: Replace Inheritance with Delegation

#### Alternative Classes with Different Interfaces
- Classes doing the same thing with different method names
- **Refactoring**: Rename Method, Extract Superclass

### 3. Change Preventers

Code that makes changes difficult.

#### Divergent Change
- One class changes for multiple reasons
- Violates Single Responsibility Principle
- **Refactoring**: Extract Class

#### Shotgun Surgery
- One change requires modifications in many classes
- **Refactoring**: Move Method, Move Field, Inline Class

#### Parallel Inheritance Hierarchies
- Creating a subclass requires creating another subclass elsewhere
- **Refactoring**: Move Method, Move Field

### 4. Dispensables

Code that is unnecessary.

#### Duplicate Code
- Same code structure in multiple places
- **Refactoring**: Extract Method, Extract Class, Pull Up Method

```typescript
// Bad: Duplicate code
function validateEmail(email: string): boolean {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}

function isValidEmail(input: string): boolean {
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return pattern.test(input);
}

// Good: Single source of truth
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function isValidEmail(email: string): boolean {
  return EMAIL_PATTERN.test(email);
}
```

#### Dead Code
- Unreachable or unused code
- **Refactoring**: Remove Dead Code

#### Speculative Generality
- Unused abstractions created "just in case"
- **Refactoring**: Collapse Hierarchy, Inline Class, Remove Parameter

#### Comments (as smell)
- Comments explaining what code does (instead of why)
- Often indicates code that should be clearer
- **Refactoring**: Extract Method, Rename Method

```typescript
// Bad: Comment explaining what
// Check if user is adult
if (user.age >= 18) { ... }

// Good: Self-documenting code
const LEGAL_ADULT_AGE = 18;
if (user.isAdult()) { ... }

// Good use of comments: explaining why
// Using >= instead of > because legal age includes 18th birthday
if (user.age >= LEGAL_ADULT_AGE) { ... }
```

### 5. Couplers

Code with excessive coupling.

#### Feature Envy
- Method uses another class's data more than its own
- **Refactoring**: Move Method, Extract Method

```typescript
// Bad: Feature envy
class OrderPrinter {
  print(order: Order) {
    console.log(`Order: ${order.id}`);
    console.log(`Customer: ${order.customer.name}`);
    console.log(`Total: ${order.items.reduce((sum, item) =>
      sum + item.price * item.quantity, 0)}`);
  }
}

// Good: Move calculation to Order
class Order {
  getTotal(): number {
    return this.items.reduce((sum, item) =>
      sum + item.price * item.quantity, 0);
  }
}
```

#### Inappropriate Intimacy
- Classes too dependent on each other's internals
- **Refactoring**: Move Method, Move Field, Change Bidirectional to Unidirectional

#### Message Chains
- Long chains of method calls (a.b().c().d())
- **Refactoring**: Hide Delegate, Extract Method

#### Middle Man
- Class that only delegates to another class
- **Refactoring**: Remove Middle Man, Inline Method

## Refactoring Techniques

### Composing Methods

#### Extract Method
The most important refactoring. Turn code fragments into methods with intention-revealing names.

```typescript
// Before
function printOwing() {
  printBanner();

  // Print details
  console.log(`name: ${name}`);
  console.log(`amount: ${getOutstanding()}`);
}

// After
function printOwing() {
  printBanner();
  printDetails();
}

function printDetails() {
  console.log(`name: ${name}`);
  console.log(`amount: ${getOutstanding()}`);
}
```

#### Inline Method
When method body is as clear as its name.

#### Replace Temp with Query
Replace temporary variables with method calls.

```typescript
// Before
const basePrice = quantity * itemPrice;
if (basePrice > 1000) {
  return basePrice * 0.95;
}

// After
if (getBasePrice() > 1000) {
  return getBasePrice() * 0.95;
}

function getBasePrice() {
  return quantity * itemPrice;
}
```

### Moving Features

#### Move Method
Move method to the class that uses it most.

#### Move Field
Move field to where it's used most.

#### Extract Class
When a class does work that should be done by two.

#### Inline Class
When a class isn't doing much.

### Organizing Data

#### Replace Magic Number with Symbolic Constant
Always name your constants!

```typescript
// Bad: Magic numbers
if (age >= 18) { ... }
const tax = price * 0.1;
setTimeout(callback, 86400000);

// Good: Named constants
const LEGAL_ADULT_AGE = 18;
const TAX_RATE = 0.1;
const MILLISECONDS_PER_DAY = 24 * 60 * 60 * 1000;

if (age >= LEGAL_ADULT_AGE) { ... }
const tax = price * TAX_RATE;
setTimeout(callback, MILLISECONDS_PER_DAY);
```

#### Encapsulate Field
Make fields private, provide accessors.

#### Replace Data Value with Object
When a data item needs additional behavior.

### Simplifying Conditionals

#### Decompose Conditional
Extract condition and branches into methods.

```typescript
// Before
if (date.before(SUMMER_START) || date.after(SUMMER_END)) {
  charge = quantity * winterRate + winterServiceCharge;
} else {
  charge = quantity * summerRate;
}

// After
if (isWinter(date)) {
  charge = winterCharge(quantity);
} else {
  charge = summerCharge(quantity);
}
```

#### Consolidate Conditional Expression
Combine conditionals that have the same result.

#### Replace Nested Conditional with Guard Clauses
Use early returns to reduce nesting.

```typescript
// Before
function getPayAmount() {
  let result;
  if (isDead) {
    result = deadAmount();
  } else {
    if (isSeparated) {
      result = separatedAmount();
    } else {
      if (isRetired) {
        result = retiredAmount();
      } else {
        result = normalPayAmount();
      }
    }
  }
  return result;
}

// After
function getPayAmount() {
  if (isDead) return deadAmount();
  if (isSeparated) return separatedAmount();
  if (isRetired) return retiredAmount();
  return normalPayAmount();
}
```

### Simplifying Method Calls

#### Rename Method
Names should reveal intent.

```typescript
// Bad names
function calc(a, b) { ... }
function doIt() { ... }
function process(data) { ... }

// Good names
function calculateTotalPrice(items, taxRate) { ... }
function sendOrderConfirmation() { ... }
function validateUserCredentials(credentials) { ... }
```

#### Add/Remove Parameter
Keep parameter lists minimal and meaningful.

#### Introduce Parameter Object
Group related parameters.

#### Preserve Whole Object
Pass the object instead of extracting values.
