# Local MIPRO/GEPA Scripts - Implementation Summary

## Overview

Both `run_mipro_local.py` and `run_gepa_local.py` now use the backend API endpoint (`http://localhost:8000`) with proper authentication, ensuring balance checking works correctly. They emulate the real production flow but bypass Modal execution.

## Changes Made

### 1. Backend Validation (`monorepo/backend/app/routes/prompt_learning/routes_online.py`)

**Updated localhost URL validation** to allow localhost when running locally:
- Checks if backend is running in Modal using `detect_runtime()`
- Only rejects localhost URLs if `is_modal() == True`
- Allows localhost URLs for local development/testing

**Key Code:**
```python
# Only reject localhost if we're running in Modal (not locally)
runtime = detect_runtime()
is_modal = runtime.is_modal() if hasattr(runtime, 'is_modal') else False

if is_localhost and is_modal:
    raise HTTPException(...)  # Only reject in Modal
```

### 2. Scripts (`run_mipro_local.py` and `run_gepa_local.py`)

**Updated to use backend endpoint:**
- Generate TOML configs programmatically
- Use SDK (`PromptLearningJob.from_config()`) to submit jobs
- Authenticate via `SYNTH_API_KEY` (provides `user_id`/`org_id`)
- Poll for completion using SDK
- Extract cost and balance from `best_snapshot` in results

**Cost/Balance Extraction:**
```python
best_snapshot = job_detail.get("best_snapshot")
if best_snapshot:
    print(f"Total Cost: ${best_snapshot.get('total_cost_usd', 0.0):.4f}")
    print(f"Category Costs: {best_snapshot.get('category_costs', {})}")
    if best_snapshot.get('final_balance_usd') is not None:
        print(f"Final Balance: ${best_snapshot.get('final_balance_usd'):.2f}")
```

### 3. Cost/Balance Tracking (Already Implemented)

**Backend already includes cost/balance in results:**
- MIPRO: Lines 2333-2336 in `online_jobs.py`
- GEPA: Lines 1170-1173 in `online_jobs.py`
- Both store in snapshot payload which is returned via API

**Fields included:**
- `total_cost_usd`: Total USD spent during optimization
- `category_costs`: Breakdown by category (e.g., `{"rollout": 0.05, "proposal": 0.02}`)
- `final_balance_usd`: User balance after optimization (if `user_id`/`org_id` available)
- `balance_type`: Type of balance checked ("user" or None)

## Prerequisites

1. **Backend server running** at `http://localhost:8000`
2. **Backend server restarted** to pick up validation changes
3. **Task app running** at `http://127.0.0.1:8115` (Iris)
4. **Environment variables set:**
   - `SYNTH_API_KEY`: API key for authentication
   - `ENVIRONMENT_API_KEY`: Task app API key (or same as `SYNTH_API_KEY`)

## Usage

### MIPRO
```bash
python run_mipro_local.py \
    --rollout-budget 10 \
    --backend-url http://localhost:8000 \
    --task-app-url http://127.0.0.1:8115
```

### GEPA
```bash
python run_gepa_local.py \
    --rollout-budget 10 \
    --backend-url http://localhost:8000 \
    --task-app-url http://127.0.0.1:8115
```

## Expected Output

```
================================================================================
✅ MIPRO Optimization Complete!
================================================================================
Job ID: pl_abc123...
Status: completed
Best Score: 0.950 (95.0%)
Total Cost: $0.0012
Category Costs: {'rollout': 0.0008, 'proposal': 0.0004}
Final Balance: $99.50 (user)
================================================================================
```

## Verification Checklist

- [ ] Backend server restarted (required for localhost URL validation)
- [ ] Backend running at `http://localhost:8000`
- [ ] Task app running at `http://127.0.0.1:8115`
- [ ] `SYNTH_API_KEY` set in environment
- [ ] Scripts can submit jobs successfully
- [ ] Cost information appears in results
- [ ] Balance information appears in results (if `user_id`/`org_id` available)

## Notes

- **Balance checking**: Only works if `user_id`/`org_id` are extracted from API key (automatic when using backend endpoint)
- **Localhost URLs**: Now allowed when backend runs locally (not in Modal)
- **Cost tracking**: Uses `CostTracker` for real-time cost accumulation
- **Balance tracking**: Fetches from `PricingService` at end of optimization

