# Common Code Antipatterns

A comprehensive guide to recognizing, understanding, and fixing common antipatterns and code smells.

## Table of Contents

1. [God Class / God Function](#god-class--god-function)
2. [Spaghetti Code](#spaghetti-code)
3. [Copy-Paste Programming](#copy-paste-programming)
4. [Magic Numbers and Strings](#magic-numbers-and-strings)
5. [Deep Nesting](#deep-nesting)
6. [Premature Optimization](#premature-optimization)
7. [Over-Engineering](#over-engineering)
8. [Poor Error Handling](#poor-error-handling)
9. [Resource Leaks](#resource-leaks)
10. [Race Conditions](#race-conditions)
11. [Circular Dependencies](#circular-dependencies)
12. [Feature Envy](#feature-envy)
13. [Primitive Obsession](#primitive-obsession)
14. [Long Parameter Lists](#long-parameter-lists)
15. [Dead Code](#dead-code)

---

## God Class / God Function

### Description

A class or function that tries to do everything. It knows too much, has too many responsibilities, and becomes a central point that everything depends on.

### Why It's Bad

- Difficult to understand and maintain
- Hard to test in isolation
- Changes risk breaking unrelated functionality
- Creates tight coupling throughout the codebase
- Violates Single Responsibility Principle

### How to Detect

- Class has 500+ lines of code
- Function has 100+ lines of code
- Class has 20+ methods
- Function has 10+ parameters
- Name is vague: `Manager`, `Handler`, `Processor`, `Utils`
- File is the most frequently modified in the codebase

### Examples

```python
# ANTIPATTERN: God class doing everything
class UserManager:
    def create_user(self, data): ...
    def update_user(self, user_id, data): ...
    def delete_user(self, user_id): ...
    def authenticate_user(self, username, password): ...
    def send_welcome_email(self, user): ...
    def send_password_reset_email(self, user): ...
    def generate_user_report(self, filters): ...
    def export_users_to_csv(self, users): ...
    def import_users_from_csv(self, file): ...
    def validate_user_data(self, data): ...
    def hash_password(self, password): ...
    def check_password(self, password, hash): ...
    def generate_api_key(self, user): ...
    def log_user_activity(self, user, action): ...
    def calculate_user_statistics(self): ...
    def sync_users_to_ldap(self): ...
    def backup_user_data(self): ...
    # ... 30 more methods

# REFACTORED: Separate responsibilities
class UserRepository:
    """Handles user persistence operations."""
    def create(self, data: UserData) -> User: ...
    def get_by_id(self, user_id: int) -> Optional[User]: ...
    def update(self, user: User) -> User: ...
    def delete(self, user_id: int) -> bool: ...

class AuthenticationService:
    """Handles authentication logic."""
    def __init__(self, user_repo: UserRepository, password_hasher: PasswordHasher):
        self.user_repo = user_repo
        self.password_hasher = password_hasher

    def authenticate(self, username: str, password: str) -> Optional[User]: ...
    def generate_token(self, user: User) -> str: ...

class UserNotificationService:
    """Handles user-related emails."""
    def __init__(self, email_client: EmailClient):
        self.email_client = email_client

    def send_welcome_email(self, user: User) -> None: ...
    def send_password_reset(self, user: User) -> None: ...

class UserExportService:
    """Handles user data export/import."""
    def export_to_csv(self, users: List[User]) -> bytes: ...
    def import_from_csv(self, file: BinaryIO) -> List[User]: ...
```

### How to Fix

1. **Identify responsibilities** - List all distinct things the class does
2. **Group related methods** - Cluster methods that work together
3. **Extract classes** - Create new classes for each responsibility
4. **Define interfaces** - Use dependency injection for communication
5. **Move incrementally** - Refactor one responsibility at a time

---

## Spaghetti Code

### Description

Code with tangled, interconnected logic that's hard to follow. Control flow jumps around unpredictably, often with excessive gotos, deeply nested callbacks, or convoluted conditionals.

### Why It's Bad

- Extremely difficult to understand
- Nearly impossible to modify safely
- Testing is challenging
- Debugging is painful
- New developers struggle to onboard

### How to Detect

- Deeply nested if/else chains (4+ levels)
- Functions calling each other in circular patterns
- Callback hell in async code
- Excessive use of global state
- Control flow that requires a flowchart to understand

### Examples

```python
# ANTIPATTERN: Spaghetti code with complex flow
def process_order(order):
    result = None
    if order:
        if order.items:
            if order.customer:
                if order.customer.verified:
                    if order.payment:
                        if order.payment.validated:
                            for item in order.items:
                                if item.in_stock:
                                    if item.quantity <= item.available:
                                        # Process continues...
                                        if order.shipping:
                                            if order.shipping.address:
                                                # 20 more nested conditions...
                                                result = "success"
                                            else:
                                                result = "no address"
                                        else:
                                            result = "no shipping"
                                    else:
                                        result = "insufficient stock"
                                else:
                                    result = "out of stock"
                        else:
                            result = "payment not validated"
                    else:
                        result = "no payment"
                else:
                    result = "customer not verified"
            else:
                result = "no customer"
        else:
            result = "no items"
    else:
        result = "no order"
    return result

# REFACTORED: Clear, linear flow with early returns
def process_order(order: Order) -> OrderResult:
    """Process an order through validation and fulfillment."""
    # Validate order exists
    if not order:
        return OrderResult.error("No order provided")

    # Validate order components
    validation_result = validate_order(order)
    if not validation_result.is_valid:
        return OrderResult.error(validation_result.message)

    # Check inventory
    inventory_result = check_inventory(order.items)
    if not inventory_result.available:
        return OrderResult.error(f"Inventory issue: {inventory_result.message}")

    # Process payment
    payment_result = process_payment(order.payment)
    if not payment_result.success:
        return OrderResult.error(f"Payment failed: {payment_result.message}")

    # Ship order
    shipping_result = ship_order(order)
    if not shipping_result.success:
        # Refund payment if shipping fails
        refund_payment(payment_result.transaction_id)
        return OrderResult.error(f"Shipping failed: {shipping_result.message}")

    return OrderResult.success(order_id=order.id)


def validate_order(order: Order) -> ValidationResult:
    """Validate all order components."""
    if not order.items:
        return ValidationResult(False, "No items in order")

    if not order.customer:
        return ValidationResult(False, "No customer information")

    if not order.customer.verified:
        return ValidationResult(False, "Customer not verified")

    if not order.payment:
        return ValidationResult(False, "No payment information")

    if not order.shipping or not order.shipping.address:
        return ValidationResult(False, "No shipping address")

    return ValidationResult(True, "Order valid")
```

### How to Fix

1. **Use early returns** - Exit early for invalid conditions
2. **Extract helper functions** - Break complex logic into named functions
3. **Use guard clauses** - Handle edge cases first
4. **Flatten callbacks** - Use async/await instead of nested callbacks
5. **State machines** - For complex workflows, use explicit state machines

---

## Copy-Paste Programming

### Description

Duplicating code instead of abstracting common functionality. When you see the same or similar code in multiple places.

### Why It's Bad

- Bug fixes must be applied in multiple places
- Easy to miss one copy when updating
- Increases codebase size unnecessarily
- Violates DRY (Don't Repeat Yourself)
- Makes refactoring difficult

### How to Detect

- Same code block appears 3+ times
- Similar functions with minor variations
- Tests with repeated setup code
- Copy-pasted error handling

### Examples

```python
# ANTIPATTERN: Duplicated validation logic
class UserAPI:
    def create_user(self, data):
        if not data.get("email"):
            raise ValueError("Email is required")
        if "@" not in data.get("email", ""):
            raise ValueError("Invalid email format")
        if len(data.get("email", "")) > 255:
            raise ValueError("Email too long")
        # ... more code

    def update_user(self, user_id, data):
        if not data.get("email"):
            raise ValueError("Email is required")
        if "@" not in data.get("email", ""):
            raise ValueError("Invalid email format")
        if len(data.get("email", "")) > 255:
            raise ValueError("Email too long")
        # ... more code

    def invite_user(self, data):
        if not data.get("email"):
            raise ValueError("Email is required")
        if "@" not in data.get("email", ""):
            raise ValueError("Invalid email format")
        if len(data.get("email", "")) > 255:
            raise ValueError("Email too long")
        # ... more code

# REFACTORED: Centralized validation
from pydantic import BaseModel, Field, validator

class EmailInput(BaseModel):
    """Validated email input."""
    email: str = Field(..., max_length=255)

    @validator("email")
    def validate_email_format(cls, v):
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower()


class UserAPI:
    def create_user(self, data: dict):
        validated = EmailInput(**data)
        # ... use validated.email

    def update_user(self, user_id: int, data: dict):
        validated = EmailInput(**data)
        # ... use validated.email

    def invite_user(self, data: dict):
        validated = EmailInput(**data)
        # ... use validated.email
```

### How to Fix

1. **Identify the pattern** - Find repeated code blocks
2. **Abstract common parts** - Extract to function, class, or decorator
3. **Parameterize differences** - Pass varying parts as arguments
4. **Use inheritance/mixins** - For repeated class behavior
5. **Create utilities** - For cross-cutting concerns

---

## Magic Numbers and Strings

### Description

Using literal values directly in code without explanation. These "magic" values have hidden meaning that's not apparent from the code.

### Why It's Bad

- Meaning is unclear without context
- Changing the value requires finding all occurrences
- Typos in strings cause hard-to-find bugs
- No IDE autocomplete or type checking
- Easy to use wrong value

### How to Detect

- Numbers like `86400`, `3600`, `1000`, `255`
- String literals for status, types, or categories
- Repeated literal values
- Comments explaining what a number means

### Examples

```python
# ANTIPATTERN: Magic numbers and strings everywhere
def process_user(user, action):
    if user.role == "admin":  # Magic string
        if action == 1:  # What does 1 mean?
            user.permissions = 255  # What's 255?
        elif action == 2:
            user.permissions = 127
    elif user.role == "moderator":
        if action == 1:
            user.permissions = 63

    if user.last_login < time.time() - 604800:  # What's 604800?
        user.status = "inactive"

    # Rate limiting
    if user.request_count > 100:  # Why 100?
        sleep(60)  # Why 60?

# REFACTORED: Named constants with clear meaning
from enum import Enum, auto

class UserRole(Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"

class PermissionAction(Enum):
    GRANT_FULL = auto()
    GRANT_LIMITED = auto()
    REVOKE = auto()

class Permission:
    """Permission bit flags."""
    READ = 0b00000001
    WRITE = 0b00000010
    DELETE = 0b00000100
    ADMIN = 0b00001000

    FULL_ACCESS = 0b11111111  # 255: All permissions
    MODERATOR_ACCESS = 0b01111111  # 127: All except admin
    USER_ACCESS = 0b00111111  # 63: Basic access

class TimeConstants:
    """Time durations in seconds."""
    SECONDS_PER_MINUTE = 60
    SECONDS_PER_HOUR = 3600
    SECONDS_PER_DAY = 86400
    SECONDS_PER_WEEK = 604800

class RateLimits:
    """Rate limiting configuration."""
    MAX_REQUESTS_PER_MINUTE = 100
    COOLDOWN_SECONDS = 60

def process_user(user: User, action: PermissionAction) -> None:
    if user.role == UserRole.ADMIN:
        if action == PermissionAction.GRANT_FULL:
            user.permissions = Permission.FULL_ACCESS
        elif action == PermissionAction.GRANT_LIMITED:
            user.permissions = Permission.MODERATOR_ACCESS
    elif user.role == UserRole.MODERATOR:
        if action == PermissionAction.GRANT_FULL:
            user.permissions = Permission.USER_ACCESS

    inactive_threshold = time.time() - TimeConstants.SECONDS_PER_WEEK
    if user.last_login < inactive_threshold:
        user.status = UserStatus.INACTIVE

    if user.request_count > RateLimits.MAX_REQUESTS_PER_MINUTE:
        sleep(RateLimits.COOLDOWN_SECONDS)
```

### How to Fix

1. **Define constants** - Named constants at module/class level
2. **Use enums** - For finite sets of values
3. **Configuration objects** - For runtime-configurable values
4. **Document units** - Include units in constant names (e.g., `TIMEOUT_SECONDS`)

---

## Deep Nesting

### Description

Code with many levels of indentation due to nested conditionals, loops, or callbacks. Generally, more than 3 levels of nesting indicates a problem.

### Why It's Bad

- Hard to follow the logic flow
- Difficult to understand which conditions apply
- Often indicates multiple responsibilities
- Makes testing complex
- Prone to bugs from misunderstood scope

### How to Detect

- Indentation goes beyond 4 levels
- "Arrow code" pattern (code shaped like an arrow pointing right)
- Need to scroll horizontally to read
- Difficulty tracing which branch you're in

### Examples

```python
# ANTIPATTERN: Deep nesting (arrow code)
def process_data(data):
    if data:
        if data.is_valid:
            if data.type == "json":
                parsed = json.loads(data.content)
                if "items" in parsed:
                    for item in parsed["items"]:
                        if item.get("active"):
                            if item.get("price") > 0:
                                if item.get("quantity") > 0:
                                    process_item(item)
                                else:
                                    log.warning("No quantity")
                            else:
                                log.warning("Invalid price")
                        else:
                            log.debug("Skipping inactive")
                else:
                    raise ValueError("No items")
            else:
                raise ValueError("Not JSON")
        else:
            raise ValueError("Invalid data")
    else:
        raise ValueError("No data")

# REFACTORED: Flat structure with early returns and extraction
def process_data(data: DataContainer) -> ProcessingResult:
    """Process data container and return results."""
    # Guard clauses - handle invalid cases first
    if not data:
        raise ValueError("No data provided")

    if not data.is_valid:
        raise ValueError("Invalid data")

    if data.type != "json":
        raise ValueError(f"Unsupported type: {data.type}")

    parsed = json.loads(data.content)

    if "items" not in parsed:
        raise ValueError("No items in data")

    # Process items
    return process_items(parsed["items"])


def process_items(items: List[dict]) -> ProcessingResult:
    """Process a list of items."""
    results = []

    for item in items:
        result = process_single_item(item)
        if result:
            results.append(result)

    return ProcessingResult(results)


def process_single_item(item: dict) -> Optional[ItemResult]:
    """Process a single item if it meets criteria."""
    if not item.get("active"):
        log.debug(f"Skipping inactive item: {item.get('id')}")
        return None

    if not item.get("price") or item["price"] <= 0:
        log.warning(f"Invalid price for item: {item.get('id')}")
        return None

    if not item.get("quantity") or item["quantity"] <= 0:
        log.warning(f"No quantity for item: {item.get('id')}")
        return None

    return process_valid_item(item)
```

### How to Fix

1. **Guard clauses** - Return early for invalid conditions
2. **Extract functions** - Break nested code into named functions
3. **Invert conditions** - Check for failure cases first
4. **Use continue/break** - Skip iterations instead of nesting
5. **Functional style** - Use filter/map for collection processing

---

## Premature Optimization

### Description

Optimizing code before understanding whether optimization is needed. Spending time on micro-optimizations without profiling to identify actual bottlenecks.

### Why It's Bad

- Wastes development time
- Often makes code harder to read
- Optimizations may be in wrong places
- Can introduce bugs
- Real bottlenecks remain unaddressed

### How to Detect

- Complex code "for performance" without benchmarks
- Caching without measuring benefit
- Using "fast" data structures when simple ones work
- Premature database denormalization
- Comments saying "this is faster"

### Examples

```python
# ANTIPATTERN: Premature micro-optimizations
class UserCache:
    def __init__(self):
        # Pre-allocated array for "performance"
        self._users = [None] * 10000
        # Using __slots__ before profiling showed need
        # Complex hash function "for speed"
        self._hash_cache = {}

    def get_user(self, user_id):
        # Bit manipulation "optimization"
        bucket = user_id & 0xFFF
        # Complex caching logic for minor gain
        if bucket in self._hash_cache:
            cached = self._hash_cache[bucket]
            if cached[0] == user_id:
                return cached[1]
        # ... continues with complexity

# BETTER: Simple first, optimize if needed
class UserCache:
    """Simple user cache - optimize only if profiling shows need."""

    def __init__(self):
        self._cache: Dict[int, User] = {}
        self._max_size = 1000

    def get_user(self, user_id: int) -> Optional[User]:
        """Get cached user by ID."""
        return self._cache.get(user_id)

    def set_user(self, user: User) -> None:
        """Cache a user."""
        if len(self._cache) >= self._max_size:
            self._evict_oldest()
        self._cache[user.id] = user

# When optimization IS needed, profile first:
# python -m cProfile script.py
# Or use line_profiler, memory_profiler, py-spy
```

### How to Fix

1. **Profile first** - Measure before optimizing
2. **Focus on algorithms** - O(n) to O(log n) matters more than micro-optimizations
3. **Keep it simple** - Start with readable code
4. **Document decisions** - If you do optimize, document why with benchmarks
5. **80/20 rule** - 80% of time is spent in 20% of code

---

## Over-Engineering

### Description

Creating overly complex solutions for simple problems. Building for hypothetical future requirements instead of current needs.

### Why It's Bad

- Increases development time
- Makes code harder to understand
- Maintenance burden increases
- Features that are never used
- YAGNI violation (You Aren't Gonna Need It)

### How to Detect

- Abstract base classes with one implementation
- Factory factories
- Configuration for things that never change
- "Plugin architecture" for internal code
- Multiple abstraction layers for simple operations

### Examples

```python
# ANTIPATTERN: Over-engineered solution for simple config
from abc import ABC, abstractmethod

class ConfigurationLoaderFactory(ABC):
    @abstractmethod
    def create_loader(self) -> "ConfigurationLoader":
        pass

class ConfigurationLoader(ABC):
    @abstractmethod
    def load(self) -> "Configuration":
        pass

class JSONConfigurationLoader(ConfigurationLoader):
    def __init__(self, path: str, validator: "ConfigValidator"):
        self.path = path
        self.validator = validator

    def load(self) -> "Configuration":
        # ... loads JSON

class ConfigurationLoaderFactoryFactory:
    _loaders: Dict[str, ConfigurationLoaderFactory] = {}

    @classmethod
    def register(cls, format: str, factory: ConfigurationLoaderFactory):
        cls._loaders[format] = factory

    @classmethod
    def get_factory(cls, format: str) -> ConfigurationLoaderFactory:
        return cls._loaders[format]

# ... 200 more lines of abstraction

# BETTER: Simple solution for actual requirements
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment/.env file."""

    database_url: str
    api_key: str
    debug: bool = False

    class Config:
        env_file = ".env"

# Usage: settings = Settings()
```

### How to Fix

1. **YAGNI** - Don't build what you don't need yet
2. **Rule of three** - Abstract after 3 uses, not before
3. **Start simple** - Refactor when complexity is justified
4. **Question abstractions** - Does this layer add value?
5. **Delete code** - Remove unused flexibility

---

## Poor Error Handling

### Description

Inadequate, inconsistent, or incorrect handling of errors and exceptions.

### Why It's Bad

- Silent failures hide bugs
- Users get unhelpful error messages
- Errors in wrong places make debugging hard
- Can lead to security vulnerabilities
- Inconsistent behavior confuses users

### How to Detect

- Empty except blocks
- Catching `Exception` or bare `except`
- Printing errors instead of proper handling
- No error messages or generic messages
- Error handling at wrong abstraction level

### Examples

```python
# ANTIPATTERN: Poor error handling patterns

# Silent failure
def get_user(user_id):
    try:
        return db.query(User).get(user_id)
    except:  # Catches EVERYTHING, including KeyboardInterrupt
        pass  # Silent failure - caller has no idea what happened

# Too broad exception handling
def process_data(data):
    try:
        result = parse(data)
        transformed = transform(result)
        return save(transformed)
    except Exception as e:
        print(f"Error: {e}")  # Loses stack trace, wrong output channel
        return None

# Hiding useful information
def connect():
    try:
        return database.connect(config.db_url)
    except Exception:
        raise Exception("Database error")  # Original error lost!

# Error handling at wrong level
def calculate_order_total(order):
    total = 0
    for item in order.items:
        try:
            total += item.price * item.quantity
        except:
            pass  # If one item fails, should the whole order fail?
    return total

# REFACTORED: Proper error handling

class DatabaseConnectionError(Exception):
    """Raised when database connection fails."""
    pass

class ValidationError(Exception):
    """Raised when data validation fails."""
    pass

def get_user(user_id: int) -> User:
    """
    Get user by ID.

    Raises:
        UserNotFoundError: If user doesn't exist
        DatabaseConnectionError: If database is unavailable
    """
    try:
        user = db.query(User).get(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found")
        return user
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching user {user_id}: {e}")
        raise DatabaseConnectionError("Unable to fetch user") from e


def process_data(data: dict) -> ProcessResult:
    """
    Process input data through parsing, transformation, and storage.

    Raises:
        ValidationError: If data is invalid
        StorageError: If saving fails
    """
    try:
        parsed = parse(data)
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON data: {e}")
        raise ValidationError(f"Invalid data format: {e}") from e

    try:
        transformed = transform(parsed)
    except TransformError as e:
        logger.error(f"Transform failed: {e}")
        raise ValidationError(f"Data transformation failed: {e}") from e

    try:
        return save(transformed)
    except IOError as e:
        logger.error(f"Save failed: {e}")
        raise StorageError(f"Failed to save result: {e}") from e


def calculate_order_total(order: Order) -> Money:
    """
    Calculate order total.

    Raises:
        OrderValidationError: If any item has invalid price/quantity
    """
    invalid_items = []
    total = Money(0)

    for item in order.items:
        if item.price is None or item.price < 0:
            invalid_items.append(f"Item {item.id}: invalid price")
            continue
        if item.quantity is None or item.quantity < 0:
            invalid_items.append(f"Item {item.id}: invalid quantity")
            continue
        total += item.price * item.quantity

    if invalid_items:
        raise OrderValidationError(
            f"Order has invalid items: {', '.join(invalid_items)}"
        )

    return total
```

### How to Fix

1. **Specific exceptions** - Catch specific exception types
2. **Preserve context** - Use `from e` to chain exceptions
3. **Log appropriately** - Log at correct level with context
4. **Fail fast** - Don't hide errors
5. **Document exceptions** - Include in docstrings

---

## Resource Leaks

### Description

Failing to properly release resources like file handles, database connections, network sockets, or memory.

### Why It's Bad

- Memory exhaustion over time
- File handle exhaustion
- Database connection pool depletion
- Network socket exhaustion
- Application crashes or hangs

### How to Detect

- `open()` without `with` statement
- Manual `close()` that might be skipped
- No `finally` block for cleanup
- Missing context managers
- Connections not returned to pool

### Examples

```python
# ANTIPATTERN: Resource leaks

# File handle leak - close() may never be called
def read_config(path):
    f = open(path)
    data = f.read()
    f.close()  # Not called if exception before this line!
    return json.loads(data)

# Database connection leak
def get_users():
    conn = database.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()
    # Connection never closed!

# Memory leak with large data
def process_large_file(path):
    data = open(path).read()  # Loads entire file into memory
    results = []
    for line in data.split("\n"):  # Creates another copy
        results.append(process(line))
    return results

# Thread/executor leak
def parallel_process(items):
    executor = ThreadPoolExecutor(max_workers=10)
    futures = [executor.submit(process, item) for item in items]
    return [f.result() for f in futures]
    # Executor never shutdown!

# REFACTORED: Proper resource management

# File handling with context manager
def read_config(path: Path) -> dict:
    """Read JSON config file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)

# Database with context manager
def get_users() -> List[User]:
    """Get all users from database."""
    with database.connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            return cursor.fetchall()

# Memory-efficient processing
def process_large_file(path: Path) -> Iterator[ProcessedLine]:
    """Process large file line by line without loading entirely."""
    with open(path, encoding="utf-8") as f:
        for line in f:  # Iterates without loading whole file
            yield process(line.strip())

# Executor with context manager
def parallel_process(items: List[Item]) -> List[Result]:
    """Process items in parallel with proper cleanup."""
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process, item) for item in items]
        return [f.result() for f in futures]

# Custom context manager for resources
from contextlib import contextmanager

@contextmanager
def temporary_directory():
    """Create and clean up temporary directory."""
    tmp_dir = Path(tempfile.mkdtemp())
    try:
        yield tmp_dir
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

# Usage
with temporary_directory() as tmp:
    (tmp / "data.txt").write_text("test")
    process_directory(tmp)
# Directory is cleaned up automatically
```

### How to Fix

1. **Use context managers** - `with` statements ensure cleanup
2. **Try/finally** - When context managers aren't available
3. **Weak references** - For caches that can be garbage collected
4. **Connection pooling** - For database connections
5. **Generator functions** - For memory-efficient iteration

---

## Race Conditions

### Description

Bugs that occur when the behavior depends on the timing or sequence of events, particularly in concurrent code.

### Why It's Bad

- Intermittent, hard-to-reproduce bugs
- Data corruption
- Security vulnerabilities
- Inconsistent application state
- Extremely difficult to debug

### How to Detect

- Shared mutable state without synchronization
- Check-then-act patterns without locking
- Assumptions about operation ordering
- Global variables modified by multiple threads
- File operations without locking

### Examples

```python
# ANTIPATTERN: Race conditions

# Check-then-act race condition
class Counter:
    def __init__(self):
        self.value = 0

    def increment_if_less_than(self, max_value):
        if self.value < max_value:  # Thread A checks
            # Thread B could modify self.value here!
            self.value += 1  # Thread A increments stale value

# Shared mutable state without locking
users_cache = {}  # Global, shared between threads

def get_or_create_user(user_id):
    if user_id not in users_cache:
        # Another thread might create the same user here!
        user = fetch_user_from_db(user_id)
        users_cache[user_id] = user
    return users_cache[user_id]

# File race condition (TOCTOU - Time Of Check to Time Of Use)
def safe_write(path, data):
    if not os.path.exists(path):  # Check
        # Another process could create file here!
        with open(path, "w") as f:  # Use
            f.write(data)

# REFACTORED: Thread-safe patterns

import threading
from threading import Lock

# Proper synchronization with locks
class Counter:
    def __init__(self):
        self.value = 0
        self._lock = Lock()

    def increment_if_less_than(self, max_value: int) -> bool:
        """Atomically increment if below max. Returns True if incremented."""
        with self._lock:
            if self.value < max_value:
                self.value += 1
                return True
            return False

# Thread-safe cache with locking
class ThreadSafeCache:
    def __init__(self):
        self._cache: Dict[int, User] = {}
        self._lock = Lock()

    def get_or_create(self, user_id: int, factory: Callable) -> User:
        """Get cached value or create with factory function."""
        with self._lock:
            if user_id not in self._cache:
                self._cache[user_id] = factory(user_id)
            return self._cache[user_id]

# Atomic file operations
import os

def safe_write(path: Path, data: str) -> None:
    """Write data atomically to prevent partial writes."""
    tmp_path = path.with_suffix(".tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        tmp_path.rename(path)  # Atomic on POSIX systems
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise

# Using atomic operations
from threading import Lock
import os

def exclusive_create(path: Path, data: str) -> bool:
    """Create file only if it doesn't exist."""
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        try:
            os.write(fd, data.encode())
            return True
        finally:
            os.close(fd)
    except FileExistsError:
        return False
```

### How to Fix

1. **Use locks** - Synchronize access to shared state
2. **Atomic operations** - Use atomic APIs when available
3. **Immutable data** - Prefer immutable objects
4. **Message passing** - Use queues instead of shared memory
5. **Thread-local storage** - Isolate state per thread

---

## Quick Reference: Antipattern Detection

| Antipattern | Key Indicator | Severity |
|-------------|---------------|----------|
| God Class | 500+ lines, 20+ methods | High |
| Spaghetti | 4+ nesting levels | High |
| Copy-Paste | Same code 3+ places | Medium |
| Magic Numbers | Unexplained literals | Medium |
| Deep Nesting | Arrow-shaped code | Medium |
| Premature Opt | Complex code without benchmarks | Low |
| Over-Engineering | Abstractions for single use | Medium |
| Poor Error Handling | Empty except, bare except | High |
| Resource Leaks | Missing context managers | High |
| Race Conditions | Shared mutable state | Critical |
| Circular Dependencies | Import cycles | Medium |
| Feature Envy | Class using other class more than self | Low |
| Primitive Obsession | Using primitives instead of types | Low |
| Long Parameters | 5+ function parameters | Medium |
| Dead Code | Unreachable or unused code | Low |

---

## Refactoring Prioritization

When multiple antipatterns exist, prioritize fixes by:

1. **Security issues** - Race conditions, poor error handling
2. **Correctness** - Bugs from any antipattern
3. **Maintainability** - God classes, spaghetti code
4. **Code duplication** - Copy-paste programming
5. **Style issues** - Magic numbers, naming
