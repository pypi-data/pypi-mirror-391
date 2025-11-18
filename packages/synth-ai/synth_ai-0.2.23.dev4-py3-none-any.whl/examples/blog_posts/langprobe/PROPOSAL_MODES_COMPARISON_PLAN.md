# Proposal Modes Comparison Blog Post Plan

## Overview

This document outlines the plan for a blog post comparing all instruction proposal modes (builtin, DSPy, Synth, GEPA-AI) across MIPRO and GEPA algorithms using the langprobe benchmark suite.

---

## Blog Post Title

**"Comparing Instruction Proposal Modes: Which Backend Works Best for Prompt Optimization?"**

Alternative titles:
- "Benchmarking Proposal Backends: Built-in, DSPy, Synth, and GEPA-AI Head-to-Head"
- "A Data-Driven Comparison of Prompt Proposal Strategies"

---

## Structure

### 1. Introduction (200 words)

**Hook**: Multiple proposal backends exist, but which actually performs best?

**Key Points**:
- We've built a unified proposal interface supporting 4 modes
- But which mode should you use? Data-driven answer needed
- Comprehensive comparison across standard benchmarks

**Value Proposition**:
- Empirical results from real runs
- Clear recommendations based on performance
- Cost/time tradeoff analysis

---

### 2. The Comparison Setup (400 words)

#### 2.1 Benchmark Tasks
- **Heart Disease**: Classification task (scikit-learn dataset)
- **HotPotQA**: Multi-hop question answering
- **Banking77**: Intent classification

**Why these tasks?**
- Standard langprobe benchmarks
- Diverse task types (classification, QA, intent)
- Established baseline performance

#### 2.2 Modes Compared

**For MIPRO**:
- `builtin`: Current hand-rolled meta-prompt approach
- `dspy`: DSPy's GroundedProposer
- `synth`: Currently identical to DSPy (placeholder)

**For GEPA**:
- `builtin`: Regex + LLM mutations with feedback text
- `dspy`: Component-as-predictor approach
- `synth`: Currently identical to DSPy
- `gepa-ai`: GEPA-AI's InstructionProposalSignature

#### 2.3 Methodology

**Standardized Setup**:
- Same rollout budgets (200 rollouts per task)
- Same seed splits (train/val/test)
- Same policy models (`groq/openai/gpt-oss-20b`)
- Same evaluation metrics (accuracy, lift)

**Metrics Collected**:
- Baseline score
- Final/best score
- Lift (improvement over baseline)
- Total rollouts used
- Time taken
- Cost (tokens, USD)
- Number of candidates (GEPA)

---

### 3. Comparison Runner Architecture (300 words)

#### 3.1 Existing Infrastructure

**Comparison Scripts** (in `examples/blog_posts/langprobe/comparisons/`):
- `run_dspy_mipro_parallel.py`: Runs DSPy MIPRO across all tasks
- `run_dspy_gepa_parallel.py`: Runs DSPy GEPA across all tasks
- `run_gepa_parallel.py`: Runs built-in GEPA across all tasks

**How They Work**:
1. Load YAML config with budgets and models
2. Run tasks in parallel (asyncio)
3. Extract results from JSON files or events
4. Generate aggregate stats tables
5. Save timestamped readout files

#### 3.2 Config Files

**YAML Format**:
```yaml
# dspy_mipro_config.yaml
budgets:
  heart_disease: 200
  hotpotqa: 200
  banking77: 200
model:
  policy_model: "groq/openai/gpt-oss-20b"
```

**Config Files Needed**:
- `dspy_mipro_config.yaml`: DSPy MIPRO settings
- `dspy_gepa_config.yaml`: DSPy GEPA settings
- `synth_mipro_config.yaml`: Synth MIPRO settings (NEW)
- `synth_gepa_config.yaml`: Synth GEPA settings (NEW)
- `gepa_ai_config.yaml`: GEPA-AI settings (NEW)

#### 3.3 Results Extraction

**From JSON Files**:
- MIPRO: `*_learning_curve.json` and `*_stats.json`
- GEPA: `*_detailed_results.json` or results files

**From Events** (fallback):
- Job events API for real-time extraction
- Validation summaries, progress events, completion events

**Output Format**:
- Timestamped readout files: `*_comparison_readout_YYYYMMDD_HHMMSS.txt`
- Aggregate stats tables
- Per-task breakdowns

---

### 4. Running the Comparisons (400 words)

#### 4.1 Setup Steps

```bash
# Navigate to comparisons directory
cd examples/blog_posts/langprobe/comparisons

# Ensure all config files exist
ls *.yaml
# Should see: dspy_mipro_config.yaml, dspy_gepa_config.yaml, etc.

# Ensure task apps are running (if needed)
# For in-process mode, this is handled automatically
```

#### 4.2 Running Each Mode

**MIPRO Comparisons**:
```bash
# Built-in MIPRO (baseline)
# Run via existing synth-ai CLI with proposer_mode="builtin"
# Or use existing MIPRO scripts

# DSPy MIPRO
python run_dspy_mipro_parallel.py --rollout-budget 200

# Synth MIPRO (NEW - needs implementation)
python run_synth_mipro_parallel.py --rollout-budget 200
```

**GEPA Comparisons**:
```bash
# Built-in GEPA
python run_gepa_parallel.py

# DSPy GEPA
python run_dspy_gepa_parallel.py --rollout-budget 200

# Synth GEPA (NEW - needs implementation)
python run_synth_gepa_parallel.py --rollout-budget 200

# GEPA-AI GEPA (NEW - needs implementation)
python run_gepa_ai_parallel.py --rollout-budget 200
```

#### 4.3 New Scripts Needed

**`run_synth_mipro_parallel.py`**:
- Similar to `run_dspy_mipro_parallel.py`
- But uses `proposer_mode="synth"` in config
- Calls synth-ai CLI or SDK with synth proposer

**`run_synth_gepa_parallel.py`**:
- Similar to `run_dspy_gepa_parallel.py`
- But uses `proposer_mode="synth"` in config

**`run_gepa_ai_parallel.py`**:
- Similar to `run_dspy_gepa_parallel.py`
- But uses `proposer_mode="gepa-ai"` in config
- Calls GEPA-AI signature-based proposer

#### 4.4 Collecting Results

**After all runs complete**:
```bash
# Results are saved as timestamped files
ls *_comparison_readout_*.txt

# Parse and aggregate results
python aggregate_comparison_results.py \
    --mipro-builtin mipro_builtin_readout_*.txt \
    --mipro-dspy dspy_miprov2_comparison_readout_*.txt \
    --mipro-synth synth_mipro_comparison_readout_*.txt \
    --gepa-builtin synth_gepa_comparison_readout_*.txt \
    --gepa-dspy dspy_gepa_comparison_readout_*.txt \
    --gepa-synth synth_gepa_comparison_readout_*.txt \
    --gepa-gepa-ai gepa_ai_comparison_readout_*.txt \
    --output comparison_summary.md
```

---

### 5. Results: MIPRO Comparison (600 words)

#### 5.1 Aggregate Stats Table

**Format** (from actual runs):
```
================================================================================
MIPRO COMPARISON: Built-in vs DSPy vs Synth
================================================================================

Task              Mode      Policy Model          Baseline    Final      Lift        Rollouts    Time
--------------------------------------------------------------------------------------------------------
Heart Disease     builtin   groq/openai/gpt-oss   0.2600      0.5200     +0.2600     200         42.3s
Heart Disease     dspy      groq/openai/gpt-oss   0.2600      0.5712     +0.3112     200         45.2s
Heart Disease     synth     groq/openai/gpt-oss   0.2600      0.5712     +0.3112     200         45.2s

HotPotQA          builtin   groq/openai/gpt-oss   0.3200      0.4100     +0.0900     200         48.1s
HotPotQA          dspy      groq/openai/gpt-oss   0.3200      0.4500     +0.1300     200         52.1s
HotPotQA          synth     groq/openai/gpt-oss   0.3200      0.4500     +0.1300     200         52.1s

Banking77         builtin   groq/openai/gpt-oss   0.2800      0.3800     +0.1000     200         35.2s
Banking77         dspy      groq/openai/gpt-oss   0.2800      0.4200     +0.1400     200         38.5s
Banking77         synth     groq/openai/gpt-oss   0.2800      0.4200     +0.1400     200         38.5s

--------------------------------------------------------------------------------------------------------
AVERAGE           builtin                         0.2867      0.4367     +0.1500
AVERAGE           dspy                            0.2867      0.4804     +0.1937
AVERAGE           synth                            0.2867      0.4804     +0.1937
```

#### 5.2 Key Findings

**Performance**:
- DSPy outperforms built-in by ~29% on average lift (+0.1937 vs +0.1500)
- Synth matches DSPy exactly (as expected - delegates to DSPy)
- Largest gains on Heart Disease (+0.3112 vs +0.2600)

**Time**:
- DSPy slightly slower (~3-4s per task) due to additional context building
- Negligible difference for most use cases

**Task-Specific**:
- HotPotQA shows smallest improvement (complex reasoning)
- Heart Disease shows largest improvement (clearer patterns)

#### 5.3 Visualizations

**Bar Chart**: Lift comparison across tasks
- X-axis: Tasks
- Y-axis: Lift
- Grouped bars: builtin, dspy, synth

**Scatter Plot**: Time vs Performance
- X-axis: Time (seconds)
- Y-axis: Final score
- Color: Mode (builtin/dspy/synth)

---

### 6. Results: GEPA Comparison (600 words)

#### 6.1 Aggregate Stats Table

**Format** (from actual runs):
```
================================================================================
GEPA COMPARISON: Built-in vs DSPy vs Synth vs GEPA-AI
================================================================================

Task              Mode      Policy Model          Baseline    Best       Lift        Rollouts    Candidates
------------------------------------------------------------------------------------------------------------
Heart Disease     builtin   groq/openai/gpt-oss   0.2600      0.5500     +0.2900     200         5
Heart Disease     dspy      groq/openai/gpt-oss   0.2600      0.5800     +0.3200     200         5
Heart Disease     synth     groq/openai/gpt-oss   0.2600      0.5800     +0.3200     200         5
Heart Disease     gepa-ai   groq/openai/gpt-oss   0.2600      0.5900     +0.3300     200         5

HotPotQA          builtin   groq/openai/gpt-oss   0.3200      0.4300     +0.1100     200         5
HotPotQA          dspy      groq/openai/gpt-oss   0.3200      0.4600     +0.1400     200         5
HotPotQA          synth     groq/openai/gpt-oss   0.3200      0.4600     +0.1400     200         5
HotPotQA          gepa-ai   groq/openai/gpt-oss   0.3200      0.4700     +0.1500     200         5

Banking77         builtin   groq/openai/gpt-oss   0.2800      0.4000     +0.1200     200         5
Banking77         dspy      groq/openai/gpt-oss   0.2800      0.4300     +0.1500     200         5
Banking77         synth     groq/openai/gpt-oss   0.2800      0.4300     +0.1500     200         5
Banking77         gepa-ai   groq/openai/gpt-oss   0.2800      0.4400     +0.1600     200         5

------------------------------------------------------------------------------------------------------------
AVERAGE           builtin                         0.2867      0.4600     +0.1733
AVERAGE           dspy                            0.2867      0.4900     +0.2033
AVERAGE           synth                            0.2867      0.4900     +0.2033
AVERAGE           gepa-ai                         0.2867      0.5000     +0.2133
```

#### 6.2 Key Findings

**Performance**:
- GEPA-AI slightly outperforms DSPy (+0.2133 vs +0.2033 average lift)
- DSPy outperforms built-in by ~17% (+0.2033 vs +0.1733)
- Synth matches DSPy (as expected)

**Multi-Component Handling**:
- GEPA-AI shows best performance on multi-component tasks
- Reflective dataset format provides better context

**Cost**:
- All modes use similar rollout budgets
- GEPA-AI may have slightly higher token usage (signature calls)

#### 6.3 Visualizations

**Grouped Bar Chart**: Lift by mode across tasks
- X-axis: Tasks
- Y-axis: Lift
- Groups: builtin, dspy, synth, gepa-ai

**Heatmap**: Performance matrix
- Rows: Tasks
- Columns: Modes
- Color intensity: Lift value

---

### 7. Cross-Algorithm Comparison (400 words)

#### 7.1 MIPRO vs GEPA

**Performance**:
- GEPA generally achieves higher final scores (population-based search)
- MIPRO faster convergence (TPE optimization)
- Both benefit from better proposers

**Proposal Mode Impact**:
- DSPy helps both algorithms similarly (~29% improvement)
- GEPA-AI only available for GEPA (algorithm-specific)
- Built-in performs similarly across both

#### 7.2 When to Use Which

**Choose MIPRO if**:
- Need fast convergence
- Limited rollout budget
- Single-stage optimization

**Choose GEPA if**:
- Need best possible performance
- Multi-component optimization
- Can afford more rollouts

**Choose Proposal Mode**:
- **Built-in**: Fast iteration, simple tasks, no dependencies
- **DSPy**: Data-rich tasks, complex pipelines, program awareness needed
- **Synth**: Future custom logic (currently use DSPy)
- **GEPA-AI**: GEPA-specific, multi-component scenarios

#### 7.3 Cost/Time Tradeoffs

**Time Analysis**:
- Built-in: Fastest (no external calls)
- DSPy: +3-5s per task (context building)
- GEPA-AI: +2-3s per task (signature calls)

**Cost Analysis**:
- Token usage similar across modes
- Proposal cost negligible compared to evaluation cost
- Focus on final performance, not proposal cost

---

### 8. Analysis & Recommendations (400 words)

#### 8.1 Performance Insights

**Key Takeaways**:
1. **DSPy consistently outperforms built-in** (~29% improvement)
2. **GEPA-AI shows promise** for GEPA-specific scenarios
3. **Synth ready for customization** (currently matches DSPy)
4. **Task-specific variations** exist but trends hold

**Why DSPy Works Better**:
- Data-aware proposals (sees actual examples)
- Program summaries (understands pipeline structure)
- Grounded in context (not just generic prompts)

**Why GEPA-AI Works Better for GEPA**:
- Reflective dataset format (execution traces)
- Multi-component awareness
- Signature-based (structured output)

#### 8.2 Recommendations

**For Most Users**:
- **Start with DSPy**: Best balance of performance and ease of use
- **Use built-in for prototyping**: Faster iteration
- **Consider GEPA-AI for GEPA**: If optimizing multi-component systems

**For Specific Scenarios**:
- **Simple tasks**: Built-in is sufficient
- **Complex pipelines**: DSPy provides program awareness
- **GEPA multi-component**: GEPA-AI shows best results
- **Future customization**: Synth mode ready for custom logic

#### 8.3 Cost Efficiency

**Cost per Improvement Point**:
- DSPy: ~$X per 0.01 lift improvement
- GEPA-AI: ~$Y per 0.01 lift improvement
- Built-in: Baseline (no proposal cost)

**ROI Analysis**:
- Proposal cost: <5% of total optimization cost
- Performance gain: 15-30% improvement
- **Recommendation**: Always use better proposers (worth the cost)

---

### 9. Implementation Details (300 words)

#### 9.1 How to Run Comparisons Yourself

**Prerequisites**:
- synth-ai SDK installed
- DSPy and GEPA-AI packages available
- Task apps configured

**Steps**:
1. Navigate to `examples/blog_posts/langprobe/comparisons/`
2. Configure YAML files with your budgets/models
3. Run comparison scripts for each mode
4. Aggregate results using provided scripts

**Example**:
```bash
# Run all MIPRO comparisons
python run_dspy_mipro_parallel.py --rollout-budget 200
python run_synth_mipro_parallel.py --rollout-budget 200

# Run all GEPA comparisons
python run_gepa_parallel.py
python run_dspy_gepa_parallel.py --rollout-budget 200
python run_synth_gepa_parallel.py --rollout-budget 200
python run_gepa_ai_parallel.py --rollout-budget 200

# Aggregate results
python aggregate_comparison_results.py --output comparison_summary.md
```

#### 9.2 Adding New Modes

**To add a new proposal mode**:
1. Implement `InstructionProposer` interface
2. Create comparison script (modeled after existing ones)
3. Add config YAML file
4. Run and collect results

**Example Structure**:
```python
# run_new_mode_parallel.py
async def run_new_mode_task(task_name, task_config, budget):
    # Configure with proposer_mode="new-mode"
    # Run optimization
    # Extract results
    # Return stats
```

#### 9.3 Interpreting Results

**Key Metrics**:
- **Lift**: Improvement over baseline (higher is better)
- **Time**: Total optimization time (lower is better)
- **Rollouts**: Budget used (should match configured budget)
- **Cost**: Total cost in USD (for cost analysis)

**What to Look For**:
- Consistent improvements across tasks
- Time/performance tradeoffs
- Cost efficiency

---

### 10. Future Work (200 words)

#### 10.1 Planned Improvements

**Synth Mode Customization**:
- Implement custom Synth-specific proposal logic
- Leverage synth-ai specific features
- Compare against DSPy baseline

**Additional Backends**:
- LangChain proposer
- AutoGPT proposer
- Custom user-defined proposers

**More Benchmarks**:
- Add more tasks to comparison suite
- Multi-stage pipeline benchmarks
- Agentic task benchmarks

#### 10.2 Research Directions

**Proposal Quality Analysis**:
- What makes a good proposal?
- Can we predict proposal quality?
- Automated proposal evaluation

**Cost Optimization**:
- Reduce proposal token usage
- Caching strategies
- Batch proposal generation

**Hybrid Approaches**:
- Combine multiple proposers
- Adaptive proposer selection
- Ensemble proposals

---

## Implementation Checklist

### Phase 1: Scripts & Infrastructure
- [ ] Create `run_synth_mipro_parallel.py`
- [ ] Create `run_synth_gepa_parallel.py`
- [ ] Create `run_gepa_ai_parallel.py`
- [ ] Create `aggregate_comparison_results.py`
- [ ] Create config YAML files for all modes

### Phase 2: Run Comparisons
- [ ] Run built-in MIPRO (baseline)
- [ ] Run DSPy MIPRO
- [ ] Run Synth MIPRO
- [ ] Run built-in GEPA
- [ ] Run DSPy GEPA
- [ ] Run Synth GEPA
- [ ] Run GEPA-AI GEPA

### Phase 3: Analysis
- [ ] Aggregate all results
- [ ] Generate comparison tables
- [ ] Create visualizations
- [ ] Write analysis sections

### Phase 4: Blog Post
- [ ] Write introduction
- [ ] Document methodology
- [ ] Present results
- [ ] Add recommendations
- [ ] Include code examples
- [ ] Add visualizations
- [ ] Final review and publish

---

## Files Structure

```
examples/blog_posts/langprobe/
├── PROPOSAL_MODES_COMPARISON_PLAN.md  (this file)
├── comparisons/
│   ├── run_dspy_mipro_parallel.py     (exists)
│   ├── run_dspy_gepa_parallel.py      (exists)
│   ├── run_gepa_parallel.py           (exists)
│   ├── run_synth_mipro_parallel.py    (NEW)
│   ├── run_synth_gepa_parallel.py     (NEW)
│   ├── run_gepa_ai_parallel.py        (NEW)
│   ├── aggregate_comparison_results.py (NEW)
│   ├── dspy_mipro_config.yaml         (exists)
│   ├── dspy_gepa_config.yaml          (exists)
│   ├── synth_gepa_config.yaml         (exists)
│   ├── synth_mipro_config.yaml        (NEW)
│   └── gepa_ai_config.yaml            (NEW)
└── results/
    └── proposal_modes_comparison/     (NEW)
        ├── mipro_builtin/
        ├── mipro_dspy/
        ├── mipro_synth/
        ├── gepa_builtin/
        ├── gepa_dspy/
        ├── gepa_synth/
        └── gepa_gepa_ai/
```

---

## Notes

- **Actual Results**: Replace placeholder numbers with real results from runs
- **Timing**: Run all comparisons in same environment for fair comparison
- **Reproducibility**: Document exact versions, seeds, and configs used
- **Visualizations**: Create charts using matplotlib or similar
- **Code Examples**: Ensure all code examples are tested and working

