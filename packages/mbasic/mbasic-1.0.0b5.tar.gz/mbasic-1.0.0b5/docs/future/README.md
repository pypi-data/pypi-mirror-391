# Future / Someday Projects

This directory contains ideas and plans for features that are deferred for future consideration.

## What Belongs Here

- **Nice-to-have features** that aren't critical for core functionality
- **Enhancement ideas** that would improve UX but aren't blocking
- **Optimization projects** that could improve performance but aren't urgent
- **Experimental features** that need more research or design work

## What Doesn't Belong Here

- **Active work** should be in `docs/dev/` with `*_TODO.md` files
- **Completed work** should be in `docs/history/` with `*_DONE.md` files
- **Design documents** should be in `docs/design/`
- **User documentation** should be in `docs/user/`

## Moving Projects

### To Active Development
When a future project becomes a priority:
```bash
git mv docs/future/FEATURE_TODO.md docs/dev/
```

### To History
If a future project is completed or no longer relevant:
```bash
git mv docs/future/FEATURE_TODO.md docs/history/FEATURE_DONE.md
# or for cancelled projects:
git mv docs/future/FEATURE_TODO.md docs/history/FEATURE_CANCELLED.md
```

## Current Future Projects

See files in this directory for specific project ideas and plans.
