# Iris Framework Comparison Plan

## Overview

This directory contains scripts to run all 5 prompt optimization frameworks on Iris with comparable budgets and evaluate them on a held-out test set for apples-to-apples comparison.

## Frameworks

1. **Synth GEPA** - Synth-ai's GEPA optimizer (in-process)
2. **Synth MIPRO** - Synth-ai's MIPRO optimizer (in-process)
3. **DSPy MIPROv2** - DSPy's MIPROv2 teleprompter
4. **DSPy GEPA** - DSPy's GEPA teleprompter
5. **Lakshya GEPA** - Lakshya Agrawal's standalone GEPA library

## Dataset Splits

- **Training seeds**: 0-99 (100 examples) - Used for optimization
- **Validation seeds**: 100-149 (50 examples) - Used during optimization for validation/early stopping
- **Test seeds**: 100-149 (50 examples) - **HELD-OUT**, only used for final evaluation AFTER optimization completes

**Note**: Validation and test use the same seeds (100-149), but:
- **Validation** is used **during** optimization (for early stopping, hyperparameter tuning, etc.)
- **Test** is evaluated **after** optimization completes (apples-to-apples comparison)

This ensures fair comparison: all frameworks see the same validation data during optimization, and we evaluate all optimized prompts on the same test set using the same model.

## Budgets

We run comparisons at two budget levels:
- **Budget 100**: Modest budget for quick comparisons
- **Budget 500**: Larger budget for more thorough optimization

## Usage

### Run Single Budget Comparison

```bash
# Budget 100
python3 -m examples.blog_posts.langprobe.task_specific.iris.run_comparison_iris --rollout-budget 100

# Budget 500
python3 -m examples.blog_posts.langprobe.task_specific.iris.run_comparison_iris --rollout-budget 500
```

### Run Both Budgets

```bash
# Run both budgets sequentially
./run_comparison.sh 100
./run_comparison.sh 500
```

### Skip Test Evaluation (Optimization Only)

```bash
python3 -m examples.blog_posts.langprobe.task_specific.iris.run_comparison_iris \
    --rollout-budget 100 \
    --skip-test-eval
```

## Results Structure

```
iris/results/comparison/
├── budget_100/
│   ├── comparison_results.json       # Summary of all framework results
│   ├── synth_gepa/                   # Synth GEPA results
│   ├── synth_mipro/                  # Synth MIPRO results
│   ├── dspy_mipro/                   # DSPy MIPROv2 results
│   ├── dspy_gepa/                    # DSPy GEPA results
│   └── lakshya_gepa/                 # Lakshya GEPA results
└── budget_500/
    └── ... (same structure)
```

## Comparison Results Format

The `comparison_results.json` file contains:

```json
{
  "rollout_budget": 100,
  "train_seeds": [0, 1, ..., 99],
  "val_seeds": [100, 101, ..., 149],
  "test_seeds": [100, 101, ..., 149],
  "frameworks": {
    "synth_gepa": {
      "status": "completed",
      "best_score": 0.95,
      "train_score": 0.92,
      "val_score": 0.90,
      "total_rollouts": 100,
      "output_dir": "..."
    },
    ...
  },
  "test_evaluation": {
    "synth_gepa": {
      "status": "completed",
      "test_accuracy": 0.88,
      "test_mean_reward": 0.88,
      "test_correct": 44,
      "test_total": 50
    },
    ...
  }
}
```

## Metrics

For each framework, we track:
- **best_score**: Best score achieved during optimization
- **train_score**: Score on training set
- **val_score**: Score on validation set (used during optimization)
- **test_accuracy**: Accuracy on held-out test set (apples-to-apples comparison)
- **test_mean_reward**: Mean reward on test set

## Apples-to-Apples Comparison

All frameworks are evaluated on the **same held-out test set** (seeds 100-149) using the **same model** (`groq/llama-3.3-70b-versatile`) to ensure fair comparison.

## Next Steps

1. Run comparisons at budgets 100 and 500
2. Aggregate results across budgets
3. Generate comparison visualizations (learning curves, final performance, etc.)
4. Analyze which frameworks perform best at different budget levels

