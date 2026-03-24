# Security Review Checklist

A comprehensive security checklist for code reviews, based on OWASP guidelines and industry best practices.

## Table of Contents

1. [Input Validation](#input-validation)
2. [Authentication](#authentication)
3. [Authorization](#authorization)
4. [Session Management](#session-management)
5. [SQL Injection Prevention](#sql-injection-prevention)
6. [Cross-Site Scripting (XSS)](#cross-site-scripting-xss)
7. [Cross-Site Request Forgery (CSRF)](#cross-site-request-forgery-csrf)
8. [Sensitive Data Handling](#sensitive-data-handling)
9. [Cryptography](#cryptography)
10. [Secret Management](#secret-management)
11. [Dependency Security](#dependency-security)
12. [Logging and Monitoring](#logging-and-monitoring)
13. [API Security](#api-security)
14. [File Operations](#file-operations)
15. [OWASP Top 10 Quick Reference](#owasp-top-10-quick-reference)

---

## Input Validation

### Checklist

- [ ] All user input is validated before processing
- [ ] Validation happens on the server side (not just client)
- [ ] Input length limits are enforced
- [ ] Data types are validated
- [ ] Whitelist validation is preferred over blacklist
- [ ] Special characters are properly handled

### Vulnerable vs Secure Patterns

```python
# VULNERABLE: No input validation
@app.route("/search")
def search():
    query = request.args.get("q")
    return db.execute(f"SELECT * FROM items WHERE name LIKE '%{query}%'")

# SECURE: Proper validation and parameterization
from pydantic import BaseModel, Field, validator

class SearchQuery(BaseModel):
    q: str = Field(..., min_length=1, max_length=100)

    @validator("q")
    def sanitize_query(cls, v):
        # Remove potentially dangerous characters
        return re.sub(r"[^\w\s-]", "", v)

@app.route("/search")
def search():
    try:
        query = SearchQuery(q=request.args.get("q", ""))
        return db.execute(
            "SELECT * FROM items WHERE name LIKE :query",
            {"query": f"%{query.q}%"}
        )
    except ValidationError as e:
        return {"error": "Invalid search query"}, 400
```

### Input Validation Guidelines

| Input Type | Validation Rules |
|------------|-----------------|
| Email | Regex pattern, max length 254 |
| Username | Alphanumeric, 3-50 chars, no spaces |
| Password | Min 8 chars, complexity requirements |
| Phone | Digits only, length 10-15 |
| URL | Valid URL format, allowed schemes only |
| File upload | Extension whitelist, size limit, content type |
| Numeric | Range limits, integer vs float |
| Date | Valid format, reasonable range |

---

## Authentication

### Checklist

- [ ] Passwords are hashed with strong algorithms (bcrypt, argon2)
- [ ] No plaintext password storage or transmission
- [ ] Account lockout after failed attempts
- [ ] Secure password reset flow
- [ ] Multi-factor authentication available for sensitive operations
- [ ] Login attempts are rate-limited
- [ ] Session tokens are regenerated after login

### Password Hashing

```python
# VULNERABLE: Weak or no hashing
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()  # MD5 is broken
password_hash = hashlib.sha256(password.encode()).hexdigest()  # No salt!

# SECURE: Using bcrypt with proper settings
import bcrypt

def hash_password(password: str) -> str:
    """Hash a password with bcrypt."""
    salt = bcrypt.gensalt(rounds=12)  # Work factor of 12
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode(), password_hash.encode())

# SECURE: Using argon2 (recommended for new projects)
from argon2 import PasswordHasher

ph = PasswordHasher(
    time_cost=3,      # Number of iterations
    memory_cost=65536,  # Memory usage in KB
    parallelism=4     # Parallel threads
)

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    try:
        ph.verify(password_hash, password)
        return True
    except Exception:
        return False
```

### Account Lockout Implementation

```python
# SECURE: Rate limiting and lockout
from datetime import datetime, timedelta
from typing import Optional

class LoginAttemptTracker:
    def __init__(self, max_attempts: int = 5, lockout_minutes: int = 15):
        self.max_attempts = max_attempts
        self.lockout_duration = timedelta(minutes=lockout_minutes)
        self.attempts: dict[str, list[datetime]] = {}
        self.lockouts: dict[str, datetime] = {}

    def is_locked_out(self, username: str) -> bool:
        """Check if account is currently locked."""
        if username in self.lockouts:
            if datetime.now() < self.lockouts[username]:
                return True
            del self.lockouts[username]
        return False

    def record_failed_attempt(self, username: str) -> None:
        """Record a failed login attempt."""
        now = datetime.now()
        window_start = now - timedelta(minutes=15)

        # Clean old attempts
        if username in self.attempts:
            self.attempts[username] = [
                t for t in self.attempts[username] if t > window_start
            ]
        else:
            self.attempts[username] = []

        self.attempts[username].append(now)

        if len(self.attempts[username]) >= self.max_attempts:
            self.lockouts[username] = now + self.lockout_duration

    def clear_attempts(self, username: str) -> None:
        """Clear attempts after successful login."""
        self.attempts.pop(username, None)
        self.lockouts.pop(username, None)
```

---

## Authorization

### Checklist

- [ ] All endpoints check user authorization
- [ ] Role-based access control is implemented
- [ ] Users cannot access other users' data
- [ ] Admin functions are properly protected
- [ ] Authorization checks happen on every request
- [ ] Principle of least privilege is followed

### Insecure Direct Object Reference (IDOR) Prevention

```python
# VULNERABLE: No authorization check
@app.route("/users/<user_id>/profile")
def get_profile(user_id):
    # Any user can access any profile by changing the URL!
    return db.get_user(user_id)

# SECURE: Proper authorization check
@app.route("/users/<user_id>/profile")
@login_required
def get_profile(user_id):
    current_user = get_current_user()

    # Users can only access their own profile (unless admin)
    if current_user.id != int(user_id) and not current_user.is_admin:
        abort(403, "Access denied")

    return db.get_user(user_id)

# SECURE: Better pattern - don't expose internal IDs
@app.route("/profile")
@login_required
def get_own_profile():
    """Get current user's profile - no ID needed."""
    return db.get_user(get_current_user().id)
```

### Role-Based Access Control

```python
from enum import Enum
from functools import wraps

class Role(Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

ROLE_HIERARCHY = {
    Role.USER: 0,
    Role.MODERATOR: 1,
    Role.ADMIN: 2,
}

def requires_role(minimum_role: Role):
    """Decorator to require minimum role level."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user = get_current_user()
            if not current_user:
                abort(401, "Authentication required")

            user_level = ROLE_HIERARCHY.get(current_user.role, -1)
            required_level = ROLE_HIERARCHY.get(minimum_role, 999)

            if user_level < required_level:
                abort(403, f"Requires {minimum_role.value} role or higher")

            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@app.route("/admin/users")
@requires_role(Role.ADMIN)
def list_all_users():
    return db.get_all_users()
```

---

## Session Management

### Checklist

- [ ] Sessions use secure, random identifiers
- [ ] Session cookies have Secure, HttpOnly, and SameSite flags
- [ ] Sessions expire after appropriate timeout
- [ ] Sessions are invalidated on logout
- [ ] Session fixation is prevented (regenerate on login)
- [ ] Concurrent session limits are enforced if needed

### Secure Cookie Configuration

```python
# VULNERABLE: Insecure cookie settings
response.set_cookie("session_id", session_id)

# SECURE: Proper cookie security
app.config.update(
    SESSION_COOKIE_SECURE=True,      # Only send over HTTPS
    SESSION_COOKIE_HTTPONLY=True,    # Not accessible via JavaScript
    SESSION_COOKIE_SAMESITE="Lax",   # CSRF protection
    SESSION_COOKIE_NAME="__Host-session",  # Cookie prefix for extra security
    PERMANENT_SESSION_LIFETIME=timedelta(hours=24),
)

# Or manually setting cookies
response.set_cookie(
    key="session_id",
    value=session_id,
    secure=True,
    httponly=True,
    samesite="Lax",
    max_age=86400,  # 24 hours
    domain=None,    # Current domain only
    path="/"
)
```

---

## SQL Injection Prevention

### Checklist

- [ ] All database queries use parameterized queries
- [ ] No string concatenation for SQL queries
- [ ] ORM is used where possible
- [ ] Stored procedures use parameters
- [ ] Database user has minimal privileges

### SQL Injection Patterns

```python
# VULNERABLE: String concatenation
def get_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)

# VULNERABLE: Format strings
def get_user(username):
    query = "SELECT * FROM users WHERE username = '%s'" % username
    return db.execute(query)

# VULNERABLE: String format method
def get_user(username):
    query = "SELECT * FROM users WHERE username = '{}'".format(username)
    return db.execute(query)

# SECURE: Parameterized queries
def get_user(username):
    query = "SELECT * FROM users WHERE username = :username"
    return db.execute(query, {"username": username})

# SECURE: Using ORM (SQLAlchemy example)
def get_user(username):
    return session.query(User).filter(User.username == username).first()

# SECURE: Prepared statements
def get_user(username):
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    return cursor.fetchone()
```

### SQL Injection Attack Examples

| Attack Type | Example Input | Impact |
|-------------|---------------|--------|
| Basic injection | `' OR '1'='1` | Bypass authentication |
| UNION attack | `' UNION SELECT password FROM users--` | Data extraction |
| Stacked queries | `'; DROP TABLE users;--` | Data destruction |
| Blind injection | `' AND (SELECT COUNT(*) FROM users) > 0--` | Information disclosure |
| Time-based | `' AND SLEEP(5)--` | Confirming vulnerability |

---

## Cross-Site Scripting (XSS)

### Checklist

- [ ] All user input is HTML-encoded before rendering
- [ ] Content Security Policy (CSP) headers are set
- [ ] JavaScript uses safe DOM manipulation methods
- [ ] Rich text editors sanitize input
- [ ] HTTP-only cookies prevent script access

### XSS Prevention Patterns

```python
# VULNERABLE: Rendering user input directly
@app.route("/greet")
def greet():
    name = request.args.get("name", "")
    return f"<h1>Hello, {name}!</h1>"  # XSS if name contains <script>

# SECURE: Using template auto-escaping
# templates/greet.html: <h1>Hello, {{ name }}!</h1>
@app.route("/greet")
def greet():
    name = request.args.get("name", "")
    return render_template("greet.html", name=name)

# SECURE: Manual escaping when needed
from markupsafe import escape

@app.route("/greet")
def greet():
    name = escape(request.args.get("name", ""))
    return f"<h1>Hello, {name}!</h1>"
```

### Content Security Policy

```python
# SECURE: Setting CSP headers
@app.after_request
def add_security_headers(response):
    # Content Security Policy
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self' https://api.example.com; "
        "frame-ancestors 'none';"
    )
    response.headers["Content-Security-Policy"] = csp
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

---

## Cross-Site Request Forgery (CSRF)

### Checklist

- [ ] CSRF tokens are used for state-changing operations
- [ ] Tokens are validated on the server
- [ ] SameSite cookie attribute is set
- [ ] Origin/Referer headers are validated
- [ ] GET requests don't modify state

### CSRF Token Implementation

```python
# SECURE: CSRF protection with Flask-WTF
from flask_wtf.csrf import CSRFProtect, generate_csrf

csrf = CSRFProtect(app)

# In template:
# <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">

# For AJAX requests
@app.route("/api/transfer", methods=["POST"])
@csrf.exempt  # Only if using header-based token
def transfer_funds():
    # Validate CSRF token from header
    token = request.headers.get("X-CSRF-Token")
    if not validate_csrf_token(token):
        abort(403, "Invalid CSRF token")
    # Process transfer...

# SECURE: Manual CSRF implementation
import secrets

def generate_csrf_token(session_id: str) -> str:
    """Generate a CSRF token tied to the session."""
    token = secrets.token_urlsafe(32)
    cache.set(f"csrf:{session_id}", token, expire=3600)
    return token

def validate_csrf_token(session_id: str, token: str) -> bool:
    """Validate CSRF token."""
    stored_token = cache.get(f"csrf:{session_id}")
    if not stored_token:
        return False
    return secrets.compare_digest(stored_token, token)
```

---

## Sensitive Data Handling

### Checklist

- [ ] Sensitive data is encrypted at rest
- [ ] Data is encrypted in transit (HTTPS)
- [ ] PII is minimized and retention limited
- [ ] Data masking in logs and error messages
- [ ] Secure deletion of sensitive data
- [ ] Memory is cleared after use for secrets

### Data Masking

```python
import re

def mask_credit_card(card_number: str) -> str:
    """Mask credit card number, showing only last 4 digits."""
    return re.sub(r"\d(?=\d{4})", "*", card_number)

def mask_email(email: str) -> str:
    """Mask email address."""
    local, domain = email.split("@")
    masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
    return f"{masked_local}@{domain}"

def mask_ssn(ssn: str) -> str:
    """Mask SSN showing only last 4."""
    return "***-**-" + ssn[-4:]

# Usage in logging
logger.info(f"Processing payment for card {mask_credit_card(card_number)}")
```

### Secure Data Deletion

```python
import secrets

def secure_delete_string(s: str) -> None:
    """Attempt to securely delete string contents from memory."""
    # Python strings are immutable, so this is best-effort
    # For truly sensitive data, use specialized libraries
    pass

def secure_delete_bytes(b: bytearray) -> None:
    """Securely overwrite bytearray with random data."""
    for i in range(len(b)):
        b[i] = secrets.randbelow(256)
    for i in range(len(b)):
        b[i] = 0
```

---

## Cryptography

### Checklist

- [ ] Using modern, secure algorithms (AES-256, ChaCha20)
- [ ] Not using broken algorithms (MD5, SHA1 for security, DES)
- [ ] Proper key management
- [ ] Using authenticated encryption (GCM mode)
- [ ] Random IVs/nonces for each encryption
- [ ] Keys are of appropriate length

### Secure Encryption Patterns

```python
# VULNERABLE: Using ECB mode
from Crypto.Cipher import AES
cipher = AES.new(key, AES.MODE_ECB)  # ECB reveals patterns!

# VULNERABLE: Reusing IV
cipher = AES.new(key, AES.MODE_CBC, iv=static_iv)  # IV must be unique!

# SECURE: AES-GCM with random nonce
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def encrypt(plaintext: bytes, key: bytes) -> bytes:
    """Encrypt data using AES-GCM."""
    nonce = os.urandom(12)  # 96-bit nonce
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return nonce + ciphertext  # Prepend nonce

def decrypt(data: bytes, key: bytes) -> bytes:
    """Decrypt AES-GCM encrypted data."""
    nonce = data[:12]
    ciphertext = data[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)

# SECURE: Using Fernet (simpler API)
from cryptography.fernet import Fernet

key = Fernet.generate_key()  # Store this securely
f = Fernet(key)

encrypted = f.encrypt(b"sensitive data")
decrypted = f.decrypt(encrypted)
```

---

## Secret Management

### Checklist

- [ ] No secrets in source code
- [ ] No secrets in version control
- [ ] Environment variables or secret manager used
- [ ] Secrets are rotated regularly
- [ ] Different secrets for dev/staging/prod
- [ ] Access to secrets is audited

### Secure Secret Handling

```python
# VULNERABLE: Hardcoded secrets
API_KEY = "sk-1234567890abcdef"
DATABASE_URL = "postgresql://admin:password123@localhost/db"

# VULNERABLE: Secrets in config files committed to git
# config.py (in git)
API_KEY = "sk-1234567890abcdef"

# SECURE: Environment variables
import os

API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY environment variable required")

# SECURE: Using pydantic-settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str
    database_url: str
    secret_key: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# SECURE: Using secret manager (AWS Secrets Manager)
import boto3
import json

def get_secret(secret_name: str) -> dict:
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])
```

---

## Dependency Security

### Checklist

- [ ] Dependencies are regularly updated
- [ ] Known vulnerabilities are scanned (pip-audit, npm audit)
- [ ] Dependency versions are pinned
- [ ] Only necessary dependencies are installed
- [ ] Dependencies come from trusted sources

### Dependency Scanning

```bash
# Python
pip install pip-audit
pip-audit

# Check for known vulnerabilities
pip install safety
safety check

# Pin dependencies
pip freeze > requirements.txt
# Or better, use pip-tools
pip-compile requirements.in

# npm (JavaScript)
npm audit
npm audit fix
```

---

## Logging and Monitoring

### Checklist

- [ ] Security events are logged
- [ ] No sensitive data in logs
- [ ] Logs are tamper-evident
- [ ] Alerts for suspicious activity
- [ ] Log retention policy defined
- [ ] Structured logging format used

### Security Event Logging

```python
import logging
import json
from datetime import datetime

class SecurityLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(f"security.{name}")

    def log_event(
        self,
        event_type: str,
        user_id: str = None,
        ip_address: str = None,
        details: dict = None,
        severity: str = "INFO"
    ):
        """Log a security event in structured format."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "details": details or {},
            "severity": severity
        }

        log_method = getattr(self.logger, severity.lower(), self.logger.info)
        log_method(json.dumps(event))

# Usage
security_log = SecurityLogger("auth")

security_log.log_event(
    "LOGIN_FAILED",
    user_id="user123",
    ip_address="192.168.1.1",
    details={"reason": "invalid_password", "attempts": 3},
    severity="WARNING"
)

security_log.log_event(
    "PRIVILEGE_ESCALATION_ATTEMPT",
    user_id="user123",
    ip_address="192.168.1.1",
    details={"attempted_role": "admin"},
    severity="CRITICAL"
)
```

---

## API Security

### Checklist

- [ ] API authentication required (API keys, OAuth, JWT)
- [ ] Rate limiting implemented
- [ ] Input validation on all endpoints
- [ ] HTTPS enforced
- [ ] Proper CORS configuration
- [ ] API versioning strategy

### Rate Limiting

```python
from functools import wraps
import time

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.limit = requests_per_minute
        self.window = 60  # seconds
        self.requests: dict[str, list[float]] = {}

    def is_allowed(self, identifier: str) -> bool:
        """Check if request is within rate limit."""
        now = time.time()
        window_start = now - self.window

        if identifier not in self.requests:
            self.requests[identifier] = []

        # Clean old requests
        self.requests[identifier] = [
            t for t in self.requests[identifier] if t > window_start
        ]

        if len(self.requests[identifier]) >= self.limit:
            return False

        self.requests[identifier].append(now)
        return True

rate_limiter = RateLimiter(requests_per_minute=100)

def rate_limit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        identifier = get_client_identifier()  # IP or API key
        if not rate_limiter.is_allowed(identifier):
            abort(429, "Rate limit exceeded")
        return func(*args, **kwargs)
    return wrapper
```

---

## File Operations

### Checklist

- [ ] File paths are validated (no traversal)
- [ ] File types are validated
- [ ] File sizes are limited
- [ ] Uploaded files stored outside web root
- [ ] Filenames are sanitized

### Path Traversal Prevention

```python
from pathlib import Path
import os

# VULNERABLE: Direct path concatenation
def read_file(filename):
    with open(f"/uploads/{filename}") as f:
        return f.read()
# Attack: filename="../../etc/passwd"

# SECURE: Path validation
def read_file_secure(filename: str, base_dir: Path) -> str:
    """Read file ensuring it's within allowed directory."""
    # Resolve the full path
    base_dir = base_dir.resolve()
    target_path = (base_dir / filename).resolve()

    # Check if target is within base directory
    if not target_path.is_relative_to(base_dir):
        raise SecurityError("Access denied: path traversal detected")

    if not target_path.exists():
        raise FileNotFoundError(f"File not found: {filename}")

    return target_path.read_text()
```

---

## OWASP Top 10 Quick Reference

| Rank | Vulnerability | Key Mitigations |
|------|--------------|-----------------|
| A01 | Broken Access Control | Authorization checks, RBAC, deny by default |
| A02 | Cryptographic Failures | TLS, strong encryption, proper key management |
| A03 | Injection | Parameterized queries, input validation, ORMs |
| A04 | Insecure Design | Threat modeling, secure design patterns |
| A05 | Security Misconfiguration | Secure defaults, hardening, updates |
| A06 | Vulnerable Components | Dependency scanning, regular updates |
| A07 | Auth Failures | MFA, secure passwords, session management |
| A08 | Data Integrity Failures | Signed updates, CI/CD security, integrity checks |
| A09 | Logging Failures | Audit logging, monitoring, alerting |
| A10 | Server-Side Request Forgery | URL validation, allowlists, network segmentation |

---

## Security Review Severity Ratings

| Severity | Criteria | Response Time |
|----------|----------|---------------|
| **Critical** | Actively exploitable, data breach risk | Immediate fix required |
| **High** | Serious vulnerability, likely exploitable | Fix within 24-48 hours |
| **Medium** | Moderate risk, requires specific conditions | Fix within 1 week |
| **Low** | Minor issue, limited impact | Fix in next release |
| **Info** | Best practice recommendation | Consider for improvement |
