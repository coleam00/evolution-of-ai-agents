# Code Best Practices Guide

A comprehensive guide to writing clean, maintainable, and professional code.

## Table of Contents

1. [Code Organization](#code-organization)
2. [Naming Conventions](#naming-conventions)
3. [Function Design](#function-design)
4. [Error Handling](#error-handling)
5. [Documentation](#documentation)
6. [Testing Principles](#testing-principles)
7. [Code Style](#code-style)
8. [Performance Considerations](#performance-considerations)

---

## Code Organization

### Module Structure

Organize code into logical modules with clear responsibilities:

```python
# Good: Clear module structure
project/
├── src/
│   ├── models/          # Data models and schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── product.py
│   ├── services/        # Business logic
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── payments.py
│   ├── api/             # API endpoints
│   │   ├── __init__.py
│   │   └── routes.py
│   └── utils/           # Shared utilities
│       ├── __init__.py
│       └── helpers.py
├── tests/
└── config/
```

### Single Responsibility Principle

Each module, class, and function should have one clear purpose:

```python
# Bad: Multiple responsibilities in one class
class UserManager:
    def create_user(self, data): ...
    def send_email(self, to, subject, body): ...
    def generate_report(self, users): ...
    def backup_database(self): ...

# Good: Separated responsibilities
class UserService:
    def create_user(self, data): ...
    def get_user(self, user_id): ...
    def update_user(self, user_id, data): ...

class EmailService:
    def send_email(self, to, subject, body): ...

class ReportGenerator:
    def generate_user_report(self, users): ...
```

### Import Organization

Organize imports in a consistent order:

```python
# Standard library imports
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Third-party imports
import requests
from pydantic import BaseModel

# Local imports
from src.models import User
from src.services import AuthService
```

### File Length Guidelines

| Component | Recommended Max Lines | Notes |
|-----------|----------------------|-------|
| Module/File | 300-500 | Split if exceeding |
| Class | 200-300 | Consider extraction |
| Function | 20-50 | Definitely split if > 50 |
| Line length | 88-120 | Follow project standard |

---

## Naming Conventions

### General Principles

- **Be descriptive**: Names should explain purpose without needing comments
- **Be consistent**: Use the same conventions throughout the codebase
- **Avoid abbreviations**: Unless universally understood (e.g., `id`, `url`, `http`)

### Variables

```python
# Bad: Unclear names
x = 10
temp = users[0]
data = process()

# Good: Descriptive names
max_retry_attempts = 10
first_user = users[0]
processed_orders = process_pending_orders()
```

### Boolean Variables

Use prefixes that indicate boolean nature:

```python
# Good boolean names
is_active = True
has_permission = False
can_edit = user.role == "admin"
should_retry = attempt_count < max_attempts
was_successful = response.status_code == 200
```

### Functions and Methods

Use verbs that describe the action:

```python
# Bad: Noun-based or unclear names
def user_data():
    pass

def process():
    pass

# Good: Verb-based, action-oriented names
def get_user_by_id(user_id: int) -> User:
    pass

def process_payment(order: Order) -> Receipt:
    pass

def validate_email_format(email: str) -> bool:
    pass

def send_notification(user: User, message: str) -> None:
    pass
```

### Classes

Use PascalCase with nouns:

```python
# Good class names
class UserAccount:
    pass

class PaymentProcessor:
    pass

class EmailNotificationService:
    pass

class DatabaseConnectionPool:
    pass
```

### Constants

Use SCREAMING_SNAKE_CASE:

```python
# Good constant definitions
MAX_CONNECTIONS = 100
DEFAULT_TIMEOUT_SECONDS = 30
API_BASE_URL = "https://api.example.com"
SUPPORTED_FILE_TYPES = frozenset({"pdf", "doc", "txt"})
```

### Naming Convention Summary Table

| Type | Convention | Example |
|------|-----------|---------|
| Variables | snake_case | `user_count`, `total_price` |
| Functions | snake_case | `calculate_total()`, `get_user()` |
| Classes | PascalCase | `UserService`, `DataProcessor` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_SIZE`, `API_KEY` |
| Private | Leading underscore | `_internal_method()`, `_cache` |
| Protected | Single underscore | `_helper_method()` |
| Type variables | PascalCase | `T`, `KeyType`, `ValueType` |
| Modules | snake_case | `user_service.py`, `data_utils.py` |

---

## Function Design

### Single Responsibility

Each function should do one thing well:

```python
# Bad: Multiple responsibilities
def process_user_registration(data):
    # Validate
    if not data.get("email"):
        raise ValueError("Email required")
    if not is_valid_email(data["email"]):
        raise ValueError("Invalid email")

    # Create user
    user = User(**data)
    db.save(user)

    # Send welcome email
    send_email(user.email, "Welcome!", f"Hi {user.name}")

    # Log analytics
    analytics.track("user_registered", user.id)

    return user

# Good: Separated concerns
def validate_registration_data(data: dict) -> None:
    """Validate user registration data."""
    if not data.get("email"):
        raise ValueError("Email required")
    if not is_valid_email(data["email"]):
        raise ValueError("Invalid email format")

def create_user(data: dict) -> User:
    """Create and persist a new user."""
    user = User(**data)
    db.save(user)
    return user

def handle_new_user_registration(data: dict) -> User:
    """Orchestrate user registration process."""
    validate_registration_data(data)
    user = create_user(data)
    send_welcome_email(user)
    track_registration_event(user)
    return user
```

### Pure Functions

Prefer pure functions when possible (no side effects, same input = same output):

```python
# Impure: Depends on external state, modifies global
discount_rate = 0.1
def calculate_price(base_price):
    global discount_rate
    discount_rate += 0.01  # Side effect!
    return base_price * (1 - discount_rate)

# Pure: No side effects, predictable
def calculate_discounted_price(base_price: float, discount_rate: float) -> float:
    """Calculate price with discount applied."""
    return base_price * (1 - discount_rate)
```

### Function Parameters

- Limit to 3-5 parameters
- Use keyword arguments for clarity
- Group related parameters into objects

```python
# Bad: Too many parameters
def create_report(
    title, start_date, end_date, include_charts, chart_type,
    color_scheme, font_size, page_size, orientation, author
):
    pass

# Good: Grouped into config object
@dataclass
class ReportConfig:
    include_charts: bool = True
    chart_type: str = "bar"
    color_scheme: str = "default"
    font_size: int = 12
    page_size: str = "A4"
    orientation: str = "portrait"

def create_report(
    title: str,
    date_range: DateRange,
    config: ReportConfig,
    author: str
) -> Report:
    pass
```

### Return Values

Be consistent and explicit about return values:

```python
# Bad: Inconsistent returns
def find_user(user_id):
    user = db.query(user_id)
    if user:
        return user
    # Implicit None return

# Good: Explicit and typed
def find_user(user_id: int) -> Optional[User]:
    """Find user by ID, returns None if not found."""
    return db.query(User).filter(User.id == user_id).first()

# Better for most cases: Raise exception
def get_user(user_id: int) -> User:
    """Get user by ID, raises UserNotFoundError if not found."""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise UserNotFoundError(f"User {user_id} not found")
    return user
```

---

## Error Handling

### Exception Hierarchy

Use appropriate exception types:

```python
# Define custom exceptions for your domain
class AppError(Exception):
    """Base exception for application errors."""
    pass

class ValidationError(AppError):
    """Raised when input validation fails."""
    pass

class NotFoundError(AppError):
    """Raised when a requested resource is not found."""
    pass

class AuthenticationError(AppError):
    """Raised when authentication fails."""
    pass

class AuthorizationError(AppError):
    """Raised when user lacks required permissions."""
    pass
```

### Try/Except Best Practices

```python
# Bad: Catching everything
try:
    result = risky_operation()
except:  # Catches everything including KeyboardInterrupt!
    pass

# Bad: Too broad
try:
    result = risky_operation()
except Exception as e:
    log.error(f"Error: {e}")

# Good: Specific exception handling
try:
    result = external_api_call()
except requests.Timeout:
    log.warning("API call timed out, retrying...")
    result = retry_api_call()
except requests.HTTPError as e:
    if e.response.status_code == 404:
        raise ResourceNotFoundError(f"Resource not found") from e
    raise ExternalServiceError(f"API error: {e}") from e
```

### Error Messages

Write helpful error messages:

```python
# Bad: Unhelpful
raise ValueError("Invalid input")

# Good: Specific and actionable
raise ValueError(
    f"Invalid email format: '{email}'. "
    f"Expected format: user@domain.com"
)

# Good: Include context
raise ConfigurationError(
    f"Database connection failed: {error}. "
    f"Check DATABASE_URL environment variable is set correctly. "
    f"Current value: {db_url[:20]}..."
)
```

### Resource Cleanup

Always clean up resources properly:

```python
# Good: Context manager for file handling
def read_config(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)

# Good: Context manager for database
def process_records():
    with db.session() as session:
        records = session.query(Record).all()
        for record in records:
            process(record)
        session.commit()

# Good: Custom context manager
@contextmanager
def temporary_directory():
    """Create a temporary directory that's cleaned up after use."""
    tmp_dir = Path(tempfile.mkdtemp())
    try:
        yield tmp_dir
    finally:
        shutil.rmtree(tmp_dir)
```

---

## Documentation

### Docstrings

Use Google-style docstrings for functions:

```python
def process_order(
    order: Order,
    payment_method: PaymentMethod,
    apply_discount: bool = False
) -> Receipt:
    """
    Process an order and generate a receipt.

    Validates the order, processes payment, and creates a receipt.
    If payment fails, the order status is set to 'payment_failed'.

    Args:
        order: The order to process
        payment_method: Payment method to use for this transaction
        apply_discount: Whether to apply any available discounts

    Returns:
        A Receipt object containing transaction details

    Raises:
        InvalidOrderError: If order validation fails
        PaymentError: If payment processing fails
        InsufficientInventoryError: If ordered items are out of stock

    Example:
        >>> order = Order(items=[Item("SKU123", quantity=2)])
        >>> receipt = process_order(order, PaymentMethod.CREDIT_CARD)
        >>> print(receipt.total)
        49.99
    """
    pass
```

### Class Documentation

```python
class UserService:
    """
    Service for managing user accounts.

    Handles user creation, authentication, and profile management.
    All operations are logged and audit-trailed.

    Attributes:
        db: Database session for persistence
        cache: Redis cache for session data
        email_service: Service for sending user emails

    Example:
        >>> service = UserService(db_session, cache, email_svc)
        >>> user = service.create_user({"email": "test@example.com"})
        >>> assert user.is_active
    """

    def __init__(
        self,
        db: Session,
        cache: RedisCache,
        email_service: EmailService
    ) -> None:
        """
        Initialize UserService with required dependencies.

        Args:
            db: SQLAlchemy database session
            cache: Redis cache instance
            email_service: Email service for notifications
        """
        self.db = db
        self.cache = cache
        self.email_service = email_service
```

### Inline Comments

Use sparingly and explain *why*, not *what*:

```python
# Bad: Explains what (obvious from code)
# Increment counter by 1
counter += 1

# Good: Explains why
# Use exponential backoff to avoid overwhelming the server
delay = base_delay * (2 ** attempt_number)

# Good: Explains complex business logic
# Orders over $100 get free shipping, but hazmat items
# are excluded per regulations (see policy doc #1234)
if order.total >= 100 and not order.contains_hazmat:
    order.shipping_cost = 0
```

---

## Testing Principles

### Test Structure (AAA Pattern)

```python
def test_user_creation():
    # Arrange - Set up test data and conditions
    email = "test@example.com"
    name = "Test User"
    service = UserService(mock_db)

    # Act - Execute the code being tested
    user = service.create_user(email=email, name=name)

    # Assert - Verify the results
    assert user.email == email
    assert user.name == name
    assert user.is_active is True
```

### Test Naming

```python
# Good: Descriptive test names
def test_create_user_with_valid_email_succeeds():
    pass

def test_create_user_with_invalid_email_raises_validation_error():
    pass

def test_delete_user_removes_associated_sessions():
    pass

def test_login_with_wrong_password_increments_failed_attempts():
    pass
```

### Test Coverage Guidelines

| Component | Minimum Coverage | Priority Tests |
|-----------|-----------------|----------------|
| Business logic | 80-90% | Critical paths, edge cases |
| API endpoints | 70-80% | Happy path, error responses |
| Utilities | 90%+ | All exported functions |
| Data models | 60-70% | Validation, serialization |

### Test Best Practices

```python
# Good: Independent tests (no shared state)
@pytest.fixture
def user_service():
    """Fresh service instance for each test."""
    return UserService(create_test_db())

def test_create_user(user_service):
    user = user_service.create_user({"email": "a@b.com"})
    assert user is not None

def test_delete_user(user_service):
    # Uses fresh service, not affected by other tests
    user = user_service.create_user({"email": "a@b.com"})
    user_service.delete_user(user.id)
    assert user_service.get_user(user.id) is None

# Good: Test edge cases
@pytest.mark.parametrize("invalid_email", [
    "",
    "not-an-email",
    "@missing-local.com",
    "missing-domain@",
    "spaces in@email.com",
])
def test_create_user_rejects_invalid_emails(user_service, invalid_email):
    with pytest.raises(ValidationError):
        user_service.create_user({"email": invalid_email})
```

---

## Code Style

### Consistency

- Choose a style guide and follow it consistently
- Use automated formatters (black, prettier)
- Configure linters (ruff, eslint)

### Whitespace and Formatting

```python
# Good: Consistent spacing
def calculate_total(
    items: List[Item],
    tax_rate: float = 0.08,
    discount: Optional[float] = None
) -> float:
    subtotal = sum(item.price * item.quantity for item in items)

    if discount:
        subtotal *= (1 - discount)

    total = subtotal * (1 + tax_rate)
    return round(total, 2)
```

### Type Hints

Always use type hints for function signatures:

```python
from typing import Dict, List, Optional, Union

def process_data(
    data: Dict[str, Any],
    options: Optional[ProcessingOptions] = None
) -> ProcessingResult:
    pass

def fetch_users(
    ids: List[int],
    include_inactive: bool = False
) -> List[User]:
    pass
```

---

## Performance Considerations

### Avoid Premature Optimization

```python
# Don't optimize until you've measured
# Profile first, then optimize bottlenecks

# Usually fine for most cases
users = [process(u) for u in all_users]

# Only if profiling shows this is a bottleneck
# and memory is constrained
users = (process(u) for u in all_users)  # Generator
```

### Common Performance Patterns

```python
# Good: Use appropriate data structures
# O(1) lookup instead of O(n) for membership tests
user_ids = set(u.id for u in users)  # Use set, not list
if target_id in user_ids:
    pass

# Good: Batch database operations
# Instead of N queries
for user in users:
    db.save(user)  # Bad: N separate commits

# Do one batch operation
db.bulk_save(users)  # Good: Single transaction

# Good: Use database-level filtering
# Instead of fetching all and filtering in Python
active_users = [u for u in db.get_all_users() if u.is_active]  # Bad

# Let the database do the filtering
active_users = db.query(User).filter(User.is_active == True).all()  # Good
```

### Resource Management

```python
# Good: Limit concurrent operations
async def fetch_all_urls(urls: List[str]) -> List[Response]:
    """Fetch URLs with concurrency limit to avoid overwhelming servers."""
    semaphore = asyncio.Semaphore(10)  # Max 10 concurrent

    async def fetch_with_limit(url: str) -> Response:
        async with semaphore:
            return await fetch(url)

    return await asyncio.gather(*[fetch_with_limit(u) for u in urls])
```

---

## Quick Reference Checklist

### Before Committing Code

- [ ] All functions have type hints
- [ ] Complex logic has docstrings
- [ ] No hardcoded credentials or secrets
- [ ] Error messages are helpful
- [ ] No unused imports or variables
- [ ] Tests exist for new functionality
- [ ] Code passes linting checks
- [ ] No `print()` statements (use logging)

### Code Review Focus Areas

1. **Correctness**: Does it do what it's supposed to?
2. **Clarity**: Can someone new understand it?
3. **Consistency**: Does it follow project conventions?
4. **Completeness**: Are edge cases handled?
5. **Security**: Are there any vulnerabilities?
6. **Performance**: Any obvious inefficiencies?
