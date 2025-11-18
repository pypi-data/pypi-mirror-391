# Meta Model Configuration: Investigation & Explanation

## What is the Meta Model?

**Purpose**: The meta-model is an LLM used to **generate instruction proposals** for optimization.

### MIPRO's Meta Model Usage

**What it does**:
1. Takes a **meta-prompt** containing:
   - Dataset summary (what the task is)
   - Program summary (what the pipeline does)
   - Baseline instruction (current prompt)
   - Few-shot examples (high-scoring demonstrations)
   - Optimization tips (best practices)
   - System spec context (optional)

2. Generates **instruction variants** (JSON proposals):
   ```json
   {
     "instructions": [
       "Be concise and direct",
       "Encourage tool usage when appropriate",
       "Highlight the expected classification labels"
     ],
     "demo_seeds": [0, 1, 2]
   }
   ```

3. These proposals are then **evaluated** via rollouts and **selected** by TPE (Bayesian optimization)

**Code location**: `_generate_stage_instruction_batch()` → `_call_meta_model()` → `_render_stage_meta_prompt()`

### GEPA's Mutation LLM (Similar Concept)

**What it does**:
- **Optional** LLM-guided mutations (can use regex-only)
- Takes current prompt + execution traces
- Generates **mutated prompt variants**
- Different from MIPRO: evolutionary mutations vs. instruction proposals

**Config**: `mutation_llm_model`, `mutation_llm_provider`, `mutation_llm_inference_url`

## Current Meta Model Parameters

### MIPRO: `MIPROMetaConfig`

```python
@dataclass
class MIPROMetaConfig:
    model: str = "gpt-4o-mini"           # Which LLM to use
    provider: str = "openai"              # Which provider
    inference_url: Optional[str] = None   # Custom inference URL (rarely used)
    temperature: float = 0.3              # Generation temperature
    max_tokens: int = 600                 # Max tokens per proposal
```

**Why each parameter exists**:
1. **`model`**: Different models have different:
   - Quality (gpt-4o-mini vs gpt-4o vs gpt-oss-120b)
   - Cost (gpt-4o-mini is cheap, gpt-4o is expensive)
   - Speed (Groq models are fast, OpenAI can be slower)
   - Capabilities (some models better at instruction generation)

2. **`provider`**: Determines:
   - API endpoint (OpenAI vs Groq vs custom)
   - Authentication method
   - Rate limits

3. **`inference_url`**: For custom endpoints (rarely needed, usually None)

4. **`temperature`**: Controls creativity:
   - Lower (0.1-0.3): More focused, deterministic proposals
   - Higher (0.7-1.0): More diverse, creative proposals
   - Default 0.3 is conservative (good for instruction generation)

5. **`max_tokens`**: Limits proposal length:
   - Too low: Truncated proposals
   - Too high: Wasted tokens
   - Default 600 is reasonable for instruction proposals

## The Problem: Low-Level vs High-Level Configuration

### Current State (Low-Level)

**Users configure**:
```python
meta=MIPROMetaConfig(
    model="gpt-4o-mini",        # ❌ Low-level: specific model name
    provider="openai",           # ❌ Low-level: specific provider
    inference_url=None,         # ❌ Low-level: rarely used
    temperature=0.3,             # ❌ Low-level: implementation detail
    max_tokens=600,              # ❌ Low-level: implementation detail
)
```

**Issues**:
- Users need to know **which models exist** and **which are good**
- Users need to understand **temperature** and **max_tokens** (implementation details)
- **Provider** is usually obvious from model name (can auto-detect)
- **inference_url** is almost always None (why expose it?)

### Proposed State (High-Level Menu)

**Users configure**:
```python
meta_preset="balanced"  # ✅ High-level: "fast", "balanced", "high-quality"
# OR
meta_preset="custom",
meta_model="gpt-4o-mini",  # Only if custom
```

**Backend maps**:
```python
META_PRESETS = {
    "fast": MIPROMetaConfig(
        model="openai/gpt-oss-20b",  # Groq = fast
        provider="groq",
        temperature=0.3,
        max_tokens=400,  # Shorter = faster
    ),
    "balanced": MIPROMetaConfig(
        model="gpt-4o-mini",  # Good balance
        provider="openai",
        temperature=0.3,
        max_tokens=600,
    ),
    "high-quality": MIPROMetaConfig(
        model="gpt-4o",  # Best quality
        provider="openai",
        temperature=0.2,  # More focused
        max_tokens=800,  # Longer proposals
    ),
}
```

## Why Config is Still Necessary

### 1. **Future Options Will Be Exposed**

**Planned additions**:
- **Custom meta-prompts**: Users might want to customize the instruction generation prompt
- **Multi-model ensembling**: Use multiple meta-models and combine proposals
- **Model-specific tuning**: Different temperature/max_tokens per model
- **Cost optimization**: Auto-select cheapest model that meets quality threshold

**Config structure needed**:
```python
@dataclass
class MIPROMetaConfig:
    # Preset-based (simple)
    preset: str = "balanced"  # "fast", "balanced", "high-quality"
    
    # Custom overrides (advanced)
    model: Optional[str] = None  # Override preset model
    provider: Optional[str] = None  # Override preset provider
    temperature: Optional[float] = None  # Override preset temperature
    max_tokens: Optional[int] = None  # Override preset max_tokens
    
    # Future options
    custom_prompt_template: Optional[str] = None
    ensemble_models: Optional[List[str]] = None
    cost_threshold_usd: Optional[float] = None
```

### 2. **Different Optimizers Have Variation**

**MIPRO**:
- Uses meta-model for **instruction proposals**
- Needs: `model`, `provider`, `temperature`, `max_tokens`
- Default: `gpt-4o-mini` (balanced quality/cost)

**GEPA**:
- Uses mutation LLM for **prompt mutations** (optional)
- Needs: `mutation_llm_model`, `mutation_llm_provider`, `mutation_llm_inference_url`
- Default: `None` (regex-only mutations)
- Different purpose: evolutionary mutations vs. instruction proposals

**Future optimizers**:
- Might use meta-model for **different purposes**
- Might need **different parameters**
- Config structure needs to be **extensible**

## Recommended Approach

### 1. **Preset-Based API (Simple)**

```python
# Simple: Use preset
config = MIPROConfig.simple(
    ...
    meta_preset="balanced",  # ✅ High-level choice
)

# Advanced: Custom override
config = MIPROConfig.simple(
    ...
    meta_preset="balanced",
    meta_model="gpt-4o",  # Override preset model
    meta_temperature=0.2,  # Override preset temperature
)
```

### 2. **Backend Implementation**

```python
@dataclass
class MIPROMetaConfig:
    preset: str = "balanced"
    model: Optional[str] = None
    provider: Optional[str] = None
    inference_url: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    
    def __post_init__(self):
        # Load preset defaults
        preset_config = META_PRESETS.get(self.preset, META_PRESETS["balanced"])
        
        # Apply overrides
        self.model = self.model or preset_config.model
        self.provider = self.provider or preset_config.provider
        self.temperature = self.temperature if self.temperature is not None else preset_config.temperature
        self.max_tokens = self.max_tokens if self.max_tokens is not None else preset_config.max_tokens
        
        # Auto-detect provider from model name if not set
        if not self.provider:
            self.provider = _detect_provider_from_model(self.model)
        
        # Validate
        _validate_model_for_provider(self.model, self.provider, ...)
```

### 3. **Menu Options (Future UI)**

**Simple users**:
- Choose from dropdown: "Fast", "Balanced", "High Quality"
- Backend maps to appropriate model/config

**Advanced users**:
- Toggle "Advanced Options"
- See: model, provider, temperature, max_tokens
- Can override preset values

## Current State Analysis

### What's Actually Used

**Common patterns**:
1. **Default**: `gpt-4o-mini` (OpenAI) - most common
2. **Fast**: `openai/gpt-oss-120b` (Groq) - for speed
3. **Quality**: `gpt-4o` (OpenAI) - for best results

**Rarely changed**:
- `inference_url`: Almost always `None`
- `temperature`: Usually `0.3` (default)
- `max_tokens`: Usually `600` (default)

### What Should Be Exposed

**✅ Should expose**:
- `meta_preset`: "fast", "balanced", "high-quality" (high-level choice)
- `meta_model`: Optional override (for advanced users)

**❌ Should hide**:
- `provider`: Auto-detect from model name
- `inference_url`: Almost never used, hide unless needed
- `temperature`: Use preset defaults, only expose if advanced
- `max_tokens`: Use preset defaults, only expose if advanced

## Comparison: MIPRO vs GEPA

| Aspect | MIPRO | GEPA |
|--------|-------|------|
| **Purpose** | Instruction proposals | Prompt mutations |
| **Required?** | ✅ Yes (core to algorithm) | ❌ Optional (can use regex-only) |
| **Config** | `MIPROMetaConfig` | `mutation_llm_model`, `mutation_llm_provider` |
| **Default** | `gpt-4o-mini` | `None` (regex-only) |
| **Parameters** | model, provider, temperature, max_tokens | model, provider, inference_url |
| **Complexity** | More parameters (5) | Fewer parameters (3) |

**Key difference**: MIPRO **requires** meta-model, GEPA can work without it.

## Recommendations

### Short-Term (Keep Config, Add Presets)

```python
@dataclass
class MIPROMetaConfig:
    # High-level preset (new)
    preset: str = "balanced"  # "fast", "balanced", "high-quality"
    
    # Low-level overrides (keep for advanced users)
    model: Optional[str] = None
    provider: Optional[str] = None
    inference_url: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    
    def __post_init__(self):
        # Load preset, apply overrides, auto-detect provider
        ...
```

### Long-Term (Menu-Based UI)

**UI Flow**:
1. **Simple mode**: Choose preset from dropdown
2. **Advanced mode**: Toggle to see model/provider/temperature/max_tokens
3. **Custom mode**: Full control for power users

**Backend**: Config structure stays the same, UI abstracts complexity

## Bottom Line

**Current problem**: Users configure low-level details (`model="gpt-4o-mini"`, `provider="openai"`, `temperature=0.3`) that should be abstracted.

**Solution**: 
- **Preset-based API**: `meta_preset="balanced"` (simple)
- **Config structure**: Keep for future options and optimizer variation (necessary)
- **Auto-detection**: Provider from model name, sensible defaults
- **Menu abstraction**: UI exposes presets, hides low-level details

**Config is necessary** because:
1. Future options will be exposed (custom prompts, ensembling, etc.)
2. Different optimizers have variation (MIPRO vs GEPA)
3. Advanced users need overrides

**But users shouldn't need to know**:
- Specific model names (use presets)
- Provider (auto-detect)
- Temperature/max_tokens (use preset defaults)
- inference_url (hide unless needed)

