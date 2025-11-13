# Pluggable Storage Backends for Web UI

## Goal
Make web UI session storage configurable to support both in-memory (default) and Redis (for load-balanced deployments).

## Motivation
- Current implementation stores session state in `app.storage.client` (in-memory, server-side)
- In-memory storage doesn't work across multiple server instances behind a load balancer
- Each HTTP request from the same client browser can go to a different server process
- NiceGUI has built-in Redis support (since v2.10.0) that can be leveraged
- Default behavior should work without Redis (for developers doing `git clone`)

## Current Architecture
- `src/ui/web/nicegui_backend.py:3263` - Stores entire `NiceGUIBackend` instance in `app.storage.client['backend']`
- Each backend instance contains:
  - `Runtime` (variables, arrays, execution stack, program counter)
  - `Interpreter` instance
  - `SandboxedFileSystemProvider` (per-session filesystem)
  - Editor content and output buffer
  - File I/O state

## Implementation Plan

### Phase 1: Analysis & Design
1. **Audit current session storage requirements**
   - Identify all state stored in `app.storage.client['backend']`
   - Determine serialization requirements for Redis
   - Identify non-serializable objects (file handles, async futures, etc.)

2. **Design storage abstraction layer**
   - Define interface for pluggable backends
   - Plan state extraction into JSON-serializable format
   - Design session lifecycle management

### Phase 2: Implementation
3. **Implement in-memory storage backend**
   - Keep current behavior as default (no changes needed)
   - Ensure it's explicitly defined as a backend option

4. **Refactor NiceGUIBackend for serialization**
   - Extract session state into serializable dict structure
   - Handle non-serializable objects (recreate on deserialization)
   - Maintain backward compatibility

5. **Implement Redis storage backend**
   - Use NiceGUI's built-in Redis support via `NICEGUI_REDIS_URL` env var
   - Set `storage_secret` in `ui.run()` for secure session cookies
   - Test serialization/deserialization of session state

6. **Add configuration system**
   - Auto-detect Redis availability via environment variable
   - Default to in-memory if Redis not configured
   - Log which backend is active on startup

7. **Update mbasic web startup**
   - Modify launcher to detect and configure storage
   - Pass `storage_secret` to `ui.run()` when Redis is enabled

### Phase 3: Testing & Documentation
8. **Test in-memory mode (default)**
   - Multiple browser tabs (same session)
   - Verify no Redis dependency required

9. **Test Redis mode**
   - Multiple browser tabs
   - Multiple sessions (different browsers)
   - Session persistence across Redis restarts

10. **Test load balancing simulation**
    - Start multiple mbasic web processes on different ports
    - Use nginx/haproxy to load balance
    - Verify session state follows user across processes

11. **Documentation**
    - Create `docs/dev/REDIS_SESSION_STORAGE.md` with setup instructions
    - Document Redis installation (server and Python package)
    - Provide example configurations for dev vs production

12. **Update dependencies**
    - Add to `requirements.txt`: `redis>=5.0.0  # optional, for load-balanced deployments`

## Redis Configuration

### Server Installation (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### Python Package Installation
```bash
pip install redis
```

### Environment Variables
```bash
# Enable Redis storage (if not set, uses in-memory default)
export NICEGUI_REDIS_URL="redis://localhost:6379/0"

# Optional: Custom key prefix
export NICEGUI_REDIS_KEY_PREFIX="mbasic:"

# Required for session security
export MBASIC_STORAGE_SECRET="your-secret-key-here"
```

### Code Changes Needed
```python
# In ui.run() call:
ui.run(
    title='MBASIC 5.21 - Web IDE',
    port=port,
    storage_secret=os.environ.get('MBASIC_STORAGE_SECRET', 'dev-secret-change-in-prod'),
    reload=False,
    show=True
)
```

## Serialization Challenges
Objects that need special handling for Redis:
- **Runtime.files** - File handles (file objects) - Must close and reopen
- **input_future** - asyncio.Future objects - Cannot serialize, recreate on load
- **exec_timer / auto_save_timer** - Timer objects - Recreate on load
- **sandboxed_fs** - SandboxedFileSystemProvider - Recreate with same session_id
- **interpreter** - Recreate with restored runtime state

## Benefits
- **Load balancing**: Deploy multiple instances behind HAProxy/nginx
- **High availability**: Redis replication for failover
- **Session persistence**: Sessions survive server restarts (if Redis persists)
- **Backward compatibility**: Existing deployments work without Redis

## Risks & Considerations
- Serialization overhead (latency per request)
- Redis as a single point of failure (mitigated by Redis HA/Sentinel)
- Larger session data size in Redis vs memory
- Need to handle Redis connection failures gracefully

## References
- NiceGUI Redis Storage: https://nicegui.io/documentation/storage
- NiceGUI Redis Example: https://github.com/zauberzeug/nicegui/blob/main/examples/redis_storage/main.py
- Redis Storage PR: https://github.com/zauberzeug/nicegui/pull/4074
