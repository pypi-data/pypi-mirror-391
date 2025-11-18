# Judge Support for GEPA and MIPRO

First-class judge support for automatic reward scoring in prompt optimization, matching GRPO/RL's rubric judging capabilities.

## Overview

Judges automatically score trajectories using hydrated traces, eliminating the need for task apps to compute rewards manually. This provides:

- **Automatic Scoring**: No manual reward computation in task apps
- **Consistent Infrastructure**: Same `RubricPipeline` as GRPO/RL
- **Trace Hydration**: Automatic trace hydration via correlation IDs
- **Flexible Reward Sources**: Choose between task app, judge, or fused rewards
- **Spec Support**: Judges can use task-specific specs for context-aware scoring

## Quick Start

### Basic Usage

```python
from backend.app.routes.prompt_learning.algorithm.gepa import GEPAConfig, GEPAOptimizer
from backend.app.routes.prompt_learning.core.judge_config import JudgeConfig

# Create judge config
judge_config = JudgeConfig(
    enabled=True,
    reward_source="judge",  # Use judge rewards only
    backend_base="https://judge.synth.ai",
    backend_api_key_env="SYNTH_API_KEY",
    backend_provider="groq",
    backend_model="llama-3.3-70b-versatile",
    backend_rubric_id="iris-rubric-v1",
)

# Create GEPA config with judge
gepa_config = GEPAConfig(
    task_app_url="http://localhost:8115",
    task_app_api_key=os.getenv("ENVIRONMENT_API_KEY"),
    env_name="iris",
    judge=judge_config,  # Pass judge config
    # ... other config ...
)

# Optimizer automatically uses judge when enabled
optimizer = GEPAOptimizer(config=gepa_config)
best_template, best_score = await optimizer.optimize(...)
```

### Reward Source Options

1. **`"task_app"`** (default): Use task app rewards only (judge disabled)
2. **`"judge"`**: Use judge rewards only (task app rewards ignored)
3. **`"fused"`**: Weighted combination of task app and judge rewards

```python
# Fused rewards with custom weights
judge_config = JudgeConfig(
    enabled=True,
    reward_source="fused",
    weight_env=0.5,      # Weight for task app reward
    weight_event=0.3,     # Weight for event-level judge reward
    weight_outcome=0.2,   # Weight for outcome-level judge reward
)
```

### Spec Support

Judges can use task-specific specs for better context-aware scoring:

```python
judge_config = JudgeConfig(
    enabled=True,
    reward_source="judge",
    # Option 1: Load from file
    spec_path="examples/task_apps/iris/iris_spec.json",
    spec_max_tokens=5000,
    # Option 2: Pre-loaded spec context
    # spec_context="...",  # Pre-loaded spec context string
)
```

## Configuration Reference

### JudgeConfig

```python
@dataclass
class JudgeConfig:
    # Enable/disable
    enabled: bool = False
    
    # Reward source selection
    reward_source: Literal["task_app", "judge", "fused"] = "task_app"
    
    # Backend judge configuration
    backend_base: str = ""  # Required if enabled
    backend_api_key_env: str = "SYNTH_API_KEY"
    backend_provider: str = ""  # e.g., "groq", "openai"
    backend_model: str = ""  # e.g., "llama-3.3-70b-versatile"
    backend_rubric_id: str = ""  # Rubric ID
    backend_event_enabled: bool = True
    backend_outcome_enabled: bool = True
    backend_options: Dict[str, Any] = field(default_factory=dict)
    
    # Concurrency and timeout
    concurrency: int = 8
    timeout: float = 60.0
    
    # Reward fusion weights (when reward_source="fused")
    weight_env: float = 1.0
    weight_event: float = 0.0
    weight_outcome: float = 0.0
    
    # Spec support (optional)
    spec_path: Optional[str] = None
    spec_max_tokens: int = 5000
    spec_context: Optional[str] = None
```

## Example: Iris with Judge

See `run_gepa_iris_with_judge.py` for a complete example:

```bash
python run_gepa_iris_with_judge.py \
    --task-app-url http://127.0.0.1:8115 \
    --rollout-budget 20 \
    --judge-enabled \
    --judge-reward-source judge
```

## How It Works

1. **Trace Hydration**: When a rollout completes, the optimizer extracts the trajectory with `inference_url` containing `?cid=trace_xxx`
2. **Judge Scoring**: If judge is enabled, the trajectory is hydrated with trace data and sent to the judge backend
3. **Reward Fusion**: Rewards are fused based on `reward_source` configuration
4. **Optimization**: The fused reward is used for optimization (Pareto selection, etc.)

## Integration Points

- **GEPA**: Judge scoring happens in `_evaluate_population()` after `evaluate_prompt_template()` returns
- **MIPRO**: Similar integration in evaluation pipeline (to be implemented)
- **Task Apps**: No changes required - judges work with existing trace hydration

## Benefits

1. **No Manual Reward Computation**: Task apps don't need to compute rewards when judges are enabled
2. **Consistent with GRPO/RL**: Same judge infrastructure, same patterns
3. **Optional**: Works with or without judges (backward compatible)
4. **Automatic Trace Hydration**: Leverages existing trace hydration logic
5. **Flexible Reward Sources**: Can use task app, judge, or fused rewards
6. **Spec Support**: Judges can use task-specific specs for better context-aware scoring

## Migration Path

- Existing configs continue to work (judge disabled by default)
- Users can opt-in by setting `judge.enabled=true` and configuring judge backend
- Task apps can continue providing rewards (used when `reward_source="task_app"`)

