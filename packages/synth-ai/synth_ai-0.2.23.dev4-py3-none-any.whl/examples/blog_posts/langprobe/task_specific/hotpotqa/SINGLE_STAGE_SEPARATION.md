# Single-Stage Simplification: Separate Logic Design

## Goal
Carve out specific and separate logic for making single-stage simpler while **NOT compromising multi-stage support at all**.

## Core Principle: Two Separate APIs

### Single-Stage API: `MIPROConfig.simple()`
- **Purpose**: Simple API for single-stage tasks (Iris, Banking77 single-stage, etc.)
- **Auto-creates**: Default module/stage structure
- **Auto-scales**: Seeds/iterations from `rollout_budget`
- **Hides**: Complex nested configs (TPE, Demo, Grounding, Meta-Update)
- **Exposes**: Only essential parameters + optional overrides

### Multi-Stage API: `MIPROConfig()` (Full Constructor)
- **Purpose**: Full control for multi-stage pipelines (banking77_pipeline, etc.)
- **Requires**: Explicit module/stage configuration
- **Exposes**: All parameters, all nested configs
- **No changes**: Keep existing API exactly as-is

## Implementation Strategy

### 1. **Separate Constructors**

```python
@dataclass
class MIPROConfig:
    """Fully-typed configuration object consumed by the MIPRO optimiser."""
    
    # ... existing fields ...
    
    @classmethod
    def simple(
        cls,
        task_app_url: str,
        task_app_api_key: str,
        env_name: str,
        rollout_budget: int,
        initial_prompt_messages: list[dict],
        # Optional overrides
        bootstrap_seeds: Optional[list[int]] = None,
        online_seeds: Optional[list[int]] = None,
        test_seeds: Optional[list[int]] = None,
        reference_pool: Optional[list[int]] = None,
        num_iterations: Optional[int] = None,
        num_evaluations_per_iteration: Optional[int] = None,
        batch_size: Optional[int] = None,
        meta_preset: str = "balanced",
        # ... other optional params ...
    ) -> "MIPROConfig":
        """Simple constructor for single-stage tasks.
        
        Auto-creates default module/stage, auto-scales seeds/iterations.
        For multi-stage tasks, use MIPROConfig() directly.
        """
        # Validate: ensure this is single-stage
        # (can't have multiple messages with different stage_ids)
        
        # Auto-scale seeds/iterations from rollout_budget
        # Auto-create: modules=[MIPROModuleConfig(module_id="default", stages=[...])]
        # Extract baseline_instruction from initial_prompt_messages
        # Use sensible defaults for everything else
        
        # Return full MIPROConfig with auto-populated fields
        return cls(
            task_app_url=task_app_url,
            task_app_api_key=task_app_api_key,
            env_name=env_name,
            seeds=MIPROSeedConfig(
                bootstrap=bootstrap_seeds or _auto_calculate_bootstrap_seeds(rollout_budget),
                online=online_seeds or _auto_calculate_online_seeds(rollout_budget),
                test=test_seeds or [],
                reference=reference_pool or _auto_calculate_reference_pool(rollout_budget),
            ),
            num_iterations=num_iterations or _auto_calculate_iterations(rollout_budget),
            num_evaluations_per_iteration=num_evaluations_per_iteration or _auto_calculate_evaluations(rollout_budget),
            batch_size=batch_size or _auto_calculate_batch_size(rollout_budget),
            # ... auto-create modules/stages ...
            modules=[
                MIPROModuleConfig(
                    module_id="default",
                    stages=[
                        MIPROStageConfig(
                            stage_id="default_stage_0",
                            baseline_instruction=_extract_baseline_instruction(initial_prompt_messages),
                            baseline_messages=_normalize_messages(initial_prompt_messages),
                        )
                    ],
                )
            ],
            # Use defaults for nested configs
            meta=_create_meta_config_from_preset(meta_preset),
            instructions=MIPROInstructionConfig(),  # Defaults
            # ... other defaults ...
        )
    
    def __init__(
        self,
        task_app_url: str,
        task_app_api_key: str,
        seeds: MIPROSeedConfig,
        # ... all existing fields ...
    ):
        """Full constructor for multi-stage tasks.
        
        Use this for pipelines with multiple modules/stages.
        For single-stage tasks, use MIPROConfig.simple() instead.
        """
        # Existing implementation - NO CHANGES
        pass
```

### 2. **Validation: Ensure Separation**

```python
@classmethod
def simple(...):
    """Simple constructor for single-stage tasks."""
    # Validate: ensure initial_prompt_messages is single-stage
    # (can't have metadata.pipeline_modules or multiple stage_ids)
    if _has_multi_stage_indicators(initial_prompt_messages):
        raise MIPROConfigurationError(
            "MIPROConfig.simple() is for single-stage tasks only. "
            "For multi-stage pipelines, use MIPROConfig() directly."
        )
    
    # ... rest of implementation ...
```

### 3. **Auto-Scaling Logic: Separate Functions**

```python
def _auto_calculate_bootstrap_seeds(rollout_budget: int) -> list[int]:
    """Auto-calculate bootstrap seeds from rollout budget."""
    if rollout_budget < 50:
        return list(range(5))
    elif rollout_budget < 100:
        return list(range(10))
    elif rollout_budget < 200:
        return list(range(20))
    else:
        return list(range(30))

def _auto_calculate_online_seeds(rollout_budget: int, bootstrap_count: int) -> list[int]:
    """Auto-calculate online seeds from rollout budget."""
    # Ensure no overlap with bootstrap seeds
    start = bootstrap_count
    if rollout_budget < 50:
        return list(range(start, start + 10))
    elif rollout_budget < 100:
        return list(range(start, start + 20))
    elif rollout_budget < 200:
        return list(range(start, start + 30))
    else:
        return list(range(start, start + 50))

def _auto_calculate_iterations(rollout_budget: int) -> int:
    """Auto-calculate iterations from rollout budget."""
    # Formula: iterations ≈ (rollout_budget - bootstrap_seeds) / (evaluations_per_iteration * batch_size)
    # Conservative estimate
    if rollout_budget < 50:
        return 3
    elif rollout_budget < 100:
        return 5
    elif rollout_budget < 200:
        return 10
    else:
        return 20

def _auto_calculate_evaluations_per_iteration(rollout_budget: int) -> int:
    """Auto-calculate evaluations per iteration from rollout budget."""
    if rollout_budget < 50:
        return 2
    elif rollout_budget < 100:
        return 3
    elif rollout_budget < 200:
        return 4
    else:
        return 5

def _auto_calculate_batch_size(rollout_budget: int, online_seeds_count: int) -> int:
    """Auto-calculate batch size from rollout budget."""
    # Ensure batch_size <= online_seeds_count
    if rollout_budget < 50:
        return min(8, online_seeds_count)
    elif rollout_budget < 100:
        return min(16, online_seeds_count)
    elif rollout_budget < 200:
        return min(24, online_seeds_count)
    else:
        return min(32, online_seeds_count)

def _auto_calculate_reference_pool(rollout_budget: int, online_end: int) -> Optional[list[int]]:
    """Auto-calculate reference pool from rollout budget (optional)."""
    # Only create reference pool for larger budgets
    if rollout_budget < 200:
        return None
    # Start after online seeds
    start = online_end
    size = min(100, rollout_budget // 10)  # Up to 100 seeds
    return list(range(start, start + size))
```

### 4. **Module/Stage Auto-Creation: Single-Stage Only**

```python
def _extract_baseline_instruction(initial_prompt_messages: list[dict]) -> str:
    """Extract baseline instruction from initial prompt messages."""
    for msg in initial_prompt_messages:
        if msg.get("role") == "system":
            return msg.get("pattern", msg.get("content", ""))
    return "Complete the task."

def _normalize_messages(initial_prompt_messages: list[dict]) -> list[dict]:
    """Normalize initial prompt messages for single-stage."""
    normalized = []
    for msg in initial_prompt_messages:
        normalized.append({
            "role": msg.get("role", "user"),
            "content": msg.get("pattern", msg.get("content", "")),
        })
    return normalized

def _has_multi_stage_indicators(initial_prompt_messages: list[dict]) -> bool:
    """Check if initial_prompt_messages indicates multi-stage."""
    # Check for metadata.pipeline_modules
    for msg in initial_prompt_messages:
        if isinstance(msg, dict) and "metadata" in msg:
            metadata = msg["metadata"]
            if isinstance(metadata, dict) and "pipeline_modules" in metadata:
                return True
    return False
```

### 5. **Meta Config Presets: Separate from Full Config**

```python
def _create_meta_config_from_preset(preset: str) -> MIPROMetaConfig:
    """Create meta config from preset (single-stage only)."""
    presets = {
        "balanced": MIPROMetaConfig(
            model="gpt-4o-mini",
            provider="openai",
            inference_url=None,
            temperature=0.3,
            max_tokens=600,
        ),
        "fast": MIPROMetaConfig(
            model="gpt-4o-mini",
            provider="openai",
            inference_url=None,
            temperature=0.5,
            max_tokens=400,
        ),
        "high_quality": MIPROMetaConfig(
            model="gpt-4",
            provider="openai",
            inference_url=None,
            temperature=0.2,
            max_tokens=800,
        ),
    }
    return presets.get(preset, presets["balanced"])
```

## Key Separation Points

### 1. **Constructor Separation**
- `MIPROConfig.simple()` → Single-stage only
- `MIPROConfig()` → Multi-stage (or single-stage if you want full control)

### 2. **Validation Separation**
- `simple()` validates it's single-stage
- Full constructor has no restrictions

### 3. **Auto-Scaling Separation**
- `simple()` uses auto-scaling functions
- Full constructor requires explicit values

### 4. **Module/Stage Creation Separation**
- `simple()` auto-creates default module/stage
- Full constructor requires explicit modules/stages

### 5. **Nested Config Separation**
- `simple()` uses defaults for TPE, Demo, Grounding, Meta-Update
- Full constructor exposes all nested configs

## Migration Path

### Phase 1: Add `MIPROConfig.simple()` (No Changes to Existing API)
- Add `simple()` classmethod
- Add auto-scaling helper functions
- Add validation for single-stage
- **No changes** to `MIPROConfig.__init__()`

### Phase 2: Update Adapters (Optional)
- Update single-stage adapters to use `simple()`
- Keep multi-stage adapters using full constructor
- **No breaking changes**

### Phase 3: Documentation
- Document when to use `simple()` vs full constructor
- Provide examples for both
- **No breaking changes**

## Testing Strategy

### Single-Stage Tests
```python
def test_simple_single_stage():
    """Test simple() for single-stage task."""
    config = MIPROConfig.simple(
        task_app_url="http://localhost:8100",
        task_app_api_key="test-key",
        env_name="iris",
        rollout_budget=400,
        initial_prompt_messages=[
            {"role": "system", "pattern": "Classify the input."},
            {"role": "user", "pattern": "{features}"},
        ],
    )
    assert len(config.modules) == 1
    assert len(config.modules[0].stages) == 1
    assert config.modules[0].module_id == "default"
    assert config.modules[0].stages[0].stage_id == "default_stage_0"

def test_simple_rejects_multi_stage():
    """Test simple() rejects multi-stage indicators."""
    with pytest.raises(MIPROConfigurationError, match="single-stage tasks only"):
        MIPROConfig.simple(
            task_app_url="http://localhost:8100",
            task_app_api_key="test-key",
            env_name="banking77_pipeline",
            rollout_budget=400,
            initial_prompt_messages=[
                {"role": "system", "pattern": "...", "metadata": {"pipeline_modules": [...]}},
            ],
        )
```

### Multi-Stage Tests (No Changes)
```python
def test_full_multi_stage():
    """Test full constructor for multi-stage (existing test - no changes)."""
    config = MIPROConfig(
        task_app_url="http://localhost:8100",
        task_app_api_key="test-key",
        env_name="banking77_pipeline",
        seeds=MIPROSeedConfig(...),
        modules=[
            MIPROModuleConfig(
                module_id="classifier",
                stages=[...],
            ),
            MIPROModuleConfig(
                module_id="calibrator",
                stages=[...],
            ),
        ],
    )
    # Existing assertions - no changes
```

## Benefits

1. **Zero Breaking Changes**: Full constructor unchanged
2. **Clear Separation**: Single-stage vs multi-stage APIs are distinct
3. **Backward Compatible**: Existing code continues to work
4. **Progressive Enhancement**: New code can use simpler API
5. **No Compromise**: Multi-stage support remains full-featured

## Conclusion

By separating single-stage simplification into `MIPROConfig.simple()` while keeping `MIPROConfig()` unchanged, we:
- ✅ Make single-stage easier
- ✅ Preserve multi-stage fully
- ✅ Avoid breaking changes
- ✅ Maintain clear separation of concerns

