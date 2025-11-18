# Local MIPRO Runner for Iris

This script runs MIPRO locally on Iris for rapid iteration on fixing step.info issues.

## Prerequisites

1. **Iris task app running**:
   ```bash
   cd /path/to/synth-ai
   uv run python -m examples.task_apps.other_langprobe_benchmarks.iris_task_app
   # Task app runs on http://127.0.0.1:8115
   ```

2. **Environment variables**:
   - `ENVIRONMENT_API_KEY` or `SYNTH_API_KEY` - for task app authentication
   - `GROQ_API_KEY` - for LLM calls (policy and meta model)
   - `MONOREPO_BACKEND_PATH` (optional) - path to monorepo/backend if auto-detection fails
   - `SYNTH_AI_ROOT` (optional) - path to synth-ai if auto-detection fails

## Usage

```bash
cd /path/to/synth-ai
python examples/blog_posts/langprobe/task_specific/iris/run_mipro_local.py \
  --task-app-url http://127.0.0.1:8115 \
  --rollout-budget 20
```

### Options

- `--task-app-url`: Task app URL (default: `http://127.0.0.1:8115`)
- `--rollout-budget`: Total rollout budget (default: 20)
- `--bootstrap-seeds`: Bootstrap seeds (default: auto-scale)
- `--online-seeds`: Online pool seeds (default: auto-scale)
- `--test-seeds`: Test seeds (default: auto-scale)
- `--interceptor-port`: Interceptor port (default: 8765)

## Example: Small Test Run

```bash
python examples/blog_posts/langprobe/task_specific/iris/run_mipro_local.py \
  --rollout-budget 10 \
  --bootstrap-seeds 0 1 2 \
  --online-seeds 3 4 5
```

## What This Does

1. Creates `MIPROConfig` programmatically (no TOML needed)
2. Uses `LocalRuntime` for local execution
3. Creates `MIPROOptimizer` directly (bypasses adapter layer)
4. Runs optimization and prints results

## Benefits for Iteration

- **No Modal deployment** - runs entirely locally
- **Direct backend access** - can modify optimizer code and test immediately
- **Fast feedback** - see errors and results instantly
- **Full control** - can set breakpoints, inspect variables, etc.

## Troubleshooting

### Import errors
- Ensure `MONOREPO_BACKEND_PATH` points to `monorepo/backend`
- Ensure `SYNTH_AI_ROOT` points to `synth-ai` root

### Task app not found
- Ensure Iris task app is running on port 8115
- Check `ENVIRONMENT_API_KEY` is set correctly

### API key errors
- Ensure `GROQ_API_KEY` is set for LLM calls
- Ensure `ENVIRONMENT_API_KEY` is set for task app auth

