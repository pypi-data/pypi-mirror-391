<div class="hero" markdown>
  ![pfly](assets/logo-horizontal.svg)
</div>

# Shift-Left Your Log Quality

**pfly** is a Python logging linter. We deserve better logs.

## The Problem

There are numerous python code formatting tools there. We strongly believe, logging requires its specialized tooling. Many devs like me spend considerable time looking at logs and not as much attention and care is given to logs at the time of writing code. This project is setting up some baseline expectation on your logs - to not only reduce cognitive load when reading logs for your next RCA but provide delight in viewing logs.

- **Missing stack traces**: Exception logs without `exc_info=True`? 
- **Performance degradation**: Unconditional logging in hot loops. Yes, logging 10,000 times per second is technically possible.
- **Inconsistent kv logging**: Different kv delimeters in logs across services means you automatically context switch from Root Cause Analysis to Regex Crafting Annoyance
- **No emojis or special chars in logs**: Machine-parsable logs are non-negotiable. Stop trying to be cute in production logs.

## The Solution

**pfly**

```bash
# Install the salvation device
uv pip install pfly

# Run it like your life depends on it
pfly path/to/code

# Make it mandatory in CI (it should be)
pfly . --config=pfly.yml
```

## The Philosophy: Catch It Early (Or Else)

**pfly's approach**

- **Shift Left**: Static analysis only. Run it in your github actions, CI. 
- **Team consistency**: Setup baseline policies for minimum expectation for service stack.

## Current Policies

| Code | Policy | What Happens If You Ignore It |
|------|--------|------|
| **LY001** | Exception exc_info | Ensure your logs in exception blocks have exc_info |
| **LY002** | Log Loop | Ensure logging in loops is with conditional checks |
| **LY003** | Orphan Variables | Remove guesswork of what is in the logs |

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
