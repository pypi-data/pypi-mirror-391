<div align="center">
  <img src="logo-horizontal.svg" alt="plly - Python LOggling Linter" width="400">
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
uv pip install plly
```

## Usage

```bash
plly path/to/code

plly path/to/code --config=plly.yml
```

## Policies

| Code | Policy | Description |
|------|--------|-------------|
| **LY001** | `exception_exc_info` | Enforces `exc_info=True` in exception handlers to capture stack traces |
| **LY002** | `log_loop` | Prevents unconditional logging in hot loops (allows conditional logging) |

## Configuration

Create a `plly.yml`:

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


## License

Apache
