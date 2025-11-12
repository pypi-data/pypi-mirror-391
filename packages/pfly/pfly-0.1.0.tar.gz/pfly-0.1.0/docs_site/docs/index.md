<div class="hero" markdown>
  ![plly](assets/logo-horizontal.svg)
</div>

# Shift-Left Your Log Quality

**plly** is a Python logging linter that catches logging anti-patterns.

## The Problem

Setting up some baseline expectation on your logs - to reduce cognitive load when reading logs for root causes analysis (RCA).

- **Missing stack traces**: Exception logs without `exc_info=True`? Congratulations, you've written the equivalent of "something went wrong" in Comic Sans.
- **Performance degradation**: Unconditional logging in hot loops. Yes, logging 10,000 times per second is technically possible. Just because you can, does not mean you should.
- **Inconsistent kv logging**: Different kv delimeters in logs across services means you automatically context switch from Root Cause Analysis to Regex Crafting Annoyance
- **No emojis or special chars in logs**: Machine-parsable logs are non-negotiable. Stop trying to be cute in production logs.

## The Solution

**plly** catches these annoyances before they happen—in your editor, during CI, before production melts down.

```bash
# Install the salvation device
uv pip install plly

# Run it like your life depends on it
plly path/to/code

# Make it mandatory in CI (it should be)
plly . --config=plly.yml
```

## The Philosophy: Catch It Early (Or Else)

**plly's approach**

- **Shift Left**: Static analysis only. Run it in your github actions, CI. 
- **Team consistency**: Setup baseline policies for minimum expectation for service stack.

## Current Policies

| Code | Policy | What Happens If You Ignore It |
|------|--------|------|
| **LY001** | Exception exc_info | Ensure your logs in exception blocks have exc_info |
| **LY002** | Log Loop | Ensure logging in loops is with conditional checks |

[See all policies](policies/index.md)

## Quick Example

```python
# LY001 violation
try:
    connect_db()
except Exception:
    logger.error("Connection failed") 

try:
    connect_db()
except Exception:
    logger.error("Connection failed", exc_info=True)
```
