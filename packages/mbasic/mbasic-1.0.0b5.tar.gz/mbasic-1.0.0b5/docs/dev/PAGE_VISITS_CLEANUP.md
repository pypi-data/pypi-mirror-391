# Dead Code Cleanup: page_visits and feature_usage Tables

## Summary
Removed dead code related to `page_visits` and `feature_usage` tables that were never being used.

## Problems

### 1. page_visits Table
The root URL (`/`) immediately redirects to `/ide`, so the landing page HTML that calls `/api/track-visit` was never served. This resulted in:
- `/api/track-visit` endpoint never being called
- `page_visits` MySQL table always empty
- Dead code in the codebase

### 2. feature_usage Table
The `track_feature_usage()` method exists in `usage_tracker.py` but is **never called anywhere** in the codebase. This resulted in:
- `feature_usage` MySQL table always empty
- Dead code in usage_tracker.py

## What Actually Gets Used
- ✅ **`ide_sessions` table** - Tracks IDE sessions with real client IPs (X-Forwarded-For fix applied)
- ✅ **`program_executions` table** - Tracks program runs (called from nicegui_backend.py)
- ❌ **`page_visits` table** - Never populated (dead code)
- ❌ **`feature_usage` table** - Never populated (dead code)

## Changes Made

### Removed from Code
1. `src/ui/web/nicegui_backend.py` - Deleted the `/api/track-visit` endpoint

### Removed from SQL Schemas
1. `deployment/sql/usage_tracking_schema.sql` - Removed `page_visits` and `feature_usage` table definitions
2. `deployment/sql/recreate_usage_tables.sql` - Removed `page_visits` and `feature_usage` table definitions
3. `deployment/sql/setup_usage_tracking.sh` - Removed from output listing

### Files Not Touched (Methods Remain but Unused)
- `src/usage_tracker.py` - `track_page_visit()` and `track_feature_usage()` methods remain (unused but harmless)
- `deployment/landing-page/index.html` - Landing page HTML remains (not served)

## Database Cleanup (Optional)

If you want to remove the unused tables from MySQL:

```sql
-- Check if tables have any data (should be empty)
SELECT COUNT(*) FROM page_visits;
SELECT COUNT(*) FROM feature_usage;

-- Drop the tables (drop feature_usage first due to foreign key constraint)
DROP TABLE IF EXISTS feature_usage;
DROP TABLE IF EXISTS page_visits;
```

**Note**: This is optional. The empty tables don't hurt anything, but removing them cleans up the schema.

## What Remains Active

The following usage tracking is still active and working:
- ✅ `ide_sessions` - Tracks IDE session starts/ends with real client IPs (X-Forwarded-For fix applied)
- ✅ `program_executions` - Tracks program runs (called from `_track_program_execution()`)
- ✅ `daily_usage_summary` - Aggregated daily statistics

Both active tables use the fixed IP extraction that gets real client IPs from X-Forwarded-For header.

## Related Documents
- `docs/dev/IP_LOGGING_FIX.md` - IP address logging fix for Kubernetes
- `docs/dev/USAGE_TRACKING_INTEGRATION.md` - Original usage tracking setup (now outdated regarding page_visits)
- `DEPLOY_NOTE_IP_LOGGING_FIX.md` - Deployment note for IP fix

## Date
2025-11-13
