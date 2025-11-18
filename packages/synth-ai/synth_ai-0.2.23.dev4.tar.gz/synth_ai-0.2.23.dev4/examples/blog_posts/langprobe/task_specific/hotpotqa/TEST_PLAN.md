# Test Plan: No-Step-Info Refactor for GEPA/MIPRO

## Overview

This document outlines comprehensive unit and integration tests to validate the refactored GEPA/MIPRO optimizers that eliminate the `step.info.messages` requirement and use GRPO-style trace hydration.

## Test Categories

### 1. Unit Tests: Core Functions

#### 1.1 Trace Utilities (`trace_utils.py`)

**File**: `tests/unit/prompt_learning/test_trace_utils.py`

**Tests**:
- [ ] `test_extract_correlation_id_from_inference_url()` - Valid URLs with `?cid=...`
  - Valid URL: `http://localhost:8000/v1/chat/completions?cid=trace_abc123`
  - Expected: `"trace_abc123"`
- [ ] `test_extract_correlation_id_missing()` - URLs without `?cid=...`
  - Invalid URL: `http://localhost:8000/v1/chat/completions`
  - Expected: `None`
- [ ] `test_extract_correlation_id_malformed()` - Malformed URLs
  - Invalid URL: `not-a-url`
  - Expected: `None` (graceful failure)
- [ ] `test_extract_correlation_id_multiple_params()` - URLs with multiple query params
  - URL: `http://localhost:8000/v1/chat/completions?cid=trace_abc123&other=value`
  - Expected: `"trace_abc123"`
- [ ] `test_with_trace_query_param()` - Add `?cid=...` to URL
  - Input: `http://localhost:8000/v1/chat/completions`, `trace_abc123`
  - Expected: `http://localhost:8000/v1/chat/completions?cid=trace_abc123`
- [ ] `test_with_trace_query_param_existing_params()` - Add to URL with existing params
  - Input: `http://localhost:8000/v1/chat/completions?foo=bar`, `trace_abc123`
  - Expected: `http://localhost:8000/v1/chat/completions?foo=bar&cid=trace_abc123`
- [ ] `test_validate_rollout_response_for_prompt_learning()` - Valid response
  - Response with `inference_url` containing `?cid=...`
  - Expected: No exception
- [ ] `test_validate_rollout_response_missing_cid()` - Missing `?cid=...`
  - Response with `inference_url` but no `?cid=...`
  - Expected: `ValueError` with clear message
- [ ] `test_validate_rollout_response_missing_inference_url()` - Missing `inference_url`
  - Response without `inference_url` field
  - Expected: `ValueError` with clear message

#### 1.2 Trace Reconstruction (`trace_reconstruction.py`)

**File**: `tests/unit/prompt_learning/test_trace_reconstruction.py`

**Tests**:
- [ ] `test_reconstruct_event_history_single_envelope()` - Single LLM call
  - One envelope with conversation metadata
  - Expected: One `lm_call` event with `llm_request` and `llm_response`
- [ ] `test_reconstruct_event_history_multiple_envelopes()` - Multi-turn conversation
  - Three envelopes with sequence_index 0, 1, 2
  - Expected: Three `lm_call` events in chronological order
- [ ] `test_reconstruct_event_history_empty_envelopes()` - Empty input
  - Empty list of envelopes
  - Expected: Empty list `[]`
- [ ] `test_reconstruct_event_history_missing_metadata()` - Missing conversation data
  - Envelope without `conversation` or `response_entry`
  - Expected: AssertionError (fail fast)
- [ ] `test_reconstruct_event_history_tool_calls()` - Tool-using conversation
  - Envelope with `tool_calls` in response
  - Expected: Event includes `tool_calls` field
- [ ] `test_reconstruct_event_history_sorting()` - Verify chronological ordering
  - Envelopes with out-of-order `sequence_index`
  - Expected: Events sorted by `sequence_index`, then `created_at_wall`
- [ ] `test_reconstruct_event_history_usage_stats()` - Token usage extraction
  - Envelope with `prompt_tokens` and `response_tokens`
  - Expected: `llm_response.usage` contains correct token counts

#### 1.3 Trace Hydration (`trace_hydration.py`)

**File**: `tests/unit/prompt_learning/test_trace_hydration.py`

**Tests**:
- [ ] `test_populate_traces_path1_complete_trace()` - Path 1: Complete v3 trace
  - Item with `trace.trace_id` and `trace.event_history`
  - Expected: Skip hydration, use existing trace
- [ ] `test_populate_traces_path2_correlation_id()` - Path 2: Correlation ID reconstruction
  - Item with `inference_url` containing `?cid=trace_abc123`
  - Mock trace_client to return envelopes
  - Expected: Trace hydrated with `event_history`
- [ ] `test_populate_traces_missing_correlation_id()` - Missing correlation ID
  - Item without `inference_url` or without `?cid=...`
  - Expected: `ValueError` with clear message
- [ ] `test_populate_traces_trace_store_failure()` - Trace store unavailable
  - Mock trace_client to raise exception
  - Expected: Exception propagated (fail fast)
- [ ] `test_populate_traces_multiple_items()` - Batch hydration
  - Multiple items with different correlation IDs
  - Expected: All traces hydrated correctly
- [ ] `test_populate_traces_idempotent()` - Idempotent hydration
  - Call hydration twice on same item
  - Expected: Second call skips (already hydrated)

### 2. Unit Tests: Pattern Validation

#### 2.1 GEPA Pattern Validation

**File**: `tests/unit/prompt_learning/algorithm/gepa/test_pattern_validation.py`

**Tests**:
- [ ] `test_validate_pattern_uses_initial_pattern()` - Uses TOML config directly
  - `initial_pattern` in config with messages
  - Expected: No rollout, uses `initial_pattern.messages` directly
- [ ] `test_validate_pattern_no_rollout_needed()` - No rollout request sent
  - Verify no HTTP calls to task app during validation
  - Expected: Zero HTTP requests
- [ ] `test_validate_pattern_missing_initial_pattern()` - Missing initial_pattern
  - Config without `initial_pattern`
  - Expected: `ValueError` or graceful fallback
- [ ] `test_validate_pattern_wildcard_extraction()` - Extract wildcards from pattern
  - Pattern with `{features}` wildcard
  - Expected: Wildcards extracted correctly

#### 2.2 MIPRO Pattern Validation

**File**: `tests/unit/prompt_learning/algorithm/mipro/test_pattern_validation.py`

**Tests**:
- [ ] `test_gather_baseline_messages_uses_initial_pattern()` - Uses TOML config
  - Similar to GEPA tests
  - Expected: No rollout, uses config directly
- [ ] `test_gather_baseline_messages_no_rollout()` - No rollout request
  - Verify no HTTP calls
  - Expected: Zero HTTP requests

### 3. Integration Tests: End-to-End Optimization

#### 3.1 GEPA Integration Tests

**File**: `tests/integration/prompt_learning/test_gepa_integration.py`

**Tests**:
- [ ] `test_gepa_optimization_iris_no_step_info()` - Full GEPA run on Iris
  - Mock task app returns minimal response (no `step.info.messages`)
  - Mock trace_client for hydration
  - Expected: Optimization completes, best prompt generated
- [ ] `test_gepa_optimization_hotpotqa_no_step_info()` - Full GEPA run on HotpotQA
  - Similar to Iris test
  - Expected: Optimization completes successfully
- [ ] `test_gepa_trace_hydration_during_optimization()` - Verify hydration happens
  - Mock trace_client, verify `populate_traces_from_store()` called
  - Expected: Traces hydrated before scoring
- [ ] `test_gepa_pattern_validation_no_rollout()` - Verify no rollout for validation
  - Mock HTTP client, verify no requests during validation
  - Expected: Zero requests during pattern validation phase

#### 3.2 MIPRO Integration Tests

**File**: `tests/integration/prompt_learning/test_mipro_integration.py`

**Tests**:
- [ ] `test_mipro_optimization_iris_no_step_info()` - Full MIPRO run on Iris
  - Mock task app returns minimal response
  - Expected: Optimization completes successfully
- [ ] `test_mipro_optimization_hotpotqa_no_step_info()` - Full MIPRO run on HotpotQA
  - Similar to Iris test
  - Expected: Optimization completes successfully
- [ ] `test_mipro_trace_hydration_during_optimization()` - Verify hydration
  - Mock trace_client, verify hydration called
  - Expected: Traces hydrated before scoring
- [ ] `test_mipro_baseline_messages_no_rollout()` - Verify no rollout for baseline
  - Mock HTTP client, verify no requests
  - Expected: Zero requests during baseline gathering

### 4. Integration Tests: Task App Compatibility

#### 4.1 Minimal Task App Response

**File**: `tests/integration/prompt_learning/test_task_app_compatibility.py`

**Tests**:
- [ ] `test_minimal_response_accepted()` - Minimal valid response
  - Response with only required fields:
    - `run_id`, `trajectories`, `metrics`
    - `metrics.episode_returns`, `metrics.mean_return`, `metrics.num_steps`
    - `metrics.outcome_score` (functionally required)
  - Expected: Optimization proceeds successfully
- [ ] `test_response_without_step_info_messages()` - No `step.info.messages`
  - Response without `step.info.messages` field
  - Expected: No errors, optimization proceeds
- [ ] `test_response_with_inference_url_cid()` - `inference_url` with `?cid=...`
  - Response with `inference_url` containing `?cid=trace_abc123`
  - Expected: Correlation ID extracted, trace hydrated
- [ ] `test_response_without_outcome_score()` - Missing `outcome_score`
  - Response without `metrics.outcome_score`
  - Expected: Falls back to `mean_return` or `0.0` (with warning)

#### 4.2 Backward Compatibility

**File**: `tests/integration/prompt_learning/test_backward_compatibility.py`

**Tests**:
- [ ] `test_legacy_response_still_works()` - Legacy response format
  - Response with `step.info.messages` (old format)
  - Expected: Still works (backward compatible)
- [ ] `test_response_with_obs_text_action_text()` - Nice-to-have fields
  - Response with `obs.text` and `action.text`
  - Expected: Used for few-shot examples (MIPRO)
- [ ] `test_response_without_obs_text_action_text()` - Missing nice-to-have fields
  - Response without `obs.text` or `action.text`
  - Expected: Uses placeholders (MIPRO), no errors

### 5. Integration Tests: Trace Hydration

#### 5.1 Trace Store Integration

**File**: `tests/integration/prompt_learning/test_trace_hydration_integration.py`

**Tests**:
- [ ] `test_hydration_with_real_trace_store()` - Real trace store (if available)
  - Use real trace store instance
  - Expected: Traces hydrated correctly
- [ ] `test_hydration_with_mock_trace_store()` - Mock trace store
  - Mock trace_client with sample envelopes
  - Expected: `event_history` reconstructed correctly
- [ ] `test_hydration_failure_handling()` - Trace store failure
  - Mock trace_client to raise exception
  - Expected: Exception propagated, optimization fails gracefully
- [ ] `test_hydration_empty_envelopes()` - No envelopes found
  - Mock trace_client returns empty envelopes
  - Expected: `ValueError` with clear message

### 6. Integration Tests: Judge Integration (Optional)

#### 6.1 Rubric Pipeline Integration

**File**: `tests/integration/prompt_learning/test_judge_integration.py`

**Tests**:
- [ ] `test_judge_with_hydrated_traces()` - Judges use hydrated traces
  - Enable rubric pipeline, hydrate traces
  - Expected: Judges receive `event_history`, score correctly
- [ ] `test_judge_without_traces()` - Judges disabled
  - Disable rubric pipeline
  - Expected: Uses task app `outcome_score` directly
- [ ] `test_judge_outcome_score_fallback()` - Missing `outcome_score` + judges
  - Response without `outcome_score`, judges enabled
  - Expected: Judges compute score, used for optimization

### 7. End-to-End Tests: Local Execution

#### 7.1 Iris Local Tests

**File**: `tests/e2e/prompt_learning/test_iris_local.py`

**Tests**:
- [ ] `test_local_mipro_iris_no_step_info()` - Local MIPRO on Iris
  - Use `run_mipro_local.py` script
  - Expected: Optimization completes, no `step.info.messages` errors
- [ ] `test_local_gepa_iris_no_step_info()` - Local GEPA on Iris
  - Use `synth_iris_adapter.py` script
  - Expected: Optimization completes successfully
- [ ] `test_local_mipro_iris_trace_hydration()` - Verify trace hydration
  - Enable trace_client, verify hydration logs
  - Expected: Traces hydrated, `event_history` populated
- [ ] `test_local_gepa_iris_pattern_validation()` - Verify pattern validation
  - Check logs for pattern validation
  - Expected: No rollout requests during validation

#### 7.2 HotpotQA Local Tests

**File**: `tests/e2e/prompt_learning/test_hotpotqa_local.py`

**Tests**:
- [ ] `test_local_mipro_hotpotqa_no_step_info()` - Local MIPRO on HotpotQA
  - Use `synth_hotpotqa_adapter.py` script
  - Expected: Optimization completes successfully
- [ ] `test_local_gepa_hotpotqa_no_step_info()` - Local GEPA on HotpotQA
  - Similar to MIPRO test
  - Expected: Optimization completes successfully

### 8. Performance Tests

#### 8.1 Pattern Validation Performance

**File**: `tests/performance/prompt_learning/test_pattern_validation_perf.py`

**Tests**:
- [ ] `test_pattern_validation_no_network_calls()` - No network overhead
  - Measure time for pattern validation
  - Expected: < 1ms (no network calls)
- [ ] `test_pattern_validation_vs_old_approach()` - Compare to old approach
  - Old: Rollout + extract messages
  - New: Use TOML config directly
  - Expected: New approach 10-100x faster

#### 8.2 Trace Hydration Performance

**File**: `tests/performance/prompt_learning/test_trace_hydration_perf.py`

**Tests**:
- [ ] `test_hydration_latency()` - Measure hydration time
  - Single trace hydration
  - Expected: < 100ms (with mock trace_client)
- [ ] `test_batch_hydration_latency()` - Batch hydration
  - 10 traces hydrated in parallel
  - Expected: < 500ms total

### 9. Error Handling Tests

#### 9.1 Validation Error Handling

**File**: `tests/unit/prompt_learning/test_error_handling.py`

**Tests**:
- [ ] `test_validation_error_missing_inference_url()` - Clear error message
  - Response without `inference_url`
  - Expected: `ValueError` with helpful message
- [ ] `test_validation_error_missing_cid()` - Clear error message
  - Response with `inference_url` but no `?cid=...`
  - Expected: `ValueError` with fix instructions
- [ ] `test_validation_error_malformed_url()` - Malformed URL handling
  - Response with malformed `inference_url`
  - Expected: `ValueError` with clear message

#### 9.2 Hydration Error Handling

**Tests**:
- [ ] `test_hydration_error_trace_store_unavailable()` - Trace store down
  - Mock trace_client to raise connection error
  - Expected: Exception propagated with context
- [ ] `test_hydration_error_no_envelopes()` - No envelopes found
  - Mock trace_client returns empty result
  - Expected: `ValueError` with correlation_id in message

## Test Data Fixtures

### Minimal Valid Response Fixture

```python
MINIMAL_VALID_RESPONSE = {
    "run_id": "rollout-0",
    "trajectories": [
        {
            "env_id": "iris",
            "policy_id": "policy",
            "steps": [
                {
                    "obs": {},
                    "action": {},
                    "reward": 1.0,
                    "done": True
                }
            ],
            "length": 1,
            "inference_url": "http://localhost:8000/v1/chat/completions?cid=trace_abc123"
        }
    ],
    "metrics": {
        "episode_returns": [1.0],
        "mean_return": 1.0,
        "num_steps": 1,
        "outcome_score": 1.0
    }
}
```

### Complete Response Fixture (With Nice-to-Haves)

```python
COMPLETE_RESPONSE = {
    "run_id": "rollout-0",
    "trajectories": [
        {
            "env_id": "iris",
            "policy_id": "policy",
            "steps": [
                {
                    "obs": {
                        "text": "Flower Measurements:\nSepalLengthCm: 5.1\n..."
                    },
                    "action": {
                        "text": "setosa"
                    },
                    "reward": 1.0,
                    "done": True,
                    "info": {
                        "expected_label": "setosa",
                        "predicted_label": "setosa"
                    }
                }
            ],
            "length": 1,
            "inference_url": "http://localhost:8000/v1/chat/completions?cid=trace_abc123"
        }
    ],
    "metrics": {
        "episode_returns": [1.0],
        "mean_return": 1.0,
        "num_steps": 1,
        "outcome_score": 1.0,
        "details": {
            "correct": True
        }
    }
}
```

## Test Execution Strategy

### Phase 1: Unit Tests (Fast Feedback)
1. Run all unit tests first
2. Fix any failures before integration tests
3. Target: < 5 seconds total

### Phase 2: Integration Tests (Moderate)
1. Run integration tests with mocks
2. Verify core functionality
3. Target: < 30 seconds total

### Phase 3: End-to-End Tests (Slower)
1. Run local execution tests
2. Requires task apps running
3. Target: < 5 minutes total

### Phase 4: Performance Tests (Optional)
1. Run performance benchmarks
2. Compare to baseline
3. Target: Document improvements

## Coverage Goals

- **Unit Tests**: 90%+ coverage for new code
- **Integration Tests**: Cover all happy paths + critical error paths
- **End-to-End Tests**: Verify full optimization runs work

## Continuous Integration

### Pre-commit Hooks
- Run unit tests
- Run linting
- Run type checking

### CI Pipeline
- Run all unit tests
- Run all integration tests
- Run end-to-end tests (if task apps available)
- Generate coverage report

## Test Maintenance

### Adding New Tests
- Follow naming convention: `test_<functionality>_<scenario>()`
- Use descriptive test names
- Include docstrings explaining what's being tested

### Updating Tests
- Update tests when refactoring code
- Keep tests in sync with implementation
- Remove obsolete tests

## Success Criteria

1. ✅ All unit tests pass
2. ✅ All integration tests pass
3. ✅ End-to-end tests pass on Iris and HotpotQA
4. ✅ No `step.info.messages` errors in any test
5. ✅ Pattern validation completes without rollouts
6. ✅ Traces are hydrated correctly (if trace_client available)
7. ✅ Backward compatibility maintained

