<div align="center">
  <img src="logo-horizontal.svg" alt="pfly - Python LOggling Linter" width="400">
  <br>
  <br>
  <p><strong>A Python logging linter that enforces best practices</strong></p>
</div>

## Why?

Production incidents are harder to debug when:
- Exception logs lack stack traces (`exc_info=True`)
- Hot loops spam logs, degrading performance
- Inconsistent logging causes time delay in parsing logs
- **Complementary**: Use with `structlog`, `loguru` — not instead of them

## Installation

```bash
uv pip install pfly
```

## Usage

```bash
pfly path/to/code

pfly path/to/code --config=pfly.yml
```

## Policies

| Code | Policy | Description |
|------|--------|-------------|
| **LY001** | `exception_exc_info` | Enforces `exc_info=True` for logs in exception handlers to capture stack traces in a consistent format |
| **LY002** | `log_loop` | Prevents unconditional logging in hot loops (allows conditional logging) |
| **LY003** | `consistent_kv` | Ensures log variables follow key-value format for consistent parsing |

## Configuration

Create a `pfly.yml`:

```yaml
logger_names: [logger, logging, log]

exception_exc_info:
  levels: [error]
  severity: fail

log_loop:
  levels: [info, debug]
  severity: fail
```

## Examples

**LY001**: Missing `exc_info=True`
```python
# Fail
try:
    connect_db()
except Exception:
    logger.error("Connection failed")  # No stack trace!

# Pass
try:
    connect_db()
except Exception:
    logger.error("Connection failed", exc_info=True)
```

**LY002**: Logging in hot loops
```python
# Fail
for user in users:
    logger.info(f"Processing {user}")  # Logs every iteration

# Pass
for i, user in enumerate(users):
    if i % 100 == 0:
        logger.info(f"Progress: {i}/{len(users)}")  # Conditional logging
```

**LY003**: Inconsistent key-value logging
```python
# Fail
logger.info(f"User {user}")  # Missing key
logger.info("User %s", user)  # Placeholder without key

# Pass
logger.info(f"User user={user}")  # Key-value pair
logger.info("User user=%s", user)  # Key=placeholder format
```

## License

Apache
