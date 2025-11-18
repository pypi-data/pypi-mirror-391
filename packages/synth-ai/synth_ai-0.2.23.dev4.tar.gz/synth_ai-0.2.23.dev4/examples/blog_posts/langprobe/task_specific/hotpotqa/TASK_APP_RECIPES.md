# Task App Recipes: Tracing & Rewards

This document provides straightforward recipes for task apps to produce trajectories with the required information (`inference_url` with `?cid=...`) and optionally leverage tracing/reward abstractions.

## Quick Recipe: Minimal Implementation

**Goal**: Produce a valid `RolloutTrajectory` with `inference_url` containing `?cid=trace_xxxxx`.

### Step 1: Extract `trace_correlation_id` from Request

```python
from synth_ai.task.trace_correlation_helpers import extract_trace_correlation_id

async def rollout_executor(request: RolloutRequest, fastapi_request: Request) -> RolloutResponse:
    policy_config = request.policy.config or {}
    
    # Extract trace_correlation_id (trainer adds ?cid=trace_xxxxx to inference_url)
    trace_correlation_id = extract_trace_correlation_id(
        policy_config=policy_config,
        inference_url=policy_config.get("inference_url"),
        mode=request.mode
    )
    
    # For RL mode, trace_correlation_id is required
    if request.mode == RolloutMode.RL:
        assert trace_correlation_id is not None, "trace_correlation_id required for RL mode"
```

### Step 2: Use `inference_url` Directly (Trainer Already Added `?cid=...`)

```python
    # The trainer already added ?cid=trace_xxxxx to inference_url
    # Just use it directly - no need to modify!
    inference_url = policy_config.get("inference_url", "")
    
    trajectory = RolloutTrajectory(
        env_id=f"iris::{sample['split']}::{sample['index']}",
        policy_id=request.policy.policy_id or "policy",
        steps=[step],
        final={"observation": observation, "reward": reward},
        length=1,
        inference_url=str(inference_url),  # ✅ Already contains ?cid=trace_xxxxx
    )
```

### Step 3: Compute Reward (Simple)

```python
    # Simple reward computation
    reward = 1.0 if answer_correct else 0.0
    
    metrics = RolloutMetrics(
        episode_returns=[reward],
        mean_return=reward,  # ✅ Used for scoring (same as GRPO/RL)
        num_steps=1,
        num_episodes=1,
        # outcome_score: ❌ NOT NEEDED - use mean_return instead!
    )
```

### Complete Minimal Example

```python
from synth_ai.task.contracts import (
    RolloutRequest,
    RolloutResponse,
    RolloutTrajectory,
    RolloutStep,
    RolloutMetrics,
    RolloutMode,
)
from synth_ai.task.trace_correlation_helpers import extract_trace_correlation_id

async def rollout_executor(request: RolloutRequest, fastapi_request: Request) -> RolloutResponse:
    # 1. Extract trace_correlation_id
    policy_config = request.policy.config or {}
    trace_correlation_id = extract_trace_correlation_id(
        policy_config=policy_config,
        inference_url=policy_config.get("inference_url"),
        mode=request.mode
    )
    
    # 2. Get inference_url (trainer already added ?cid=trace_xxxxx)
    inference_url = policy_config.get("inference_url", "")
    
    # 3. Run your task logic
    sample = get_sample(request.env.seed)
    observation = {"question": sample["question"]}
    
    # 4. Call LLM (using inference_url - it already has ?cid=...)
    response = await call_llm(inference_url, observation)
    
    # 5. Compute reward
    answer_correct = check_answer(response, sample["answer"])
    reward = 1.0 if answer_correct else 0.0
    
    # 6. Build step
    step = RolloutStep(
        obs=observation,
        action={"response": response},
        reward=reward,
        done=True,
        info={"answer_correct": answer_correct},
    )
    
    # 7. Build trajectory (inference_url already has ?cid=...)
    trajectory = RolloutTrajectory(
        env_id=f"iris::{sample['split']}::{sample['index']}",
        policy_id=request.policy.policy_id or "policy",
        steps=[step],
        final={"observation": observation, "reward": reward},
        length=1,
        inference_url=str(inference_url),  # ✅ Contains ?cid=trace_xxxxx
    )
    
    # 8. Build metrics (use mean_return for scoring)
    metrics = RolloutMetrics(
        episode_returns=[reward],
        mean_return=reward,  # ✅ Used for scoring
        num_steps=1,
        num_episodes=1,
    )
    
    return RolloutResponse(
        run_id=request.run_id,
        trajectories=[trajectory],
        metrics=metrics,
    )
```

## Advanced Recipe: Using V3 Tracing (Optional)

**Goal**: Use `SessionTracer` to create rich v3 traces for debugging/analysis.

### Step 1: Initialize SessionTracer

```python
from synth_ai.tracing_v3 import SessionTracer

# Initialize tracer (one per task app instance)
tracer = SessionTracer()
await tracer.initialize()
```

### Step 2: Create Trace Session Per Rollout

```python
async def rollout_executor(request: RolloutRequest, fastapi_request: Request) -> RolloutResponse:
    # Extract trace_correlation_id (use as session_id for correlation)
    policy_config = request.policy.config or {}
    trace_correlation_id = extract_trace_correlation_id(
        policy_config=policy_config,
        inference_url=policy_config.get("inference_url"),
        mode=request.mode
    )
    
    # Start trace session (use trace_correlation_id as session_id)
    session_id = trace_correlation_id or f"trace_{request.run_id}"
    
    async with tracer.session(session_id=session_id, metadata={
        "run_id": request.run_id,
        "env_name": request.env.env_name,
        "seed": request.env.seed,
    }) as session_id:
        async with tracer.timestep("rollout", turn_number=1):
            # Record observation
            await tracer.record_event(EnvironmentEvent(
                event_type="observation",
                content={"observation": observation},
            ))
            
            # Record LLM call (if using @trace_llm_call decorator)
            response = await call_llm_with_tracing(inference_url, observation)
            
            # Record action
            await tracer.record_event(RuntimeEvent(
                event_type="action",
                content={"action": response},
            ))
            
            # Record reward
            await tracer.record_event(EnvironmentEvent(
                event_type="reward",
                content={"reward": reward},
            ))
    
    # Traces are automatically saved to trace store
    # Backend can fetch them using trace_correlation_id
```

### Step 3: Use Trace Correlation ID

```python
    # The trace_correlation_id links:
    # 1. Rollout request → Trace session
    # 2. Inference URL → LLM call traces
    # 3. Rollout response → Full trace data
    
    # Backend can fetch traces using:
    # - trace_correlation_id (from inference_url ?cid=...)
    # - session_id (same as trace_correlation_id)
```

## Advanced Recipe: Using Reward Abstractions (Optional)

**Goal**: Use `Rubric` or `RewardComponent` for structured reward computation.

### Option A: Using Rubrics (JSON-Based Scoring)

```python
from synth_ai.task.rubrics import load_rubric, score_outcome_against_rubric

# Load rubric from file (or define inline)
rubric = load_rubric("path/to/rubric.json")
# Or define programmatically:
# from synth_ai.task.rubrics import Rubric, Criterion
# rubric = Rubric(
#     version="1.0",
#     goal_text="Evaluate answer correctness",
#     criteria=[
#         Criterion(id="correctness", description="Answer is correct", weight=1.0),
#         Criterion(id="support", description="Supporting evidence provided", weight=0.3),
#     ],
#     aggregation="weighted_sum"
# )

async def rollout_executor(request: RolloutRequest, fastapi_request: Request) -> RolloutResponse:
    # ... run task logic ...
    
    # Compute outcome scores per criterion
    outcome = {
        "correctness": 1.0 if answer_correct else 0.0,
        "support": support_coverage,  # 0.0 to 1.0
    }
    
    # Score against rubric
    scoring_result = score_outcome_against_rubric(outcome, rubric)
    reward = scoring_result["score"]  # Weighted sum
    
    metrics = RolloutMetrics(
        episode_returns=[reward],
        mean_return=reward,  # ✅ Used for scoring
        num_steps=1,
        num_episodes=1,
        details={
            "rubric_score": reward,
            "per_criterion": scoring_result["per_criterion"],
        },
    )
```

### Option B: Using RewardComponent (Class-Based Scoring)

```python
from synth_ai.environments.environment.rewards.core import RewardComponent, RewardStack

class CorrectnessReward(RewardComponent):
    """Reward for correct answers."""
    weight = 1.0
    
    async def score(self, state: dict, action: dict) -> float:
        answer_correct = state.get("answer_correct", False)
        return 1.0 if answer_correct else 0.0

class SupportReward(RewardComponent):
    """Reward for supporting evidence."""
    weight = 0.3
    
    async def score(self, state: dict, action: dict) -> float:
        support_coverage = state.get("support_coverage", 0.0)
        return float(support_coverage)

# Create reward stack
reward_stack = RewardStack([
    CorrectnessReward(),
    SupportReward(),
])

async def rollout_executor(request: RolloutRequest, fastapi_request: Request) -> RolloutResponse:
    # ... run task logic ...
    
    # Compute reward using stack
    state = {
        "answer_correct": answer_correct,
        "support_coverage": support_coverage,
    }
    action = {"response": response}
    reward = await reward_stack.step_reward(state, action)
    
    metrics = RolloutMetrics(
        episode_returns=[reward],
        mean_return=reward,  # ✅ Used for scoring
        num_steps=1,
        num_episodes=1,
    )
```

## Key Points

### 1. `inference_url` Already Contains `?cid=...`

**✅ DO THIS**:
```python
# Trainer already added ?cid=trace_xxxxx to inference_url
inference_url = policy_config.get("inference_url", "")
trajectory = RolloutTrajectory(
    ...
    inference_url=str(inference_url),  # ✅ Use as-is
)
```

**❌ DON'T DO THIS**:
```python
# Don't manually add ?cid=... - trainer already did it!
inference_url = f"{policy_config.get('inference_url')}?cid={trace_correlation_id}"
```

### 2. Use `mean_return` for Scoring

**✅ DO THIS**:
```python
metrics = RolloutMetrics(
    episode_returns=[reward],
    mean_return=reward,  # ✅ Used for scoring (same as GRPO/RL)
    num_steps=1,
)
```

**❌ DON'T DO THIS**:
```python
# Don't set outcome_score - use mean_return instead!
metrics = RolloutMetrics(
    mean_return=reward,
    outcome_score=reward,  # ❌ Redundant - not needed!
)
```

### 3. Extract `trace_correlation_id` for Optional Tracing

**✅ DO THIS**:
```python
from synth_ai.task.trace_correlation_helpers import extract_trace_correlation_id

trace_correlation_id = extract_trace_correlation_id(
    policy_config=policy_config,
    inference_url=policy_config.get("inference_url"),
    mode=request.mode
)
```

**❌ DON'T DO THIS**:
```python
# Don't manually parse URL - use helper!
parsed = urlparse(inference_url)
cid = parse_qs(parsed.query).get("cid")[0]  # ❌ Fragile!
```

## Summary: What Task Apps Need to Do

### Required (Minimal)

1. ✅ Extract `inference_url` from `request.policy.config.get("inference_url")`
2. ✅ Use `inference_url` directly in `RolloutTrajectory.inference_url` (trainer already added `?cid=...`)
3. ✅ Compute `mean_return` in `RolloutMetrics` (used for scoring)

### Optional (Advanced)

1. 🔵 Extract `trace_correlation_id` using `extract_trace_correlation_id()` helper
2. 🔵 Use `SessionTracer` to create v3 traces (for debugging/analysis)
3. 🔵 Use `Rubric` or `RewardComponent` for structured reward computation

## Migration Guide

### From Current Implementation

**Before**:
```python
inference_url = (request.policy.config or {}).get("inference_url")
trajectory = RolloutTrajectory(
    ...
    inference_url=str(inference_url or ""),
)
metrics = RolloutMetrics(
    mean_return=reward,
    outcome_score=reward,  # ❌ Remove this
)
```

**After**:
```python
# Same! inference_url already has ?cid=... from trainer
inference_url = (request.policy.config or {}).get("inference_url")
trajectory = RolloutTrajectory(
    ...
    inference_url=str(inference_url or ""),  # ✅ Already correct!
)
metrics = RolloutMetrics(
    mean_return=reward,  # ✅ Use mean_return (remove outcome_score)
    # outcome_score: ❌ NOT NEEDED
)
```

**No changes needed!** Task apps already work correctly - just remove `outcome_score` if present.

## References

- **Trace Correlation Helpers**: `synth_ai.task.trace_correlation_helpers`
- **V3 Tracing**: `synth_ai.tracing_v3.SessionTracer`
- **Rubrics**: `synth_ai.task.rubrics`
- **Reward Components**: `synth_ai.environments.environment.rewards.core`

