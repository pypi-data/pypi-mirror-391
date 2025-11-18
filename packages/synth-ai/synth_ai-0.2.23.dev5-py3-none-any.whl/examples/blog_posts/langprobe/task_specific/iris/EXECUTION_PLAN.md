# Iris Framework Comparison - Execution Plan

## Overview

Run all 5 frameworks at budgets 100 and 500, then compare on held-out test set.

## Execution Steps

### Step 1: Run Budget 100 Comparison

```bash
cd examples/blog_posts/langprobe/task_specific/iris
python3 -m examples.blog_posts.langprobe.task_specific.iris.run_comparison_iris --rollout-budget 100
```

**Expected time**: ~30-60 minutes (depending on framework speeds)

**Output**: `iris/results/comparison/budget_100/comparison_results.json`

### Step 2: Run Budget 500 Comparison

```bash
python3 -m examples.blog_posts.langprobe.task_specific.iris.run_comparison_iris --rollout-budget 500
```

**Expected time**: ~2-4 hours

**Output**: `iris/results/comparison/budget_500/comparison_results.json`

### Step 3: Aggregate Results

After both budgets complete, aggregate results for visualization:

```python
# Results will be in:
# - iris/results/comparison/budget_100/comparison_results.json
# - iris/results/comparison/budget_500/comparison_results.json
```

## Comparison Metrics

For each framework at each budget, we track:

1. **Optimization Metrics**:
   - `best_score`: Best score during optimization
   - `train_score`: Score on training set
   - `val_score`: Score on validation set (used during optimization)

2. **Test Set Metrics** (Apples-to-Apples):
   - `test_accuracy`: Accuracy on held-out test set
   - `test_mean_reward`: Mean reward on test set
   - `test_correct`: Number of correct predictions
   - `test_total`: Total test examples (50)

## Framework-Specific Notes

### Synth GEPA
- Uses in-process adapter (no HTTP polling)
- Saves optimized prompt to `iris_best_prompt.json`
- Learning curve tracked automatically

### Synth MIPRO
- Uses in-process adapter
- Requires bootstrap seeds (subset of train seeds)
- Saves optimized prompt to `iris_best_prompt.json`

### DSPy MIPROv2
- Uses DSPy's MIPROv2 teleprompter
- Optimizes instructions + few-shot examples
- Saves module info to `iris_best_module.json`

### DSPy GEPA
- Uses DSPy's GEPA teleprompter
- Requires reflection LM
- Saves module info to `iris_best_module.json`

### Lakshya GEPA
- Uses standalone GEPA library
- Requires GEPAAdapter implementation
- Saves optimized prompt to `iris_best_prompt.json`

## Next Steps After Comparison

1. **Visualization**: Generate learning curves, final performance bar charts, efficiency plots
2. **Analysis**: Compare frameworks at different budget levels
3. **Insights**: Identify which frameworks work best for Iris classification
4. **Scaling**: Run on additional benchmarks (GSM8K, HeartDisease, etc.)

