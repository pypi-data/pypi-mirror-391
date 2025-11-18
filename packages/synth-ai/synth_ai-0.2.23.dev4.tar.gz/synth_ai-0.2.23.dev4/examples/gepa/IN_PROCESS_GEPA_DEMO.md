# In-Process GEPA Demo: Zero-Configuration Prompt Optimization

This guide demonstrates running GEPA (Genetic Evolution for Prompt Optimization) with **in-process task apps** - a streamlined approach that eliminates manual process management and makes prompt optimization accessible with a single Python script.

## What is In-Process GEPA?

Traditionally, running GEPA optimization required:
1. Starting a task app server in one terminal
2. Opening a Cloudflare tunnel manually
3. Running the GEPA job in another terminal
4. Remembering to clean up processes

**In-process GEPA** simplifies this to a single Python script that:
- ✅ Starts the task app automatically in a background thread
- ✅ Opens a Cloudflare tunnel automatically
- ✅ Runs the GEPA optimization
- ✅ Cleans up everything automatically on exit

No separate terminals, no manual process management, no cleanup headaches!

---

## Quick Start

### Prerequisites

```bash
# 1. Install dependencies
cd /Users/joshpurtell/Documents/GitHub/synth-ai
uv pip install -e .

# 2. Set environment variables (or use .env file)
export GROQ_API_KEY="your_groq_key"
export SYNTH_API_KEY="test"  # or your backend API key
export ENVIRONMENT_API_KEY="test"  # or generate a secure token
```

### Run the Demo

```bash
cd examples/gepa
source ../../../.env
uv run python run_in_process_gepa.py
```

That's it! The script will:
1. Start the Heart Disease task app in-process
2. Open a Cloudflare tunnel automatically
3. Run GEPA optimization
4. Display results
5. Clean up automatically

---

## How It Works

### Architecture

```
┌────────────────────────────────────────────────────┐
│  Single Python Script (run_in_process_gepa.py)   │
│                                                    │
│  ┌──────────────────────────────────┐            │
│  │  Task App (Background Thread)    │            │
│  │  - FastAPI server               │            │
│  │  - Uvicorn on port 8114          │            │
│  └──────────────────────────────────┘            │
│                │                                  │
│                ▼                                  │
│  ┌──────────────────────────────────┐            │
│  │  Cloudflare Tunnel (Subprocess)  │            │
│  │  - cloudflared process           │            │
│  │  - Public URL: xxx.trycloudflare│            │
│  └──────────────────────────────────┘            │
│                                                    │
│  ┌──────────────────────────────────┐            │
│  │  GEPA Job Submission              │            │
│  │  - PromptLearningJob              │            │
│  │  - Polls until complete           │            │
│  └──────────────────────────────────┘            │
└────────────────────────────────────────────────────┘
```

### The `InProcessTaskApp` Class

The magic happens in `synth_ai.task.in_process.InProcessTaskApp`, a context manager that:

```python
from synth_ai.task.in_process import InProcessTaskApp

async with InProcessTaskApp(
    task_app_path="path/to/task_app.py",
    port=8114,
) as task_app:
    # task_app.url contains the Cloudflare tunnel URL
    # Use it for GEPA jobs
    job = PromptLearningJob.from_config(
        config_path="config.toml",
        task_app_url=task_app.url,  # ← Automatically injected
    )
    results = await job.poll_until_complete()
# Everything cleaned up automatically here!
```

**Key Features:**
- **Multiple input methods**: Accepts FastAPI app, TaskAppConfig, config factory, or file path
- **Automatic health checks**: Waits for server to be ready before opening tunnel
- **Cloudflare tunnel integration**: Opens ephemeral tunnels automatically
- **Resource cleanup**: Stops tunnel and server on exit (even on exceptions)

---

## Example: Heart Disease Classification

The demo script (`run_in_process_gepa.py`) optimizes prompts for a medical classification task:

### Task Description

**Heart Disease Classification**: Given patient features (age, cholesterol, blood pressure, etc.), predict whether the patient has heart disease (binary classification: 0 = no disease, 1 = disease).

### Configuration

The GEPA configuration (`configs/heartdisease_gepa_local.toml`) specifies:

```toml
[prompt_learning]
algorithm = "gepa"
task_app_url = "http://127.0.0.1:8114"  # Overridden by tunnel URL

[prompt_learning.gepa]
initial_population_size = 3
num_generations = 3
rollout_budget = 300

[prompt_learning.gepa.evaluation]
train_seeds = [0, 1, 2, ..., 29]      # 30 training examples
val_seeds = [30, 31, 32, ..., 79]     # 50 validation examples
```

### Expected Results

GEPA typically improves accuracy from baseline (~70-75%) to optimized (~80-85%) over 3 generations with 300 rollouts.

**Example output:**
```
✅ Task app running at: https://xyz.trycloudflare.com
✅ Cloudflare tunnel active

Running GEPA Optimization
=========================

Submitting job to https://xyz.trycloudflare.com...
✅ Job submitted: pl_abc123

[10:30:15]   45.2s  Status: running
[10:30:20]   50.1s  Status: running
...
[10:35:30]  315.8s  Status: completed

✅ GEPA optimization complete in 315.8s

Results
=======
Best score: 82.50%
Total candidates: 27
```

---

## Advanced Usage

### Using Config Factory

Instead of a file path, you can pass a config factory function:

```python
from heartdisease_task_app import build_config
from synth_ai.task.in_process import InProcessTaskApp

async with InProcessTaskApp(
    config_factory=build_config,
    port=8114,
) as task_app:
    # Use task_app.url
    ...
```

### Custom Port and Host

```python
async with InProcessTaskApp(
    task_app_path="task_app.py",
    port=9000,
    host="0.0.0.0",  # Bind to all interfaces
) as task_app:
    ...
```

### Health Check Timeout

```python
async with InProcessTaskApp(
    task_app_path="task_app.py",
    health_check_timeout=60.0,  # Wait up to 60 seconds
) as task_app:
    ...
```

---

## Comparison: Traditional vs In-Process

| Aspect | Traditional | In-Process |
|--------|------------|------------|
| **Terminals** | 2 terminals needed | 1 script |
| **Process Management** | Manual (start/stop) | Automatic |
| **Tunnel Setup** | Manual cloudflared | Automatic |
| **Cleanup** | Manual (Ctrl+C, kill) | Automatic |
| **Port Conflicts** | Manual checking | Automatic handling |
| **Reproducibility** | Hard (many steps) | Easy (single script) |
| **CI/CD Friendly** | ❌ | ✅ |
| **Best For** | Production deployments | Local dev, demos, experiments |

---

## Benefits

### 1. **Simplified Workflow**

**Before:**
```bash
# Terminal 1
python heartdisease_task_app.py --port 8114

# Terminal 2
cloudflared tunnel --url http://127.0.0.1:8114
# Copy URL, update config...

# Terminal 3
python run_gepa.py
# Remember to stop everything!
```

**After:**
```bash
# Single terminal
python run_in_process_gepa.py
# Done!
```

### 2. **Reproducible Experiments**

The entire workflow is captured in a single Python script, making it easy to:
- Version control the exact setup
- Share with teammates
- Run in CI/CD pipelines
- Reproduce results exactly

### 3. **Automatic Resource Management**

No more:
- ❌ Forgetting to stop task apps
- ❌ Leaving tunnels running
- ❌ Port conflicts from stale processes
- ❌ Manual cleanup after crashes

Everything is handled automatically via Python context managers.

### 4. **Better Developer Experience**

- **Faster iteration**: No context switching between terminals
- **Clearer errors**: All output in one place
- **Easier debugging**: Single process to inspect
- **Less cognitive load**: Focus on optimization, not infrastructure

---

## Implementation Details

### Task App Loading

The `InProcessTaskApp` class supports multiple ways to provide a task app:

1. **File Path** (most common):
   ```python
   InProcessTaskApp(task_app_path="task_app.py")
   ```

2. **Config Factory**:
   ```python
   InProcessTaskApp(config_factory=build_config)
   ```

3. **Config Object**:
   ```python
   config = build_config()
   InProcessTaskApp(config=config)
   ```

4. **FastAPI App** (most direct):
   ```python
   app = create_app(build_config())
   InProcessTaskApp(app=app)
   ```

### Background Server

The task app runs in a non-daemon thread using `_start_uvicorn_background()`:

```python
_start_uvicorn_background(app, host="127.0.0.1", port=8114, daemon=False)
```

Using `daemon=False` ensures the thread survives when the main process exits, allowing proper cleanup.

### Health Check

Before opening the tunnel, the class waits for the server to respond:

```python
await _wait_for_health_check(
    host="127.0.0.1",
    port=8114,
    api_key="test",
    timeout=30.0,
)
```

This ensures the tunnel only opens when the server is ready.

### Tunnel Management

The Cloudflare tunnel is opened using `open_quick_tunnel()`:

```python
url, tunnel_proc = open_quick_tunnel(port=8114, wait_s=15.0)
```

The tunnel process is stored and cleaned up in `__aexit__`:

```python
async def __aexit__(self, exc_type, exc_val, exc_tb):
    if self._tunnel_proc:
        stop_tunnel(self._tunnel_proc)
```

---

## Troubleshooting

### ❌ "Task app failed health check"

**Solution:** Check that:
1. Port is not already in use: `lsof -i :8114`
2. Task app file is valid Python
3. Task app has required endpoints (`/health`, `/rollout`, etc.)

### ❌ "Failed to open tunnel"

**Solution:**
1. Ensure `cloudflared` is installed (auto-installs if missing)
2. Check internet connection
3. Try a different port if 8114 is busy

### ❌ "GROQ_API_KEY required"

**Solution:** Set environment variable:
```bash
export GROQ_API_KEY="your_key"
# Or add to .env file
```

### ❌ "Backend not responding"

**Solution:** Ensure backend is running:
```bash
curl http://localhost:8000/api/health
```

---

## Next Steps

1. **Try other tasks**: Modify the script to use different task apps (Banking77, HotpotQA, etc.)
2. **Experiment with parameters**: Adjust GEPA config (population size, generations, budget)
3. **Compare with baseline**: Run baseline evaluation to measure improvement
4. **Production deployment**: For production, use Modal deployment instead of in-process

---

## Files

- **`synth_ai/task/in_process.py`**: `InProcessTaskApp` class implementation
- **`examples/gepa/run_in_process_gepa.py`**: Demo script
- **`examples/blog_posts/gepa/configs/heartdisease_gepa_local.toml`**: GEPA configuration
- **`examples/task_apps/other_langprobe_benchmarks/heartdisease_task_app.py`**: Task app implementation

---

## Summary

In-process GEPA makes prompt optimization **accessible, reproducible, and hassle-free**. With a single Python script, you can:

- ✅ Start task apps automatically
- ✅ Open tunnels automatically  
- ✅ Run GEPA optimization
- ✅ Clean up automatically

Perfect for **local development, demos, and experiments**. For production deployments, use Modal or traditional task app deployment.

Happy optimizing! 🧬🚀

