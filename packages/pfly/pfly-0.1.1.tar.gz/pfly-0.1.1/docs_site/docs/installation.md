# Installation

## Using uv (Recommended)

The fast, modern way to install things. We're fans.

```bash
uv pip install pfly
```

## Verify Installation

Let's make sure the universe hasn't conspired against you:

```bash
pfly --help
```

You should see:

```
Usage: pfly [OPTIONS] PATH

  Log Linter for Python

Options:
  --config PATH  Path to configuration file (default: pfly.yml)
  --help         Show this message and exit
```

If you don't? Check your installation. Google it. Call a friend. We believe in you.

## Quick Start

Time to scan your disaster of a codebase and find all those logging mistakes:

```bash
# Scan current directory (brace yourself)
pfly .

# Scan specific directory (surgical precision)
pfly src/

# Use custom config (because you're special)
pfly . --config=custom-pfly.yml
```

## Configuration

Create a `pfly.yml` in your project root. This is where you declare war on bad logging:

```yaml
logger_names: [logger, logging, log]

exception_exc_info:
  levels: [error]
  severity: fail

log_loop:
  levels: [info, debug]
  severity: fail
```

### Configuration Options

**`logger_names`**: What you named your loggers. We support many sins.

**`severity`**: How angry we should be about your violations

- `fail`: Exit with error code (blocks CI, recommended to spare the 3 AM regret)
- `warn`: Print a sad warning but let you pass (not recommended, but we won't judge)
- `info`: Informational only (for the optimistic amongst us)

**`levels`**: Which log levels get our attention (e.g., `[error, warning, info, debug]`)

## CI Integration

Make pfly mandatory.

### GitHub Actions

Catch logging disasters before they merge:

```yaml
name: Lint Logs

on: [push, pull_request]

jobs:
  pfly:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv pip install pfly
      - run: pfly . --config=pfly.yml  # Fail the build. Block the merge. Save the future.
```
