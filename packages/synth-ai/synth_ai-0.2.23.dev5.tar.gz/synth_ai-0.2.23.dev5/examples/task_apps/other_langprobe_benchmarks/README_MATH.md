# MATH Task App

MATH competition math task app for LangProBe benchmarks.

## Dataset

- **Source**: `hendrycks/competition_math` on HuggingFace
- **Splits**: `train`, `test`
- **Default split**: `test`
- **Description**: High school and competition math problems

## Usage

### Start the Task App

```bash
python -m examples.task_apps.other_langprobe_benchmarks.math_task_app --port 8111
```

Or using the CLI:

```bash
uvx synth-ai serve math --port 8111
```

### Run Baseline Evaluation

```bash
python examples/task_apps/other_langprobe_benchmarks/math_baseline.py \
  --task-app-url http://127.0.0.1:8111 \
  --num-seeds 10 \
  --model gpt-5-nano
```

### Using Eval Config

Create `eval_math_gpt5nano.toml`:

```toml
[eval]
app_id = "math"
task_app_url = "http://127.0.0.1:8111"
model = "gpt-5-nano"
seeds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
max_turns = 1
concurrency = 1

[eval.policy_config]
provider = "openai"
model = "gpt-5-nano"
inference_url = "https://api.openai.com/v1"
temperature = 0.0
max_tokens = 1024
```

Then run:

```bash
uvx synth-ai eval --config eval_math_gpt5nano.toml
```

## Task Format

- **Observation**: Math problem text
- **Action**: Free-form text response with solution
- **Reward**: 1.0 if answer matches (normalized), 0.0 otherwise
- **Answer Normalization**: Extracts `\boxed{...}` LaTeX expressions and normalizes math notation

## Implementation Notes

- Uses `gepa_benchmarks.common` for shared utilities (LLM calls, answer normalization)
- Single-turn task (max_turns=1)
- Answer matching uses normalized LaTeX math expressions

