# HotpotQA Validation Guide

## Prerequisites

1. **Start HotpotQA Task App**:
   ```bash
   python -m examples.task_apps.gepa_benchmarks.hotpotqa_task_app --port 8110
   ```

2. **Verify Task App is Running**:
   ```bash
   curl http://127.0.0.1:8110/health
   ```

## Validation Tests

### Synth GEPA (Small Budget)

```bash
python3 -m examples.blog_posts.langprobe.task_specific.hotpotqa.run_synth_gepa_hotpotqa \
  --task-app-url http://127.0.0.1:8110 \
  --rollout-budget 10
```

**Expected**: Should complete without errors, generate optimized prompt, save results.

### Synth MIPRO (Small Budget)

```bash
python3 -m examples.blog_posts.langprobe.task_specific.hotpotqa.run_synth_mipro_hotpotqa \
  --task-app-url http://127.0.0.1:8110 \
  --rollout-budget 10
```

**Expected**: Should complete without errors, generate optimized prompt, save results.

## Notes

- **No tunnel needed**: In-process adapters run locally and connect directly to `http://127.0.0.1:8110`
- **Tunnels are only needed** for HTTP adapters that submit jobs to Modal backend
- Make sure task app is running before running optimization
- Use small budgets (5-10 rollouts) for quick validation

## Troubleshooting

- **"All connection attempts failed"**: Task app not running - start it first
- **"Pattern validation failed"**: Task app may not be storing messages correctly - check task app logs
- **"Backend not available"**: Make sure monorepo/backend is accessible

