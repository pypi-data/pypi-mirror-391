# MIPRO/GEPA Roast Review: Real-World Usage Analysis

## Purpose
Review actual MIPRO and GEPA implementations to ensure our criticisms are accurate and we're not planning to remove logic that's critical for real applications.

## Key Findings

### ✅ **What We Got RIGHT**

1. **Single-stage should be simpler** ✅
   - Real examples show single-stage tasks (Iris, Banking77 single-stage) require full nested config
   - Our `MIPROConfig.simple()` proposal is valid

2. **Budget-based auto-scaling** ✅
   - Real examples manually calculate seeds/iterations based on budget
   - Auto-scaling would help (but allow overrides)

3. **Specs should be first-class but optional** ✅
   - Specs ARE used (banking77_pipeline examples)
   - But they're optional (most tasks don't use them)
   - Our proposal to use `spec.to_dict()` instead of file path is good

4. **TOML parsing needs cleanup** ✅
   - 300+ lines of fallback logic is real
   - Single dataclass with explicit required/optional would help

### ⚠️ **What We Might Have Been TOO HARSH On**

#### 1. **Multi-Stage IS First-Class (We're Right, But Need to Emphasize)**

**Real Usage:**
- `banking77_pipeline_mipro_local.toml` - 2-stage pipeline (classifier → calibrator)
- `run_local_mipro_pipeline.sh` - Multi-stage MIPRO config
- `run_local_gepa.py` - Multi-stage GEPA with `stages` config
- `multi_stage_gepa_example.toml` - Full multi-stage example

**Our Proposal:**
- ✅ Keep full `MIPROConfig()` for multi-stage (correct)
- ✅ `MIPROConfig.simple()` for single-stage (correct)
- ✅ Multi-stage remains first-class (correct)

**Verdict:** We're correct, but need to emphasize multi-stage is NOT rare - it's a core production feature.

#### 2. **Nested Configs ARE Used (TPE, Demo, Grounding, Meta-Update)**

**Real Usage:**
```toml
[prompt_learning.mipro.tpe]
gamma = 0.25
n_candidates = 32
n_startup_trials = 10

[prompt_learning.mipro.demo]
max_few_shot_examples = 5
sets_per_size = 6

[prompt_learning.mipro.grounding]
n = 10
temperature = 0.7

[prompt_learning.mipro.meta_update]
enabled = true
every_iterations = 3
```

**Our Criticism:**
- We said these are "internal implementation details"
- We said users shouldn't need to know about them

**Reality:**
- These ARE used in production configs
- Users DO tune these parameters
- They're NOT just internal - they're optimization hyperparameters

**Verdict:** We were TOO HARSH. These should:
- ✅ Have sensible defaults
- ✅ Be hidden in simple API
- ✅ But still be EXPOSABLE for advanced users (which we said, but need to emphasize)

#### 3. **Instruction Config IS Tuned**

**Real Usage:**
```python
instructions=MIPROInstructionConfig(
    instructions_per_batch=3,  # Tuned from default 10
    max_instructions=5,  # Tuned from default 1
    duplicate_retry_limit=10,  # Tuned from default 10
)
```

**Our Criticism:**
- We said these are "internal implementation details"
- We said users shouldn't need to know about them

**Reality:**
- Users DO tune these (see test_local_execution.py)
- They affect optimization behavior
- They're optimization hyperparameters, not just internal

**Verdict:** We were PARTIALLY RIGHT:
- ✅ Should have sensible defaults
- ✅ Should be hidden in simple API
- ✅ But should be EXPOSABLE for advanced users (which we said)

#### 4. **Reference Pools ARE Used**

**Real Usage:**
```toml
# Reference pool: Used to generate rich dataset context (~50k tokens) in the meta-prompt
reference_pool = [50, 51, 52, ..., 149]  # 100 seeds for rich context
```

**Our Criticism:**
- We didn't mention reference pools in our roast

**Reality:**
- Reference pools ARE used for rich meta-prompt context
- They're a real feature, not just internal

**Verdict:** We MISSED this. Reference pools should:
- ✅ Be optional (default: None)
- ✅ Be exposable in simple API
- ✅ Auto-calculate from rollout_budget if not provided

#### 5. **TOML Fallback Logic EXISTS for Backward Compatibility**

**Real Usage:**
```python
bootstrap_seeds = mipro_section.get("bootstrap_train_seeds") or \
                 pl_config.get("bootstrap_train_seeds") or \
                 ...  # More fallbacks
```

**Our Criticism:**
- We said this is "retarded" and should be removed

**Reality:**
- Fallback logic exists because:
  - Old configs have seeds at top level
  - New configs have seeds in `[prompt_learning.mipro]` section
  - Backward compatibility is important

**Verdict:** We were PARTIALLY RIGHT:
- ✅ Single dataclass with explicit required/optional is better
- ✅ But need migration path for backward compatibility
- ✅ Can deprecate old format gradually

#### 6. **Initial Prompt Config Duplication**

**Real Usage:**
```python
config = MIPROConfig(...)
optimizer = MIPROOptimizer(
    config=config,
    initial_prompt_config={  # ✅ Passed separately
        "messages": self.initial_prompt_messages,
    },
)
```

**Our Criticism:**
- We said `initial_prompt_config` is passed twice (once in config, once to optimizer)

**Reality:**
- It IS passed separately to optimizer
- But config doesn't have `initial_prompt_config` field
- It's extracted from `initial_prompt_messages` in modules/stages

**Verdict:** We were PARTIALLY RIGHT:
- ✅ There IS duplication (extract from modules vs pass separately)
- ✅ But it's not exactly what we said (config doesn't have the field)
- ✅ Should be unified: either in config OR passed separately, not both

## Updated Recommendations

### 1. **Multi-Stage: Keep First-Class** ✅
- Full `MIPROConfig()` for multi-stage (no changes)
- `MIPROConfig.simple()` for single-stage (new)
- Emphasize multi-stage is NOT rare - it's core production feature

### 2. **Nested Configs: Sensible Defaults + Exposable** ✅
- TPE, Demo, Grounding, Meta-Update should have defaults
- Hidden in simple API
- But EXPOSABLE for advanced users (which we said)

### 3. **Instruction Config: Sensible Defaults + Exposable** ✅
- `instructions_per_batch`, `max_instructions`, `duplicate_retry_limit` have defaults
- Hidden in simple API
- But EXPOSABLE for advanced users (which we said)

### 4. **Reference Pools: Add to Simple API** ⚠️
- Optional parameter in `MIPROConfig.simple()`
- Auto-calculate from `rollout_budget` if not provided
- Used for rich meta-prompt context

### 5. **TOML Parsing: Single Dataclass + Migration Path** ✅
- Single `MIPROConfigFromTOML` dataclass
- Explicit required/optional fields
- But support BOTH old and new formats during migration
- Deprecate old format gradually

### 6. **Initial Prompt Config: Unify** ✅
- Either in config OR passed separately, not both
- Prefer: extract from `modules`/`stages` in config
- Remove `initial_prompt_config` parameter from optimizer

## Conclusion

**Our criticisms were MOSTLY CORRECT**, but we need to:

1. ✅ **Emphasize multi-stage is NOT rare** - it's core production feature
2. ✅ **Clarify nested configs are EXPOSABLE** - not removed, just hidden by default
3. ✅ **Add reference pools** - we missed this feature
4. ✅ **Provide migration path** - for TOML parsing backward compatibility
5. ✅ **Unify initial prompt config** - remove duplication

**Overall:** Our proposed simplifications are valid, but we need to ensure:
- Multi-stage remains first-class (✅ we said this)
- Advanced features remain exposable (✅ we said this)
- Backward compatibility is maintained (⚠️ we need to add this)

