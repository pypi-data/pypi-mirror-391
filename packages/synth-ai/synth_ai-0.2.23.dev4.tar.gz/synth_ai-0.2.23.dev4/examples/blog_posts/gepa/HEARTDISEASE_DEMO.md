# Heart Disease GEPA Standalone Demo

This demo shows a complete end-to-end GEPA optimization workflow for the Heart Disease classification task, entirely within a single Python script (no CLI required).

## Overview

The `heartdisease_gepa_standalone.py` script demonstrates:

1. **Starting a local task app** for Heart Disease classification
2. **Submitting a GEPA job** via the Python API
3. **Polling the job** until completion
4. **Extracting the best prompt** candidate
5. **Evaluating the optimized prompt** on a held-out test set
6. **Comparing** baseline vs optimized performance

This is similar to the langprobe examples, but everything is done in-process within a standalone script.

## Files

- `heartdisease_baseline.py` - Task runner for Heart Disease classification
- `configs/heartdisease_gepa_local.toml` - GEPA configuration
- `heartdisease_gepa_standalone.py` - Main standalone script

## Prerequisites

1. **Install synth-ai**:
   ```bash
   pip install synth-ai
   # or
   uv pip install synth-ai
   ```

2. **Set environment variables**:
   ```bash
   export GROQ_API_KEY="your-groq-api-key"
   export SYNTH_API_KEY="your-synth-api-key"  # If using Synth backend
   export ENVIRONMENT_API_KEY="test"  # For local task app
   ```

3. **Backend setup** (choose one):

   **Option A: Local backend** (recommended for testing):
   ```bash
   # Start local backend in a separate terminal
   uvx synth-ai backend
   ```

   **Option B: Synth production backend**:
   ```bash
   export BACKEND_BASE_URL="https://api.usesynth.ai"
   export SYNTH_API_KEY="your-actual-synth-api-key"
   ```

## Usage

Run the standalone script:

```bash
python heartdisease_gepa_standalone.py
```

The script will:

1. Start a local task app server on `http://127.0.0.1:8114`
2. Submit a GEPA optimization job with:
   - 30 training examples (seeds 0-29)
   - 50 validation examples (seeds 30-79)
   - 300 rollout budget
   - 5 generations of prompt evolution
3. Poll the job status every 5 seconds
4. Once complete, extract the best prompt
5. Evaluate both baseline and optimized prompts on test set (seeds 80-99)
6. Print comparison results and save to JSON

## Expected Output

```
================================================================================
Heart Disease GEPA Standalone Demo
================================================================================

================================================================================
Step 1: Starting Task App Server
================================================================================

Command: uvx synth-ai serve ...
✓ Task app server ready at http://127.0.0.1:8114

================================================================================
Step 2: Submitting GEPA Optimization Job
================================================================================

✓ Job submitted: pl_abc123...

================================================================================
Step 3: Polling Job Status
================================================================================

[poll] 10:30:15 0s status=running
[poll] 10:30:20 5s status=running
...
✓ Job complete! Final status: succeeded

================================================================================
Step 4: Extracting Best Prompt
================================================================================

Best validation score: 0.8200 (82.00%)

Optimized System Prompt:
--------------------------------------------------------------------------------
[Optimized prompt text here]
--------------------------------------------------------------------------------

================================================================================
Step 5: Evaluating on Test Set
================================================================================

Evaluating baseline prompt...
Evaluating optimized prompt...

================================================================================
Final Results
================================================================================

Test Set Size: 20 examples

Baseline Accuracy:  0.7500 (75.00%)
Optimized Accuracy: 0.8500 (85.00%)

Improvement: +0.1000 (+10.00%)

✓ Results saved to: results/heartdisease_gepa_standalone/results.json

================================================================================
Demo Complete!
================================================================================
```

## Output Files

The script saves results to:
```
results/heartdisease_gepa_standalone/
└── results.json
```

The JSON file contains:
- Job ID
- Best validation score
- Test set accuracies (baseline and optimized)
- Improvement delta
- Full optimized prompts
- Detailed predictions for each test example

## Configuration

You can modify the GEPA parameters in `configs/heartdisease_gepa_local.toml`:

- `rollout.budget` - Total evaluation budget (default: 300)
- `population.initial_size` - Starting population size (default: 5)
- `population.num_generations` - Number of evolution generations (default: 5)
- `mutation.rate` - Mutation probability (default: 0.3)
- `evaluation.train_seeds` - Training examples (default: 0-29)
- `evaluation.val_seeds` - Validation examples (default: 30-79)

## Customization

To adapt this for your own dataset:

1. Create a new baseline file (copy `heartdisease_baseline.py`)
2. Update the dataset loading in your baseline
3. Create a config file (copy `configs/heartdisease_gepa_local.toml`)
4. Modify the script to use your baseline and config

## Troubleshooting

**Server fails to start:**
- Check that port 8114 is available
- Ensure `heartdisease_baseline.py` is in the same directory
- Verify synth-ai is installed: `uvx synth-ai --version`

**Job submission fails:**
- Verify SYNTH_API_KEY is set
- Check backend is running (local or production)
- Ensure GROQ_API_KEY is set for inference

**Evaluation errors:**
- Check GROQ_API_KEY is valid
- Verify dataset can be loaded: `python -c "from datasets import load_dataset; load_dataset('buio/heart-disease')"`

## References

- GEPA paper: [Link to paper]
- Synth AI documentation: https://docs.usesynth.ai
- Heart Disease dataset: https://huggingface.co/datasets/buio/heart-disease
