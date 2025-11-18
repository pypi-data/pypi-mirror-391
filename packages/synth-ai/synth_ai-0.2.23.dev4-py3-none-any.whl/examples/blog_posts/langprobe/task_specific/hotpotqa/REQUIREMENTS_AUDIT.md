# Requirements Audit: outcome_score vs mean_return

## Current State Analysis

### How GEPA/MIPRO Currently Uses Scores

**Function**: `extract_accuracy_from_response()` in `evaluation.py`

**Fallback Chain**:
1. `metrics.outcome_score` (primary)
2. `metrics.details.correct` (fallback for classification)
3. `metrics.mean_return` (fallback for RL tasks)
4. `0.0` (default)

### How GRPO/RL Uses Scores

**Function**: `_collect_batch_sync()` in `clustered_trainer.py`

**Usage**:
```python
env_reward = metrics.get("mean_return") or metrics.get("episode_returns", [None])[0]
```

**Key Point**: GRPO/RL uses `mean_return` directly, doesn't check `outcome_score` at all!

### How Task Apps Currently Set These Fields

**Iris Task App**:
```python
metrics = RolloutMetrics(
    episode_returns=[reward],
    mean_return=reward,      # ✅ Required
    num_steps=1,
    num_episodes=1,
    outcome_score=reward,     # ⚠️ Set to same value as mean_return!
    events_score=reward,
    ...
)
```

**HotpotQA Task App**:
```python
metrics = RolloutMetrics(
    episode_returns=[reward],
    mean_return=reward,      # ✅ Required
    num_steps=1,
    num_episodes=1,
    outcome_score=reward,     # ⚠️ Set to same value as mean_return!
    events_score=reward,
    ...
)
```

**Verilog Task App**:
```python
metrics = RolloutMetrics(
    episode_returns=[reward],
    mean_return=final_total_reward,  # ✅ Required
    num_steps=len(steps),
    num_episodes=1,
    outcome_score=final_total_reward,  # ⚠️ Set to same value as mean_return!
    ...
)
```

## Key Finding: They're Always Identical!

**Observation**: Every task app sets `outcome_score = mean_return` (same value).

**Why?**
- For single-episode rollouts: `mean_return = average(episode_returns) = episode_returns[0] = reward`
- Task apps set `outcome_score = reward` (same value)
- **Result**: `outcome_score == mean_return` always!

## Can We Eliminate `outcome_score`?

### ✅ YES - Here's Why:

1. **Already Required**: `mean_return` is already required in the schema (same for GRPO and GEPA/MIPRO)
2. **Already Used as Fallback**: GEPA/MIPRO already falls back to `mean_return` if `outcome_score` is missing
3. **Always Identical**: Task apps set them to the same value anyway
4. **GRPO Doesn't Need It**: GRPO/RL uses `mean_return` directly, doesn't check `outcome_score`

### Edge Cases to Consider:

**Multi-Episode Rollouts**:
- If a rollout has multiple episodes: `mean_return = average([ep1_reward, ep2_reward, ...])`
- Currently: `outcome_score` is also set to this average
- **Conclusion**: No difference, can use `mean_return` directly

**Different Scoring Logic**:
- Could someone want `outcome_score` to differ from `mean_return`?
  - Example: `mean_return = 0.5` (average), but `outcome_score = 1.0` (binary success)
- **Current Reality**: No task apps do this
- **GRPO Reality**: GRPO doesn't need this distinction
- **Recommendation**: If needed in future, can add `outcome_score` back, but for now it's redundant

## Proposed Change

### Eliminate `outcome_score` Requirement

**Change `extract_accuracy_from_response()`**:
```python
def extract_accuracy_from_response(response_data: Dict[str, Any]) -> float:
    """Extract score from RolloutResponse using mean_return (same as GRPO/RL)."""
    metrics = response_data.get("metrics", {})
    
    # Primary: mean_return (required in schema, same as GRPO/RL)
    mean_return = metrics.get("mean_return")
    if mean_return is not None:
        return float(mean_return)
    
    # Fallback: details.correct (for backward compatibility with old task apps)
    details = metrics.get("details", {})
    if details.get("correct") is True:
        return 1.0
    elif details.get("correct") is False:
        return 0.0
    
    # Fallback: episode_returns[0] (if mean_return missing)
    episode_returns = metrics.get("episode_returns", [])
    if episode_returns:
        return float(episode_returns[0])
    
    # Default: 0.0
    return 0.0
```

**Benefits**:
1. ✅ **100% identical to GRPO/RL** - uses `mean_return` directly
2. ✅ **Simpler** - one less field to worry about
3. ✅ **No breaking changes** - task apps can still set `outcome_score` (just ignored)
4. ✅ **Backward compatible** - fallback to `details.correct` still works

## Updated Requirements Comparison

### After Eliminating `outcome_score`

| Field | GRPO/RL | GEPA/MIPRO (After) | Difference |
|-------|---------|-------------------|------------|
| **`run_id`** | ✅ Required | ✅ Required | ✅ **100% Identical** |
| **`trajectories`** | ✅ Required (can be `[]`) | ✅ Required (can be `[]`) | ✅ **100% Identical** |
| **`metrics.episode_returns`** | ✅ Required | ✅ Required | ✅ **100% Identical** |
| **`metrics.mean_return`** | ✅ Required | ✅ Required | ✅ **100% Identical** |
| **`metrics.num_steps`** | ✅ Required | ✅ Required | ✅ **100% Identical** |
| **`metrics.outcome_score`** | ❌ Not used | ❌ **Not used** | ✅ **100% Identical** |
| **`trajectories[].inference_url`** | ✅ Required (with `?cid=...`) | ✅ Required (with `?cid=...`) | ✅ **100% Identical** |
| **`trajectories[].env_id`** | ✅ Required | ✅ Required | ✅ **100% Identical** |
| **`trajectories[].policy_id`** | ✅ Required | ✅ Required | ✅ **100% Identical** |
| **`trajectories[].steps`** | ✅ Required (can be `[]`) | ✅ Required (can be `[]`) | ✅ **100% Identical** |
| **`trajectories[].steps[].obs`** | ✅ Required (can be `{}`) | ✅ Required (can be `{}`) | ✅ **100% Identical** |
| **`trajectories[].steps[].action`** | ✅ Required (can be `{}`) | ✅ Required (can be `{}`) | ✅ **100% Identical** |
| **`trajectories[].steps[].reward`** | ✅ Required | ✅ Required | ✅ **100% Identical** |
| **`trajectories[].steps[].done`** | ✅ Required | ✅ Required | ✅ **100% Identical** |
| **`trajectories[].steps[].info.messages`** | ❌ Not required | ❌ Not required | ✅ **100% Identical** |
| **`trajectories[].steps[].obs.text`** | ❌ Optional | ❌ Optional | ✅ **100% Identical** |
| **`trajectories[].steps[].action.text`** | ❌ Optional | ❌ Optional | ✅ **100% Identical** |

## Result: 100% Identical Requirements!

After eliminating `outcome_score`, **GEPA/MIPRO requirements are 100% identical to GRPO/RL**!

### Minimal Task App Contract (Final)

```json
{
  "run_id": "rollout-0",
  "trajectories": [
    {
      "env_id": "iris",
      "policy_id": "policy",
      "steps": [
        {
          "obs": {},
          "action": {},
          "reward": 1.0,
          "done": true
        }
      ],
      "length": 1,
      "inference_url": "http://localhost:8000/v1/chat/completions?cid=trace_abc123"
    }
  ],
  "metrics": {
    "episode_returns": [1.0],
    "mean_return": 1.0,  // ✅ REQUIRED - used for scoring (same as GRPO/RL)
    "num_steps": 1
    // outcome_score: ❌ NOT NEEDED - use mean_return instead!
  }
}
```

## Migration Plan

### Phase 1: Update `extract_accuracy_from_response()`
- Change primary source from `outcome_score` → `mean_return`
- Keep `outcome_score` as optional fallback (backward compatibility)
- Update docstrings

### Phase 2: Update Task Apps (Optional)
- Remove `outcome_score` from task apps (they can keep it, just ignored)
- Or keep it for backward compatibility (no harm)

### Phase 3: Update Documentation
- Remove `outcome_score` from required fields
- Document that `mean_return` is used for scoring (same as GRPO/RL)

## Benefits

1. ✅ **100% alignment with GRPO/RL** - identical requirements
2. ✅ **Simpler** - one less field to document/maintain
3. ✅ **No breaking changes** - backward compatible (task apps can still set `outcome_score`)
4. ✅ **Clearer** - `mean_return` is the canonical score field (same as GRPO/RL)

## Recommendation

**✅ ELIMINATE `outcome_score` requirement**

- Use `mean_return` directly (same as GRPO/RL)
- Keep `outcome_score` as optional fallback for backward compatibility
- Update documentation to reflect this change
- Task apps can optionally remove `outcome_score` (but no harm keeping it)

This makes GEPA/MIPRO requirements **100% identical** to GRPO/RL!

