# In-Process Task App: Action Items & Improvements

## ✅ Current Status: MVP Complete & Working

The `InProcessTaskApp` utility is **fully functional** and successfully tested. This document outlines specific action items for improvements.

---

## 🔴 CRITICAL: Missing Tests

### Action Item 1: Create Unit Tests

**File:** `tests/unit/task/test_in_process.py` (NEW)

**Priority:** 🔴 CRITICAL

**Tests Needed:**
```python
@pytest.mark.asyncio
class TestInProcessTaskApp:
    """Unit tests for InProcessTaskApp."""
    
    def test_init_validates_exactly_one_input(self):
        """Should raise ValueError if multiple or no inputs."""
        # Test no inputs
        # Test multiple inputs
    
    async def test_init_with_app(self):
        """Should accept FastAPI app directly."""
        # Mock FastAPI app
        # Verify tunnel opens
    
    async def test_init_with_config(self):
        """Should accept TaskAppConfig."""
        # Create test config
        # Verify works
    
    async def test_init_with_config_factory(self):
        """Should accept config factory function."""
        # Test factory function
    
    async def test_init_with_task_app_path(self):
        """Should load from file path."""
        # Use real heartdisease_task_app.py
        # Verify works
    
    @patch("synth_ai.cloudflare.open_quick_tunnel")
    @patch("synth_ai.cloudflare._wait_for_health_check")
    @patch("synth_ai.cloudflare._start_uvicorn_background")
    async def test_cleanup_on_exception(self, ...):
        """Should clean up tunnel even if exception occurs."""
        # Raise exception in context
        # Verify tunnel stopped
    
    async def test_health_check_timeout(self):
        """Should raise RuntimeError if health check times out."""
        # Mock server that never responds
        # Verify timeout error
    
    async def test_port_conflict_handling(self):
        """Should handle port already in use."""
        # Start server on port
        # Try to start another
        # Verify error handling
```

**Estimated Time:** 2-3 hours

---

### Action Item 2: Create Integration Tests

**File:** `tests/integration/task/test_in_process.py` (NEW)

**Priority:** 🔴 CRITICAL

**Tests Needed:**
```python
@pytest.mark.integration
@pytest.mark.asyncio
class TestInProcessTaskAppIntegration:
    """Integration tests requiring cloudflared."""
    
    @pytest.mark.skipif(not shutil.which("cloudflared"), reason="cloudflared not installed")
    async def test_full_gepa_workflow(self):
        """Test complete GEPA workflow."""
        # Use real task app
        # Verify tunnel opens
        # Verify health endpoint works
        # Verify task_info endpoint works
    
    async def test_multiple_instances_different_ports(self):
        """Test running multiple instances."""
        # Start two instances
        # Verify both work
        # Verify different ports/URLs
```

**Estimated Time:** 1-2 hours

---

## 🟡 IMPORTANT: Error Handling Improvements

### Action Item 3: Port Conflict Handling

**File:** `synth_ai/task/in_process.py`

**Priority:** 🟡 IMPORTANT

**Current Issue:** Port conflicts cause unclear uvicorn errors.

**Improvement:**
```python
import socket

def _find_available_port(start_port: int, max_attempts: int = 10) -> int:
    """Find an available port starting from start_port."""
    for i in range(max_attempts):
        port = start_port + i
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("127.0.0.1", port))
            sock.close()
            return port
        except OSError:
            continue
    raise RuntimeError(f"No available port in range {start_port}-{start_port + max_attempts}")

# In __aenter__:
try:
    _start_uvicorn_background(self._app, self.host, self.port, daemon=False)
except OSError as e:
    if "address already in use" in str(e).lower():
        new_port = _find_available_port(self.port)
        import warnings
        warnings.warn(
            f"Port {self.port} in use, using {new_port} instead. "
            f"To free port {self.port}, run: lsof -ti:{self.port} | xargs kill -9",
            UserWarning
        )
        self.port = new_port
        _start_uvicorn_background(self._app, self.host, self.port, daemon=False)
    else:
        raise
```

**Estimated Time:** 30 minutes

---

### Action Item 4: Input Validation

**File:** `synth_ai/task/in_process.py`

**Priority:** 🟡 IMPORTANT

**Add to `__init__`:**
```python
def __init__(self, ...):
    # Validate port range
    if not (1024 <= port <= 65535):
        raise ValueError(f"Port must be in range 1024-65535, got {port}")
    
    # Validate host
    if host not in ("127.0.0.1", "localhost", "0.0.0.0"):
        raise ValueError(f"Host must be 127.0.0.1, localhost, or 0.0.0.0, got {host}")
    
    # Validate tunnel_mode
    if tunnel_mode not in ("quick",):
        raise ValueError(f"tunnel_mode must be 'quick' (managed not yet supported), got {tunnel_mode}")
    
    # Validate task_app_path exists (if provided)
    if task_app_path:
        path = Path(task_app_path)
        if not path.exists():
            raise FileNotFoundError(f"Task app file not found: {task_app_path}")
        if not path.suffix == ".py":
            raise ValueError(f"Task app must be a .py file, got {path.suffix}")
    
    # ... rest of init ...
```

**Estimated Time:** 15 minutes

---

## 🟢 REFACTOR: Better Abstractions

### Action Item 5: Make Private Functions Public

**File:** `synth_ai/cloudflare.py`

**Priority:** 🟢 REFACTOR

**Change:**
```python
# Rename private functions to public
def start_uvicorn_background(...):  # Was: _start_uvicorn_background
    ...

async def wait_for_health_check(...):  # Was: _wait_for_health_check
    ...
```

**Update imports in:**
- `synth_ai/task/in_process.py`
- `tests/integration/tunnel/test_tunnel_deploy.py`

**Rationale:** These functions are used by multiple modules and should be part of the public API.

**Estimated Time:** 30 minutes

---

### Action Item 6: Extract Server Lifecycle Abstraction (Optional)

**File:** `synth_ai/task/server_lifecycle.py` (NEW)

**Priority:** 🟢 OPTIONAL (Nice to have)

**Create abstraction:**
```python
class TaskAppServer:
    """Manages task app server lifecycle."""
    
    def __init__(self, app: ASGIApplication, host: str, port: int):
        ...
    
    def start(self, daemon: bool = False) -> None:
        """Start server in background thread."""
        ...
    
    async def wait_for_health(self, api_key: str, timeout: float = 30.0) -> None:
        """Wait for server to be healthy."""
        ...


class CloudflareTunnel:
    """Manages Cloudflare tunnel lifecycle."""
    
    def __init__(self, port: int, mode: str = "quick"):
        ...
    
    async def open(self) -> str:
        """Open tunnel and return URL."""
        ...
    
    def close(self) -> None:
        """Close tunnel."""
        ...
```

**Benefits:** Better separation of concerns, easier testing, reusable components.

**Estimated Time:** 2-3 hours

---

## 🟢 NICE TO HAVE: Additional Features

### Action Item 7: Signal Handling

**File:** `synth_ai/task/in_process.py`

**Priority:** 🟢 NICE TO HAVE

**Add signal handlers for graceful shutdown:**
```python
import signal
import atexit

class InProcessTaskApp:
    def __init__(self, ...):
        ...
        self._cleanup_registered = False
    
    async def __aenter__(self) -> InProcessTaskApp:
        # ... start server and tunnel ...
        
        # Register cleanup handlers
        if not self._cleanup_registered:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            atexit.register(self._cleanup)
            self._cleanup_registered = True
        
        return self
    
    def _signal_handler(self, signum, frame):
        """Handle SIGINT/SIGTERM."""
        # Cleanup and exit gracefully
```

**Estimated Time:** 1 hour

---

### Action Item 8: Observability Hooks

**File:** `synth_ai/task/in_process.py`

**Priority:** 🟢 NICE TO HAVE

**Add callbacks:**
```python
def __init__(
    self,
    ...,
    logger: Optional[logging.Logger] = None,
    on_tunnel_ready: Optional[Callable[[str], None]] = None,
    on_server_started: Optional[Callable[[int], None]] = None,
):
    self.logger = logger or logging.getLogger(__name__)
    self.on_tunnel_ready = on_tunnel_ready
    self.on_server_started = on_server_started
```

**Estimated Time:** 30 minutes

---

### Action Item 9: Managed Tunnel Support

**File:** `synth_ai/task/in_process.py`

**Priority:** 🟢 FUTURE

**Add support for managed tunnels:**
```python
def __init__(
    self,
    ...,
    tunnel_mode: str = "quick",
    tunnel_token: Optional[str] = None,  # NEW
):
    ...

async def __aenter__(self) -> InProcessTaskApp:
    ...
    if self.tunnel_mode == "quick":
        self.url, self._tunnel_proc = open_quick_tunnel(self.port, wait_s=15.0)
    elif self.tunnel_mode == "managed":
        if not self.tunnel_token:
            raise ValueError("tunnel_token required for managed tunnels")
        self._tunnel_proc = open_managed_tunnel(self.tunnel_token)
        self.url = await self._get_managed_tunnel_url()
```

**Estimated Time:** 2-3 hours

---

## 📋 Summary Checklist

### Critical (Do First)
- [ ] **Action Item 1:** Create unit tests (`tests/unit/task/test_in_process.py`)
- [ ] **Action Item 2:** Create integration tests (`tests/integration/task/test_in_process.py`)

### Important (Do Soon)
- [ ] **Action Item 3:** Port conflict handling with auto-find
- [ ] **Action Item 4:** Input validation (port, host, tunnel_mode, file existence)

### Refactor (Do When Time Permits)
- [ ] **Action Item 5:** Make private functions public (`_start_uvicorn_background` → `start_uvicorn_background`)
- [ ] **Action Item 6:** Extract server lifecycle abstraction (optional)

### Nice to Have (Future)
- [ ] **Action Item 7:** Signal handling (SIGINT/SIGTERM)
- [ ] **Action Item 8:** Observability hooks (logging, callbacks)
- [ ] **Action Item 9:** Managed tunnel support

---

## Web Endpoint Readiness Assessment

### ✅ Ready For:
- **Local development** ✅
- **Demos** ✅
- **CI/CD pipelines** ✅
- **Testing** ✅
- **Blog post examples** ✅

### ❌ NOT Ready For:
- **Production web endpoints** ❌
  - Ephemeral tunnels (URLs change)
  - No authentication (quick tunnels)
  - No persistence
  - Single process (no scaling)
  - No monitoring

### Recommendation:
- **Keep `InProcessTaskApp` for local/dev use** ✅
- **For production:** Use Modal deployment or managed tunnels via backend API ✅

---

## Files Summary

### Core Files
1. `synth_ai/task/in_process.py` - Main implementation (189 lines)
2. `synth_ai/task/__init__.py` - Exports InProcessTaskApp

### Demo Files
3. `examples/gepa/run_synth_gepa_in_process.py` - Synth GEPA demo (220 lines)
4. `examples/gepa/run_in_process_gepa.py` - Combined demo (222 lines)

### Documentation
5. `examples/gepa/IN_PROCESS_GEPA_DEMO.md` - Comprehensive guide (412 lines)
6. `examples/gepa/README.md` - Quick start (73 lines)
7. `examples/gepa/IN_PROCESS_REVIEW.md` - This review document
8. `examples/gepa/IN_PROCESS_ACTION_ITEMS.md` - Action items (this file)

### Planning Documents
9. `examples/blog_posts/gepa/in-process-implementation-plan.txt` - Planning (580 lines)
10. `examples/blog_posts/gepa/in-process-task-app.txt` - Feasibility (639 lines)

### Related Infrastructure
11. `synth_ai/cloudflare.py` - Tunnel utilities
12. `synth_ai/utils/apps.py` - App loading utilities
13. `synth_ai/task/server.py` - Task app server creation

### Tests (Existing)
14. `tests/integration/tunnel/test_tunnel_deploy.py` - Tunnel deployment tests
15. `tests/unit/tunnel/test_tunnel.py` - Tunnel unit tests

### Tests (Needed)
16. `tests/unit/task/test_in_process.py` - **MISSING** ⚠️
17. `tests/integration/task/test_in_process.py` - **MISSING** ⚠️

---

## Estimated Total Work

- **Critical:** 3-5 hours (tests)
- **Important:** 45 minutes (error handling)
- **Refactor:** 30 minutes - 3 hours (abstractions)
- **Nice to Have:** 2-4 hours (features)

**Total:** ~7-13 hours for all improvements

**Minimum Viable:** 3-5 hours (just tests) to make it production-ready for local use.

---

## Conclusion

**Status:** ✅ **MVP Complete & Working**

The `InProcessTaskApp` utility is fully functional and ready for use in demos and local development. The main gap is **test coverage**. Once tests are added, it will be production-ready for local use cases.

**Next Steps:**
1. Add unit tests (Action Item 1)
2. Add integration tests (Action Item 2)
3. Improve error handling (Action Item 3, 4)
4. Consider refactoring (Action Item 5, 6) when time permits

