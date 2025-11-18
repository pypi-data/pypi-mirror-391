# MIPRO Implementation Roast 🔥

## TL;DR: This is WAY too complex for users

**The Problem**: Users have to construct 5+ nested config objects just to run a simple single-stage task like Iris. This is integration friction hell.

## The Crimes

### 1. **Module/Stage Complexity for Single-Stage Tasks** ❌

**What users have to do for Iris (single-stage task)**:
```python
config = MIPROConfig(
    ...
    modules=[
        MIPROModuleConfig(
            module_id="classifier",
            stages=[
                MIPROStageConfig(
                    stage_id="classifier_stage_0",
                    baseline_instruction=baseline_instruction,
                )
            ],
        )
    ],
)
```

**Why this is retarded**:
- Multi-stage should be **first-class** (✅ keep it!)
- But single-stage tasks shouldn't require **manual module/stage creation**
- Users should be able to use **simple API for single-stage**, **explicit API for multi-stage**

**What it should be**:
```python
# Single-stage (simple API - auto-creates default module/stage)
config = MIPROConfig.simple(
    ...
    baseline_instruction="Classify the input.",  # ✅ Auto-creates module/stage
)

# Multi-stage (explicit API - full control)
config = MIPROConfig(
    ...
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
```

### 2. **Seed Config Wrapper Hell** ❌

**What users have to do**:
```python
seeds=MIPROSeedConfig(
    bootstrap=[0, 1, 2],
    online=[10, 11, 12],
    test=[20, 21],
    reference=[],  # Why is this even here?
)
```

**Why this is retarded**:
- Users just want to pass **3 lists of integers**
- Why wrap them in a dataclass? Just use keyword args!
- `reference` is almost never used - why is it required?

**What it should be**:
```python
bootstrap_seeds=[0, 1, 2],
online_seeds=[10, 11, 12],
test_seeds=[20, 21],
# reference_seeds optional, defaults to []
```

### 3. **Meta Config Wrapper Hell** ❌

**What users have to do**:
```python
meta=MIPROMetaConfig(
    model="gpt-4o-mini",
    provider="openai",
    inference_url=None,  # Why is this even here?
)
```

**Why this is retarded**:
- Users just want to specify the **meta-model quality** (fast/balanced/high-quality)
- Why wrap it in a dataclass? Just use `meta_preset="balanced"`!
- `inference_url` is almost always `None` - why force users to specify it?
- `provider` can be **auto-detected** from model name
- `temperature` and `max_tokens` are **implementation details** - use preset defaults!

**What it should be**:
```python
# Simple: Use preset
meta_preset="balanced",  # ✅ "fast", "balanced", "high-quality"

# Advanced: Override preset
meta_preset="balanced",
meta_model="gpt-4o",  # Override preset model
# provider auto-detected, temperature/max_tokens use preset defaults
```

**See `META_MODEL_INVESTIGATION.md` for full explanation of why meta model config is necessary but should be abstracted.**

### 4. **Initial Prompt Config Duplication** ❌

**What users have to do**:
```python
config = MIPROConfig(...)  # Has initial_prompt_config somewhere?
optimizer = MIPROOptimizer(
    config=config,
    initial_prompt_config={  # ❌ Also passed separately!
        "messages": initial_prompt_messages,
    },
)
```

**Why this is retarded**:
- `initial_prompt_config` is passed **twice** - once in config, once to optimizer
- Why not just put it in the config?
- This is confusing and error-prone

**What it should be**:
```python
config = MIPROConfig(
    ...
    initial_prompt_messages=[...],  # ✅ Just this!
)
```

### 5. **No Budget-Based Auto-Scaling** ❌

**What users have to do**:
```python
# Users have to manually calculate seeds/iterations based on budget
def _get_default_bootstrap_seeds(self):
    if self.rollout_budget < 50:
        return list(range(5))
    elif self.rollout_budget < 100:
        return list(range(10))
    # ... 20 more lines of this garbage

def _get_num_iterations(self):
    if self.rollout_budget < 50:
        return 3
    elif self.rollout_budget < 100:
        return 5
    # ... more manual calculation
```

**Why this is retarded**:
- Users shouldn't have to **manually calculate** seeds/iterations based on budget
- MIPRO should **auto-scale** seeds/iterations based on `rollout_budget` **by default**
- But users should be able to **override explicitly** if they want beefy per-step budgets (even if it means stopping early)

**What it should be**:
```python
# Default: Auto-scale from budget
config = MIPROConfig(
    rollout_budget=400,  # ✅ Auto-calculates seeds/iterations/evaluations
    # bootstrap_seeds, online_seeds, num_iterations, num_evaluations_per_iteration auto-calculated
)

# Override: Explicit per-step budgets (respects rollout_budget as hard cap)
config = MIPROConfig(
    rollout_budget=400,  # Hard cap - stops early if exceeded
    num_iterations=20,  # ✅ Explicit override
    num_evaluations_per_iteration=10,  # ✅ Explicit override
    batch_size=32,  # ✅ Explicit override
    bootstrap_seeds=[0, 1, 2, 3, 4],  # ✅ Explicit override
    # MIPRO uses these values but stops when rollout_budget is hit
)
```

**How it works**:
- **Total rollouts** ≈ `len(bootstrap_seeds) + (num_iterations * num_evaluations_per_iteration * batch_size)`
- **Default**: Given `rollout_budget=400`, auto-calculate seeds/iterations/evaluations to fit
- **Override**: If user explicitly sets `num_iterations=20`, use it but stop early when budget hit

### 6. **Instruction Config Exposure** ❌

**What users have to do**:
```python
instructions=MIPROInstructionConfig(
    instructions_per_batch=10,
    max_instructions=1,
    duplicate_retry_limit=10,
)
```

**Why this is retarded**:
- These are **internal implementation details**
- Users shouldn't have to know about `instructions_per_batch` or `duplicate_retry_limit`
- These should have **sensible defaults** and be hidden from users
- But advanced users might want to override them

**What it should be**:
```python
# Default: Use sensible defaults (hidden)
config = MIPROConfig(
    ...
    # instructions config auto-created with defaults
)

# Advanced: Override if needed
config = MIPROConfig(
    ...
    instructions_per_batch=20,  # ✅ Optional override
    max_instructions=2,  # ✅ Optional override
    duplicate_retry_limit=15,  # ✅ Optional override
    # Or use MIPROInstructionConfig if you want full control
)
```

**How it works**:
- **Default**: `instructions_per_batch=10`, `max_instructions=1`, `duplicate_retry_limit=10` (sensible defaults)
- **Override**: Users can set individual fields or pass `MIPROInstructionConfig` for full control
- **Hidden**: Not exposed in simple API, but available for advanced users
- **Note**: These ARE used in production (see `banking77_pipeline` examples), so they're optimization hyperparameters, not just internal details

### 7. **TOML Parsing Complexity** ❌

**What the code does**:
```python
def parse_mipro_config(...):
    # 300+ lines of fallback logic
    bootstrap_seeds = mipro_section.get("bootstrap_train_seeds") or \
                     pl_config.get("bootstrap_train_seeds") or \
                     ...  # More fallbacks
    
    # Multiple fallback paths for every field
    # Inconsistent error handling
    # Hard to debug config issues
```

**Why this is retarded**:
- **300+ lines** just to parse config with fallbacks
- **Inconsistent fallback logic** - some fields check `mipro_section`, some check `pl_config`, some have defaults
- **No clear required vs optional** - hard to know what's needed
- **Hard to debug** - config errors are cryptic
- **No validation** - bad configs slip through silently

**What it should be**:
```python
@dataclass
class MIPROConfigFromTOML:
    """Single dataclass that parses TOML with explicit required/optional fields."""
    
    # REQUIRED fields (no defaults, explicit errors)
    task_app_url: str
    task_app_api_key: str
    bootstrap_train_seeds: list[int]
    
    # OPTIONAL fields (explicit defaults)
    online_pool: list[int] = field(default_factory=lambda: list(range(10, 50)))
    num_iterations: int = 10
    num_evaluations_per_iteration: int = 5
    batch_size: int = 5
    # ... etc
    
**What it should be**:
```python
@dataclass
class MIPROConfigFromTOML:
    """Single dataclass that parses TOML with explicit required/optional fields."""
    
    # REQUIRED fields (no defaults, explicit errors)
    task_app_url: str
    task_app_api_key: str
    bootstrap_train_seeds: list[int]
    
    # OPTIONAL fields (explicit defaults)
    online_pool: list[int] = field(default_factory=lambda: list(range(10, 50)))
    num_iterations: int = 10
    num_evaluations_per_iteration: int = 5
    batch_size: int = 5
    reference_pool: Optional[list[int]] = None  # ✅ Optional: used for rich meta-prompt context
    # ... etc
    
    @classmethod
    def from_toml(cls, toml_dict: dict, *, allow_legacy_format: bool = True) -> "MIPROConfigFromTOML":
        """Parse TOML with explicit validation and clear errors.
        
        Args:
            allow_legacy_format: If True, support old format (seeds at top level) for backward compatibility.
        """
        mipro_section = toml_dict.get("mipro", {})
        
        # REQUIRED fields - fail fast with clear errors
        if "task_app_url" not in mipro_section:
            raise MIPROConfigurationError("mipro.task_app_url is REQUIRED")
        
        # Backward compatibility: check top-level for seeds if not in mipro section
        if allow_legacy_format:
            bootstrap_seeds = mipro_section.get("bootstrap_train_seeds") or toml_dict.get("bootstrap_train_seeds", [])
        else:
            bootstrap_seeds = mipro_section.get("bootstrap_train_seeds", [])
        
        # OPTIONAL fields - use defaults
        return cls(
            task_app_url=mipro_section["task_app_url"],
            task_app_api_key=mipro_section.get("task_app_api_key", ""),
            bootstrap_train_seeds=bootstrap_seeds,
            online_pool=mipro_section.get("online_pool", list(range(10, 50))),
            reference_pool=mipro_section.get("reference_pool"),  # ✅ Optional: for rich meta-prompt context
            # ... etc
        )
    
    def to_mipro_config(self, task_app_url: str, task_app_api_key: str) -> MIPROConfig:
        """Convert to MIPROConfig with explicit defaults."""
        # Convert to MIPROConfig with all nested configs
        pass
```

**Unit Tests Needed**:
```python
# Test required fields
def test_missing_task_app_url():
    with pytest.raises(MIPROConfigurationError, match="task_app_url is REQUIRED"):
        MIPROConfigFromTOML.from_toml({"mipro": {}})

# Test invalid types
def test_invalid_bootstrap_seeds_type():
    with pytest.raises(MIPROConfigurationError, match="bootstrap_train_seeds must be a list"):
        MIPROConfigFromTOML.from_toml({"mipro": {"bootstrap_train_seeds": "not a list"}})

# Test defaults
def test_defaults_applied():
    config = MIPROConfigFromTOML.from_toml({"mipro": {"task_app_url": "http://..."}})
    assert config.num_iterations == 10  # Default
    assert config.online_pool == list(range(10, 50))  # Default

# Test edge cases
def test_empty_toml():
    with pytest.raises(MIPROConfigurationError):
        MIPROConfigFromTOML.from_toml({})

def test_missing_mipro_section():
    with pytest.raises(MIPROConfigurationError):
        MIPROConfigFromTOML.from_toml({"policy": {}})

# Test bad configs
def test_negative_iterations():
    with pytest.raises(MIPROConfigurationError, match="num_iterations must be positive"):
        MIPROConfigFromTOML.from_toml({"mipro": {"num_iterations": -1}})

def test_invalid_spec_dict():
    with pytest.raises(MIPROConfigurationError, match="spec must be a dict"):
        MIPROConfigFromTOML.from_toml({"mipro": {"spec": "not a dict"}})

# ... 50+ more test cases for edge cases, bad configs, type errors, etc.
```

**Benefits**:
- **Single source of truth** - one dataclass, clear required/optional
- **Explicit defaults** - no magic fallbacks
- **Clear errors** - "field X is REQUIRED" not "NoneType has no attribute"
- **Easy to test** - unit tests catch bad configs early
- **Easy to debug** - validation errors point to exact field
- **Migration path** - support BOTH old format (seeds at top level) and new format (seeds in `[mipro]` section) during transition

### 8. **Spec Config Fields** ❌

**What users see**:
```python
spec_path: Optional[str] = None
spec_max_tokens: int = 5000
spec_include_examples: bool = True
spec_priority_threshold: Optional[int] = None
```

**Why this is retarded**:
- **99% of users don't use specs** - why pollute the config?
- **File path instead of spec object** - requires file I/O, harder to test
- **Scattered fields** - spec config spread across 4 fields
- **No validation** - if user uses judges, specs should be REQUIRED

**What it should be**:
```python
@dataclass
class MIPROSpecConfig:
    """First-class spec configuration (optional but required if using judges)."""
    spec: dict  # ✅ spec.to_dict() not file path
    max_tokens: int = 5000
    include_examples: bool = True
    priority_threshold: Optional[int] = None

# In MIPROConfig:
spec: Optional[MIPROSpecConfig] = None  # ✅ Optional, but required if using judges

# Validation:
if use_judges and spec is None:
    raise MIPROConfigurationError("spec is REQUIRED when using judges")
```

**How it works**:
- **Optional by default** - most users don't need specs
- **First-class when used** - `spec.to_dict()` passed directly, not file path
- **Required with judges** - if `use_judges=True`, `spec` must be provided
- **Clean API** - all spec config in one place

## The Fix: Simplified API

### Current (Complex):
```python
config = MIPROConfig(
    task_app_url="http://127.0.0.1:8115",
    task_app_api_key=api_key,
    env_name="iris",
    seeds=MIPROSeedConfig(
        bootstrap=[0, 1, 2],
        online=[10, 11, 12],
        test=[20, 21],
    ),
    num_iterations=10,
    num_evaluations_per_iteration=5,
    batch_size=32,
    max_concurrent=10,
    policy_config={"model": "gpt-oss-20b", ...},
    meta=MIPROMetaConfig(
        model="gpt-4o-mini",
        provider="openai",
        inference_url=None,
    ),
    instructions=MIPROInstructionConfig(...),
    modules=[
        MIPROModuleConfig(
            module_id="classifier",
            stages=[
                MIPROStageConfig(
                    stage_id="classifier_stage_0",
                    baseline_instruction="Classify the input.",
                )
            ],
        )
    ],
)
```

### Proposed (Simple for Single-Stage):
```python
# Single-stage: Simple API
config = MIPROConfig.simple(
    task_app_url="http://127.0.0.1:8115",
    task_app_api_key=api_key,
    env_name="iris",
    
    # Seeds (simple lists, not wrapped)
    bootstrap_seeds=[0, 1, 2],
    online_seeds=[10, 11, 12],
    test_seeds=[20, 21],
    
    # Budget-based auto-scaling (default)
    rollout_budget=400,  # Auto-calculates seeds/iterations/evaluations
    
    # OR explicit overrides (respects rollout_budget as hard cap)
    # num_iterations=20,  # Override if you want beefy per-step budgets
    # num_evaluations_per_iteration=10,  # Override if you want more evaluations
    # bootstrap_seeds=[0, 1, 2, 3, 4],  # Override if you want specific seeds
    
    # Initial prompt (simple, not nested)
    initial_prompt_messages=[
        {"role": "system", "pattern": "Classify the input."},
        {"role": "user", "pattern": "{features}"},
    ],
    
    # Policy (simple dict)
    policy_config={"model": "gpt-oss-20b", ...},
    
    # Meta-model (simple string)
    meta_model="gpt-4o-mini",  # Auto-detects provider
    
    # Auto-creates: modules=[MIPROModuleConfig(module_id="default", stages=[...])]
)

# Multi-stage: Explicit API (full control)
config = MIPROConfig(
    task_app_url="http://127.0.0.1:8115",
    task_app_api_key=api_key,
    env_name="hotpotqa",
    bootstrap_seeds=[0, 1, 2],
    online_seeds=[10, 11, 12],
    rollout_budget=400,
    meta_model="gpt-4o-mini",
    policy_config={"model": "gpt-oss-20b", ...},
    modules=[
        MIPROModuleConfig(
            module_id="retriever",
            stages=[
                MIPROStageConfig(
                    stage_id="retrieve_stage",
                    baseline_instruction="Retrieve relevant passages.",
                )
            ],
        ),
        MIPROModuleConfig(
            module_id="answerer",
            stages=[
                MIPROStageConfig(
                    stage_id="answer_stage",
                    baseline_instruction="Answer the question.",
                )
            ],
        ),
    ],
)
```

### 9. **Missing Reference Pools** ⚠️

**What we missed**:
- Reference pools ARE used in production (`banking77_pipeline` examples)
- They provide rich dataset context (~50k tokens) for meta-prompts
- They're a real feature, not just internal

**What it should be**:
```python
config = MIPROConfig.simple(
    ...
    reference_pool: Optional[list[int]] = None,  # ✅ Optional: for rich meta-prompt context
    # Auto-calculate from rollout_budget if not provided
)
```

**How it works**:
- **Optional by default** - most users don't need it
- **Auto-calculate** - if not provided, calculate from `rollout_budget`
- **Used for meta-prompts** - provides rich dataset context for instruction generation

## Key Principles

1. **Multi-stage first-class**: Full support for complex pipelines (✅ keep modules/stages!) - **NOT rare, core production feature**
2. **Simple API for single-stage**: Auto-create default module/stage for simple tasks
3. **Simple types**: Use lists/dicts/strings where possible, not nested dataclasses
4. **Budget-based auto-scaling**: Default auto-calculate from `rollout_budget`, allow explicit overrides
5. **Sensible defaults**: Hide internal implementation details (but expose for overrides)
6. **Explicit overrides**: Users can set beefy per-step budgets or instruction config (stops early when budget hit)
7. **Explicit over implicit**: Clear errors, no magic fallbacks
8. **Single dataclass for TOML parsing**: Explicit required/optional fields, clear validation, tons of unit tests, **backward compatibility during migration**
9. **Specs first-class but optional**: Use `spec.to_dict()` not file path, required if using judges
10. **Reference pools optional**: Auto-calculate from `rollout_budget` if not provided, used for rich meta-prompt context

## Migration Path

1. **Add `MIPROConfig.simple()` constructor**:
   ```python
   @classmethod
   def simple(
       cls,
       task_app_url: str,
       task_app_api_key: str,
       env_name: str,
       rollout_budget: int,  # ✅ Default: auto-scales everything
       initial_prompt_messages: list[dict],
       bootstrap_seeds: Optional[list[int]] = None,  # ✅ Override if needed
       online_seeds: Optional[list[int]] = None,  # ✅ Override if needed
       test_seeds: Optional[list[int]] = None,
       reference_pool: Optional[list[int]] = None,  # ✅ Optional: for rich meta-prompt context
       num_iterations: Optional[int] = None,  # ✅ Override if you want beefy budgets
       num_evaluations_per_iteration: Optional[int] = None,  # ✅ Override if needed
       batch_size: Optional[int] = None,  # ✅ Override if needed
       meta_preset: str = "balanced",  # ✅ High-level preset
       # Instruction config (optional overrides)
       instructions_per_batch: Optional[int] = None,  # ✅ Override if needed
       max_instructions: Optional[int] = None,  # ✅ Override if needed
       duplicate_retry_limit: Optional[int] = None,  # ✅ Override if needed
       policy_config: Optional[dict] = None,
       # Spec config (optional, but required if using judges)
       spec: Optional[dict] = None,  # ✅ spec.to_dict() not file path
       spec_max_tokens: Optional[int] = None,  # ✅ Override if needed
       spec_include_examples: Optional[bool] = None,  # ✅ Override if needed
       spec_priority_threshold: Optional[int] = None,  # ✅ Override if needed
       use_judges: bool = False,  # ✅ If True, spec is REQUIRED
       **kwargs
   ) -> MIPROConfig:
       """Simple constructor for single-stage tasks.
       
       Auto-creates default module/stage, auto-scales seeds/iterations from rollout_budget.
       Explicit overrides respected (but rollout_budget is hard cap - stops early if exceeded).
       Instruction config uses sensible defaults but can be overridden.
       Specs are optional but required if using judges.
       """
       # Validate: if use_judges=True, spec must be provided
       if use_judges and spec is None:
           raise MIPROConfigurationError("spec is REQUIRED when use_judges=True")
       
       # Auto-scale seeds/iterations from rollout_budget (if not overridden)
       # Auto-create: modules=[MIPROModuleConfig(module_id="default", stages=[...])]
       # Extract baseline_instruction from initial_prompt_messages
       # Use sensible defaults for instruction config (but allow overrides)
       # Create MIPROSpecConfig from spec dict if provided
       
       # Budget calculation:
       # total_rollouts ≈ len(bootstrap_seeds) + (num_iterations * num_evaluations_per_iteration * batch_size)
       # If explicit overrides exceed budget, use them but stop early when budget hit
   ```

2. **Keep full `MIPROConfig()` constructor** for multi-stage tasks (no changes needed)

3. **Update adapters** to use `MIPROConfig.simple()` for single-stage tasks

## Bottom Line

**Current**: Users need to understand seed configs, meta configs, instruction configs, module/stage creation, and 20+ parameters just to run Iris (single-stage).

**Proposed**: 
- **Single-stage**: Use `MIPROConfig.simple()` - pass `task_app_url`, `rollout_budget`, `initial_prompt_messages`, maybe `meta_preset`. That's it.
- **Multi-stage**: Use full `MIPROConfig()` - explicit modules/stages (first-class support!) - **NOT rare, core production feature**
- **Budget handling**: Default auto-scales from `rollout_budget`, but explicit overrides allowed (stops early when budget hit)
- **Advanced features**: TPE, Demo, Grounding, Meta-Update configs remain EXPOSABLE for advanced users (hidden by default, but available)

**Multi-stage stays first-class (it's NOT rare - it's core production), but single-stage shouldn't require understanding the full architecture. Budget auto-scaling is default, but users can override for beefy per-step budgets. Advanced features (TPE, Demo, Grounding, Meta-Update) remain exposable but hidden by default.**

