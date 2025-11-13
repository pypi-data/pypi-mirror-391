# Redis Session Storage Setup Guide

## Overview

MBASIC Web UI supports two session storage modes:

1. **In-Memory (Default)** - Session state stored in server process memory
   - ✅ No external dependencies
   - ✅ Works out-of-the-box
   - ❌ Sessions don't survive server restart
   - ❌ Can't load balance across multiple processes

2. **Redis-Backed** - Session state stored in Redis
   - ✅ Sessions persist across server restarts
   - ✅ Load balancing across multiple instances
   - ✅ High availability with Redis Sentinel/Cluster
   - ❌ Requires Redis server and Python package

## Quick Start

### Development (In-Memory, Default)

```bash
# No configuration needed
python3 mbasic --ui web
```

### Production (Redis-Backed)

```bash
# 1. Install Redis server (if not already installed)
sudo apt-get update && sudo apt-get install -y redis-server

# 2. Install Python redis package
pip install redis

# 3. Configure environment variables
export NICEGUI_REDIS_URL="redis://localhost:6379/0"
export MBASIC_STORAGE_SECRET="your-secret-key-change-this"

# 4. Start web UI
python3 mbasic --ui web
```

## Detailed Installation

### 1. Redis Server Installation

#### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install -y redis-server

# Enable and start Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Verify Redis is running
redis-cli ping  # Should return "PONG"
```

#### macOS (via Homebrew)

```bash
brew install redis
brew services start redis

# Verify
redis-cli ping
```

#### Docker

```bash
docker run -d --name redis -p 6379:6379 redis:latest

# Verify
docker exec -it redis redis-cli ping
```

### 2. Python Redis Package

```bash
# From requirements.txt
pip install -r requirements.txt

# Or directly
pip install redis>=5.0.0
```

Verify installation:
```bash
python3 -c "import redis; r=redis.Redis(); print('Redis OK:', r.ping())"
```

## Configuration

### Environment Variables

#### NICEGUI_REDIS_URL (Optional)
Redis connection URL. If not set, uses in-memory storage.

**Format**: `redis://[username:password@]host:port/database`

**Examples**:
```bash
# Local Redis (default port, database 0)
export NICEGUI_REDIS_URL="redis://localhost:6379/0"

# Remote Redis with password
export NICEGUI_REDIS_URL="redis://:mypassword@redis.example.com:6379/0"

# Redis with username and password (Redis 6+)
export NICEGUI_REDIS_URL="redis://myuser:mypassword@redis.example.com:6379/0"
```

#### NICEGUI_REDIS_KEY_PREFIX (Optional)
Prefix for all Redis keys. Default: `"nicegui:"`

```bash
export NICEGUI_REDIS_KEY_PREFIX="mbasic:"
```

#### MBASIC_STORAGE_SECRET (Required for production)
Secret key for encrypting session cookies. **Change in production!**

```bash
# Development (auto-generated if not set)
# Uses default: 'dev-default-change-in-production'

# Production (REQUIRED - use a strong random key)
export MBASIC_STORAGE_SECRET="$(openssl rand -hex 32)"
```

### Checking Active Mode

When you start the web UI, it logs which storage mode is active:

**In-Memory Mode**:
```
======================================================================
MBASIC Web UI Starting - Version 1.0.738
======================================================================

In-memory storage (default): Session state per process only
Set NICEGUI_REDIS_URL to enable Redis storage for load balancing

NiceGUI ready to go on http://localhost:8080
```

**Redis Mode**:
```
======================================================================
MBASIC Web UI Starting - Version 1.0.738
======================================================================

Redis storage enabled: redis://localhost:6379/0
Session state will be shared across load-balanced instances

NiceGUI ready to go on http://localhost:8080
```

## Testing

### Test In-Memory Mode

```bash
# Start without Redis
unset NICEGUI_REDIS_URL
python3 mbasic --ui web
```

Open http://localhost:8080 in two browser tabs:
- Tab 1: Enter program `10 PRINT "TAB 1"`
- Tab 2: Enter program `10 PRINT "TAB 2"`

**Expected**: Each tab has its own isolated session (different programs)

### Test Redis Mode

```bash
# Start with Redis
export NICEGUI_REDIS_URL="redis://localhost:6379/0"
python3 mbasic --ui web
```

Open http://localhost:8080 in two browser tabs:
- Tab 1: Enter program `10 PRINT "REDIS TEST"`
- Refresh Tab 1
- Check Tab 2

**Expected**: Program persists across refreshes (Redis is working)

### Test Load Balancing (Multiple Processes)

Terminal 1:
```bash
export NICEGUI_REDIS_URL="redis://localhost:6379/0"
export MBASIC_STORAGE_SECRET="test-secret"
python3 mbasic --ui web --port 8080
```

Terminal 2:
```bash
export NICEGUI_REDIS_URL="redis://localhost:6379/0"
export MBASIC_STORAGE_SECRET="test-secret"
python3 mbasic --ui web --port 8081
```

Test:
1. Open http://localhost:8080
2. Enter program and run it
3. Note your session ID (check browser cookies)
4. Open http://localhost:8081 **in the same browser** (shares cookies)
5. Verify your program and output are there

**Expected**: Session state follows you across both instances

## Load Balancer Configuration

### nginx Example

```nginx
upstream mbasic_web {
    # IP hash ensures same client goes to same server
    # (not needed with Redis, but reduces latency)
    ip_hash;

    server localhost:8080;
    server localhost:8081;
    server localhost:8082;
}

server {
    listen 80;
    server_name mbasic.example.com;

    location / {
        proxy_pass http://mbasic_web;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed in future)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### HAProxy Example

```haproxy
frontend mbasic_frontend
    bind *:80
    default_backend mbasic_backend

backend mbasic_backend
    balance roundrobin
    option httpclose
    option forwardfor
    cookie SERVERID insert indirect nocache

    server mbasic1 localhost:8080 check cookie mbasic1
    server mbasic2 localhost:8081 check cookie mbasic2
    server mbasic3 localhost:8082 check cookie mbasic3
```

## Session State Details

### What Gets Saved

- Program source code (all lines)
- Runtime state (variables, arrays, execution position)
- Output text
- Current file and recent files list
- Execution state (running, paused)
- Editor content
- Find/Replace state
- Configuration settings

### What Gets Recreated

- UI elements (buttons, menus, dialogs)
- Editor widget
- Interpreter instance
- IO handlers
- Timers

### Serialization Frequency

Session state is saved:
- **Every 5 seconds** (automatic)
- **On disconnect** (page unload, browser close)
- **On page navigation**

### Session Persistence

- **In-memory**: Until server restart
- **Redis**: Based on NiceGUI's TTL (default: 24 hours)

## Troubleshooting

### Redis Connection Errors

**Problem**: `redis.exceptions.ConnectionError: Error connecting to Redis`

**Solutions**:
1. Check Redis is running: `redis-cli ping`
2. Check firewall/network access
3. Verify NICEGUI_REDIS_URL is correct
4. Check Redis logs: `sudo journalctl -u redis-server -f`

### Import Error

**Problem**: `ImportError: Redis is not installed`

**Solution**: Install redis package:
```bash
pip install redis>=5.0.0
```

### State Not Persisting

**Problem**: Session state lost on refresh (Redis mode)

**Debug**:
1. Check Redis keys:
   ```bash
   redis-cli KEYS "nicegui:*"
   ```
2. Monitor Redis operations:
   ```bash
   redis-cli MONITOR
   ```
3. Check browser console for errors
4. Verify MBASIC_STORAGE_SECRET is set

### Session Not Shared Across Instances

**Problem**: Different servers show different state

**Solutions**:
1. Verify all instances use same NICEGUI_REDIS_URL
2. Verify all instances use same MBASIC_STORAGE_SECRET
3. Check browser is sending same session cookie to both
4. Verify Redis is accessible from all instances

### Serialization Errors

**Problem**: `Warning: Failed to save session state`

**Check logs**: stderr output shows serialization errors

**Common causes**:
- Open file handles (should be closed automatically)
- Corrupted runtime state
- Pickle version mismatch

**Solution**: Usually resolves on next save attempt. If persistent:
1. Check debug output
2. Clear Redis: `redis-cli FLUSHDB`
3. Restart browser (clear cookies)

## Security Considerations

### Production Checklist

- [ ] Set strong MBASIC_STORAGE_SECRET (32+ random hex characters)
- [ ] Configure Redis password (`requirepass` in redis.conf)
- [ ] Enable Redis AUTH
- [ ] Use TLS for Redis connections (rediss:// URL)
- [ ] Restrict Redis network access (firewall/security groups)
- [ ] Regular Redis backups (if session persistence is critical)
- [ ] Monitor Redis memory usage
- [ ] Set Redis maxmemory policy

### Redis Configuration

Edit `/etc/redis/redis.conf`:

```conf
# Require password
requirepass your-strong-redis-password

# Bind to specific interface (not all)
bind 127.0.0.1

# Enable TLS (optional)
tls-port 6380
tls-cert-file /path/to/redis.crt
tls-key-file /path/to/redis.key
tls-ca-cert-file /path/to/ca.crt

# Memory management
maxmemory 256mb
maxmemory-policy allkeys-lru
```

Then update NICEGUI_REDIS_URL:
```bash
export NICEGUI_REDIS_URL="redis://:your-strong-redis-password@localhost:6379/0"
# Or with TLS:
export NICEGUI_REDIS_URL="rediss://:your-strong-redis-password@localhost:6380/0"
```

## Performance Optimization

### Redis Persistence

For session storage, you can disable Redis persistence to improve performance:

```conf
# redis.conf
save ""
appendonly no
```

**Trade-off**: Sessions lost if Redis crashes (acceptable for session data)

### Connection Pooling

NiceGUI handles connection pooling automatically. No configuration needed.

### Memory Usage

Monitor Redis memory:
```bash
redis-cli INFO memory
```

Estimate: ~10-50 KB per active session (depends on program size and output)

## High Availability

### Redis Sentinel

For production deployments, use Redis Sentinel for automatic failover:

```bash
# Install Sentinel
sudo apt-get install redis-sentinel

# Configure sentinel.conf
sentinel monitor mbasic-redis 127.0.0.1 6379 2
sentinel down-after-milliseconds mbasic-redis 5000
sentinel failover-timeout mbasic-redis 10000
```

Update URL to use Sentinel:
```bash
export NICEGUI_REDIS_URL="redis://sentinel1:26379,sentinel2:26379,sentinel3:26379/mymaster"
```

### Redis Cluster

For very large deployments, use Redis Cluster for sharding.

## References

- [NiceGUI Storage Documentation](https://nicegui.io/documentation/storage)
- [Redis Documentation](https://redis.io/documentation)
- [Redis Python Client](https://redis-py.readthedocs.io/)
- Session Storage Audit: `docs/dev/SESSION_STORAGE_AUDIT.md`
- Storage Abstraction Design: `docs/dev/STORAGE_ABSTRACTION_DESIGN.md`
