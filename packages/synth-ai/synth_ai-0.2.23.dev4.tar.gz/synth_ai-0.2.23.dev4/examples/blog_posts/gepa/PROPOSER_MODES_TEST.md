# Proposer Modes Testing

This directory contains test configurations and scripts for testing the new GEPA and MIPRO proposer modes: `dspy`, `synth`, and `gepa-ai`.

## Overview

The proposer modes control how instruction mutations are generated during prompt optimization:

- **`builtin`** (default): Uses built-in mutation strategies
- **`dspy`**: Uses DSPy-style instruction proposer
- **`synth`**: Uses Synth-style instruction proposer (currently same as DSPy)
- **`gepa-ai`**: Uses GEPA-AI instruction proposer

## Test Configurations

### GEPA Configs
- `configs/heartdisease_gepa_dspy.toml` - GEPA with DSPy proposer
- `configs/heartdisease_gepa_synth.toml` - GEPA with Synth proposer
- `configs/heartdisease_gepa_gepa_ai.toml` - GEPA with GEPA-AI proposer

### MIPRO Configs
- `configs/heartdisease_mipro_dspy.toml` - MIPRO with DSPy proposer
- `configs/heartdisease_mipro_synth.toml` - MIPRO with Synth proposer
- `configs/heartdisease_mipro_gepa_ai.toml` - MIPRO with GEPA-AI proposer

## Running Tests

### Prerequisites

```bash
# Set required environment variables
export GROQ_API_KEY="your-groq-key"
export SYNTH_API_KEY="your-backend-key"
export ENVIRONMENT_API_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"

# Ensure backend is running
curl http://localhost:8000/api/health
```

### Run All Tests

```bash
# Test all proposer modes (GEPA + MIPRO)
python test_proposer_modes.py
```

### Run Specific Tests

```bash
# Test only GEPA algorithms
python test_proposer_modes.py --gepa-only

# Test only MIPRO algorithms
python test_proposer_modes.py --mipro-only

# Test only a specific proposer mode
python test_proposer_modes.py --mode dspy
python test_proposer_modes.py --mode synth
python test_proposer_modes.py --mode gepa-ai
```

## Test Script Features

The `test_proposer_modes.py` script:

1. **Starts a task app server** automatically (heart disease baseline)
2. **Submits jobs** for each test configuration
3. **Polls until completion** and collects results
4. **Prints a summary table** with:
   - Test name
   - Status (✓/✗)
   - Best validation score
   - Elapsed time
5. **Saves results** to `results/proposer_modes_test/results.json`

## Expected Output

```
================================================================================
PROPOSER MODE TEST SUITE
================================================================================

Total tests: 6
Tests to run:
  - GEPA + DSPy
  - GEPA + Synth
  - GEPA + GEPA-AI
  - MIPRO + DSPy
  - MIPRO + Synth
  - MIPRO + GEPA-AI

[... test execution ...]

================================================================================
TEST SUMMARY
================================================================================

┌──────────────────────────────────────────────────────────────────────────────┐
│ Test Name                      │    Status     │     Score      │      Time      │
├──────────────────────────────┼───────────────┼───────────────┼────────────────┤
│ GEPA + DSPy                   │       ✓       │    0.7234      │     145.2s      │
│ GEPA + Synth                  │       ✓       │    0.7101      │     142.8s      │
│ GEPA + GEPA-AI                │       ✓       │    0.7189      │     148.5s      │
│ MIPRO + DSPy                  │       ✓       │    0.7012      │     138.3s      │
│ MIPRO + Synth                 │       ✓       │    0.6956      │     140.1s      │
│ MIPRO + GEPA-AI               │       ✓       │    0.7089      │     139.7s      │
└──────────────────────────────┴───────────────┴───────────────┴────────────────┘

Total tests: 6
Passed: 6
Failed: 0
Skipped: 0
Average score: 0.7097 (70.97%)
```

## Configuration Details

### GEPA Proposer Mode Configuration

```toml
[prompt_learning.gepa]
proposer_mode = "dspy"  # or "synth" or "gepa-ai"

[prompt_learning.gepa.mutation]
# DSPy-specific config
dspy_meta_model = "llama-3.3-70b-versatile"
dspy_meta_provider = "groq"
dspy_temperature = 0.7
dspy_max_tokens = 512

# Synth-specific config (if proposer_mode = "synth")
synth_meta_model = "llama-3.3-70b-versatile"
synth_meta_provider = "groq"
synth_temperature = 0.7
synth_max_tokens = 512

# GEPA-AI-specific config (if proposer_mode = "gepa-ai")
gepa_ai_meta_model = "llama-3.3-70b-versatile"
gepa_ai_meta_provider = "groq"
gepa_ai_temperature = 0.7
gepa_ai_max_tokens = 512
```

### MIPRO Proposer Mode Configuration

```toml
[prompt_learning.mipro.instructions]
proposer_mode = "dspy"  # or "synth" or "gepa-ai"

# DSPy-specific config
dspy_meta_model = "llama-3.3-70b-versatile"
dspy_meta_provider = "groq"
dspy_temperature = 0.7
dspy_max_tokens = 512

# Synth-specific config (if proposer_mode = "synth")
synth_meta_model = "llama-3.3-70b-versatile"
synth_meta_provider = "groq"
synth_temperature = 0.7
synth_max_tokens = 512

# GEPA-AI-specific config (if proposer_mode = "gepa-ai")
gepa_ai_meta_model = "llama-3.3-70b-versatile"
gepa_ai_meta_provider = "groq"
gepa_ai_temperature = 0.7
gepa_ai_max_tokens = 512
```

## Troubleshooting

### "Config file not found"
- Ensure you're running from the `examples/blog_posts/gepa/` directory
- Check that config files exist in `configs/` subdirectory

### "Task app server failed to start"
- Check if port 8114 is already in use
- Ensure `heartdisease_baseline.py` exists in the same directory
- Verify `uvx synth-ai serve` command works

### "GROQ_API_KEY environment variable is required"
- Export your Groq API key: `export GROQ_API_KEY="your-key"`
- Or add it to `.env` file and load with `dotenv`

### Job fails or times out
- Check backend logs for errors
- Verify backend is running: `curl http://localhost:8000/api/health`
- Increase timeout in test script if needed (default: 600s per test)

## Next Steps

After running tests:

1. **Compare results** across proposer modes to see which performs best
2. **Check metadata** in job results to verify proposer mode was used correctly
3. **Inspect traces** to see how each proposer generates mutations
4. **Tune hyperparameters** (temperature, max_tokens) for each proposer mode

## Related Documentation

- [GEPA Algorithm Documentation](../../../../monorepo/docs/training-configs/pl.mdx)
- [MIPRO Algorithm Documentation](../../../../monorepo/docs/training-configs/pl.mdx)
- [Proposal System Implementation Plan](../../../../monorepo/PROPOSAL_SYSTEM_IMPLEMENTATION_PLAN.md)

