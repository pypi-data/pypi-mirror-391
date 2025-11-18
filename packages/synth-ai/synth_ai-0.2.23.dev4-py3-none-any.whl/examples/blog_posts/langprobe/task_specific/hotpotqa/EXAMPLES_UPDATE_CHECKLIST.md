# Examples & Demos Update Checklist: Post-Refactor

## Purpose
Comprehensive list of all examples, demos, task apps, and tests that need updates after:
1. **Step.info refactor** (removing `step.info.messages` requirement)
2. **MIPRO single-stage simplification** (`MIPROConfig.simple()` for single-stage)
3. **TOML parsing cleanup** (new `MIPROConfigFromTOML` dataclass)

## Summary Statistics

### Task Apps
- **Total checked**: 7 task apps
- **Need update**: 2 (Iris, HotpotQA) - Remove `step.info.messages` storage
- **No update needed**: 5 (PUPA, IFBench, HoVer, GSM8K, HeartDisease) - Already correct

### MIPRO Adapters
- **Single-stage adapters**: 3 files (should migrate to `MIPROConfig.simple()`)
- **Multi-stage adapters**: 1 file (keep full constructor - no changes)

### GEPA Adapters
- **Total**: 3+ files
- **Update needed**: 0 (GEPA simplification not in scope)

### Test Files
- **MIPRO tests**: 5 files (verify if single-stage, update if needed)
- **GEPA tests**: 4 files (no changes needed)

### Config Files
- **MIPRO TOML**: 9 files (verify backward compatibility)
- **GEPA TOML**: 15+ files (no changes needed)

### Documentation
- **README files**: 3 files (update examples)
- **Docs**: 2 files (update requirements)

## Update Categories

### Category 1: Task Apps (Remove `step.info.messages` Storage)

**Priority: HIGH** - These currently store `step.info.messages` and must be updated.

#### ✅ Already Updated (or need verification)
- [ ] `examples/task_apps/other_langprobe_benchmarks/iris_task_app.py`
  - **Current**: Stores `template_messages` in `step.info.messages` (lines 206-220)
  - **Action**: Remove `template_messages` storage, ensure `inference_url` has `?cid=...`
  - **Status**: ✅ **NEEDS UPDATE** - Confirmed stores messages

- [ ] `examples/task_apps/gepa_benchmarks/hotpotqa_task_app.py`
  - **Current**: Stores `template_messages` in `step.info.messages` (lines 237-254)
  - **Action**: Remove `template_messages` storage, ensure `inference_url` has `?cid=...`
  - **Status**: ✅ **NEEDS UPDATE** - Confirmed stores messages

#### ✅ Verified: No Messages Storage (No Update Needed)
- [x] `examples/task_apps/gepa_benchmarks/pupa_task_app.py`
  - **Verified**: Does NOT store `step.info.messages` (only `info_payload` without messages)
  - **Action**: **NO UPDATE NEEDED** - Already correct
  - **Status**: ✅ **NO CHANGE**

- [x] `examples/task_apps/gepa_benchmarks/ifbench_task_app.py`
  - **Verified**: Does NOT store `step.info.messages` (only `eval_details` without messages)
  - **Action**: **NO UPDATE NEEDED** - Already correct
  - **Status**: ✅ **NO CHANGE**

- [x] `examples/task_apps/gepa_benchmarks/hover_task_app.py`
  - **Verified**: Does NOT store `step.info.messages` (only `info_payload` without messages)
  - **Action**: **NO UPDATE NEEDED** - Already correct
  - **Status**: ✅ **NO CHANGE**

- [x] `examples/task_apps/other_langprobe_benchmarks/gsm8k_task_app.py`
  - **Verified**: Does NOT store `step.info.messages` (only `info_payload` without messages)
  - **Action**: **NO UPDATE NEEDED** - Already correct
  - **Status**: ✅ **NO CHANGE**

- [x] `examples/task_apps/other_langprobe_benchmarks/heartdisease_task_app.py`
  - **Verified**: Does NOT store `step.info.messages` (only `info_payload` without messages)
  - **Action**: **NO UPDATE NEEDED** - Already correct
  - **Status**: ✅ **NO CHANGE**

#### 📝 Documentation Updates
- [ ] `monorepo/docs/task-app/pl.mdx` (line 18)
  - **Current**: Documents `step.info.messages` requirement
  - **Action**: Update to document `inference_url` with `?cid=...` instead
  - **Status**: Needs update

### Category 2: MIPRO Adapters (Migrate to `MIPROConfig.simple()`)

**Priority: MEDIUM** - Single-stage adapters should use simpler API.

#### Single-Stage Adapters (Should Use `MIPROConfig.simple()`)
- [ ] `examples/blog_posts/langprobe/integrations/synth_mipro_adapter_inprocess.py`
  - **Current**: Uses full `MIPROConfig()` constructor (lines 207-242)
  - **Action**: Migrate to `MIPROConfig.simple()` for single-stage tasks
  - **Note**: Check if `task_app_id` indicates single-stage (Iris) vs multi-stage
  - **Status**: Needs update

- [ ] `examples/blog_posts/langprobe/task_specific/iris/synth_iris_adapter.py`
  - **Current**: Uses `SynthMIPROAdapterInProcess` (which uses full constructor)
  - **Action**: Update to use `MIPROConfig.simple()` for Iris
  - **Status**: Needs update

- [ ] `examples/blog_posts/langprobe/task_specific/iris/run_mipro_local.py`
  - **Current**: Uses full `MIPROConfig()` constructor (line 159)
  - **Action**: Migrate to `MIPROConfig.simple()` for Iris
  - **Status**: Needs update

#### Multi-Stage Adapters (Keep Full Constructor)
- [ ] `examples/blog_posts/langprobe/task_specific/hotpotqa/synth_hotpotqa_adapter.py`
  - **Current**: Uses `SynthMIPROAdapterInProcess` (which uses full constructor)
  - **Action**: **NO CHANGE** - HotpotQA is multi-stage, keep full constructor
  - **Status**: No update needed

#### Backend Examples (Keep Full Constructor - Multi-Stage)
- [ ] `monorepo/backend/app/routes/prompt_learning/examples/test_mipro_banking77.py`
  - **Action**: **NO CHANGE** - May be multi-stage, verify first
  - **Status**: Verify

- [ ] `monorepo/scripts/run_local_mipro.py`
  - **Action**: **NO CHANGE** - Likely multi-stage (banking77_pipeline)
  - **Status**: Verify

### Category 3: GEPA Adapters (No Changes Needed)

**Priority: LOW** - GEPA doesn't have single-stage simplification yet.

#### GEPA Adapters (No Changes)
- [ ] `examples/blog_posts/langprobe/integrations/synth_gepa_adapter_inprocess.py`
  - **Current**: Uses `GEPAConfig()` constructor (lines 243-265)
  - **Action**: **NO CHANGE** - GEPA simplification not in scope
  - **Status**: No update needed

- [ ] `examples/blog_posts/langprobe/task_specific/iris/synth_iris_adapter.py`
  - **Action**: **NO CHANGE** - GEPA simplification not in scope
  - **Status**: No update needed

- [ ] `examples/blog_posts/langprobe/task_specific/hotpotqa/synth_hotpotqa_adapter.py`
  - **Action**: **NO CHANGE** - GEPA simplification not in scope
  - **Status**: No update needed

### Category 4: Test Files

**Priority: MEDIUM** - Tests should reflect new patterns.

#### MIPRO Tests
- [ ] `tests/unit/learning/test_mipro_spec_config.py`
  - **Action**: Update if tests construct `MIPROConfig()` for single-stage
  - **Status**: Verify

- [ ] `tests/integration/test_spec_with_mipro.py`
  - **Action**: Update if tests construct `MIPROConfig()` for single-stage
  - **Status**: Verify

- [ ] `tests/integration/cli/test_cli_train_mipro_banking77.py`
  - **Action**: Update if tests construct `MIPROConfig()` for single-stage
  - **Status**: Verify

- [ ] `monorepo/tests/backend/unit/prompt_learning/test_mipro_pipeline_baselines.py`
  - **Action**: **NO CHANGE** - Pipeline tests should use full constructor
  - **Status**: No update needed

- [ ] `monorepo/backend/tests/unit/prompt_learning/test_mipro_spec_mode.py`
  - **Action**: Update if tests construct `MIPROConfig()` for single-stage
  - **Status**: Verify

#### GEPA Tests
- [ ] `tests/unit/learning/test_gepa_spec_config.py`
  - **Action**: **NO CHANGE** - GEPA simplification not in scope
  - **Status**: No update needed

- [ ] `tests/unit/api/train/configs/test_gepa_module_config.py`
  - **Action**: **NO CHANGE** - GEPA simplification not in scope
  - **Status**: No update needed

- [ ] `tests/integration/cli/test_cli_train_gepa_banking77.py`
  - **Action**: **NO CHANGE** - GEPA simplification not in scope
  - **Status**: No update needed

- [ ] `monorepo/tests/backend/integration/prompt_learning/test_gepa_multistage_constraints.py`
  - **Action**: **NO CHANGE** - Multi-stage tests
  - **Status**: No update needed

### Category 5: Config Files (TOML)

**Priority: LOW** - TOML files should work with new parser (backward compatible).

#### MIPRO TOML Configs
- [ ] `examples/blog_posts/mipro/configs/banking77_mipro_local.toml`
  - **Action**: Verify works with new `MIPROConfigFromTOML` parser
  - **Status**: Verify

- [ ] `examples/blog_posts/mipro/configs/banking77_mipro_test.toml`
  - **Action**: Verify works with new `MIPROConfigFromTOML` parser
  - **Status**: Verify

- [ ] `examples/blog_posts/mipro/configs/banking77_pipeline_mipro_local.toml`
  - **Action**: **NO CHANGE** - Multi-stage config, should work as-is
  - **Status**: Verify

- [ ] `examples/blog_posts/mipro/configs/banking77_pipeline_mipro_test.toml`
  - **Action**: **NO CHANGE** - Multi-stage config, should work as-is
  - **Status**: Verify

- [ ] `examples/blog_posts/mipro/configs/banking77_pipeline_mipro_gemini_flash_lite_local.toml`
  - **Action**: **NO CHANGE** - Multi-stage config
  - **Status**: Verify

- [ ] `examples/blog_posts/mipro/configs/banking77_pipeline_mipro_gpt41mini_local.toml`
  - **Action**: **NO CHANGE** - Multi-stage config
  - **Status**: Verify

- [ ] `monorepo/backend/app/routes/prompt_learning/configs/banking77_mipro_test.toml`
  - **Action**: Verify works with new parser
  - **Status**: Verify

- [ ] `monorepo/backend/app/routes/prompt_learning/configs/banking77_mipro_smoke_test.toml`
  - **Action**: Verify works with new parser
  - **Status**: Verify

- [ ] `monorepo/backend/app/routes/prompt_learning/configs/banking77_mipro_large.toml`
  - **Action**: Verify works with new parser
  - **Status**: Verify

#### GEPA TOML Configs (No Changes)
- [ ] All GEPA TOML configs in `examples/blog_posts/gepa/configs/`
  - **Action**: **NO CHANGE** - GEPA simplification not in scope
  - **Status**: No update needed

### Category 6: Documentation & READMEs

**Priority: MEDIUM** - Documentation should reflect new patterns.

#### README Files
- [ ] `examples/blog_posts/mipro/README.md`
  - **Action**: Update examples to show `MIPROConfig.simple()` for single-stage
  - **Status**: Needs update

- [ ] `examples/blog_posts/gepa/README.md`
  - **Action**: Update to document `inference_url` with `?cid=...` requirement
  - **Status**: Needs update

- [ ] `examples/blog_posts/langprobe/task_specific/iris/README.md`
  - **Action**: Update to show `MIPROConfig.simple()` usage
  - **Status**: Needs update

- [ ] `examples/blog_posts/langprobe/task_specific/hotpotqa/README.md` (if exists)
  - **Action**: Document multi-stage uses full constructor
  - **Status**: Verify

#### Documentation Files
- [ ] `monorepo/docs/po/config.mdx`
  - **Action**: Update MIPRO examples to show `simple()` for single-stage
  - **Status**: Needs update

- [ ] `monorepo/docs/po/examples/overview.mdx`
  - **Action**: Update examples if needed
  - **Status**: Verify

- [ ] `monorepo/docs/task-app/pl.mdx`
  - **Action**: Remove `step.info.messages` requirement, document `inference_url` with `?cid=...`
  - **Status**: Needs update

### Category 7: Example Scripts & Demos

**Priority: LOW** - Example scripts should demonstrate best practices.

#### MIPRO Example Scripts
- [ ] `examples/blog_posts/mipro/run_mipro_banking77.sh`
  - **Action**: Verify still works with new parser
  - **Status**: Verify

- [ ] `examples/blog_posts/mipro/run_mipro_banking77_pipeline.sh`
  - **Action**: **NO CHANGE** - Multi-stage script
  - **Status**: Verify

- [ ] `monorepo/scripts/run_local_mipro.py`
  - **Action**: Verify if single-stage or multi-stage, update accordingly
  - **Status**: Verify

#### GEPA Example Scripts
- [ ] `examples/blog_posts/gepa/run_gepa_banking77.sh`
  - **Action**: **NO CHANGE** - GEPA simplification not in scope
  - **Status**: No update needed

- [ ] `examples/blog_posts/gepa/run_gepa_banking77_pipeline.sh`
  - **Action**: **NO CHANGE** - Multi-stage script
  - **Status**: No update needed

- [ ] `monorepo/scripts/run_local_gepa.py`
  - **Action**: **NO CHANGE** - GEPA simplification not in scope
  - **Status**: No update needed

### Category 8: SDK/API Config Classes

**Priority: LOW** - These are API definitions, not examples.

#### Config Class Definitions
- [ ] `synth_ai/api/train/configs/prompt_learning.py`
  - **Current**: Defines `MIPROConfig` and `GEPAConfig` classes
  - **Action**: Add `MIPROConfig.simple()` classmethod
  - **Status**: Needs update

- [ ] `monorepo/backend/app/routes/prompt_learning/algorithm/mipro/config.py`
  - **Current**: Defines `MIPROConfig` dataclass
  - **Action**: Add `MIPROConfig.simple()` classmethod
  - **Status**: Needs update

## Update Priority Summary

### 🔴 HIGH PRIORITY (Must Update)
1. **Task Apps** - Remove `step.info.messages` storage:
   - ✅ `iris_task_app.py` - **CONFIRMED** stores messages
   - ✅ `hotpotqa_task_app.py` - **CONFIRMED** stores messages
   - ✅ Other gepa_benchmarks task apps - **VERIFIED** do NOT store messages (no update needed)

2. **Documentation** - Update requirements:
   - `monorepo/docs/task-app/pl.mdx`

### 🟡 MEDIUM PRIORITY (Should Update)
1. **Single-Stage MIPRO Adapters** - Migrate to `MIPROConfig.simple()`:
   - `synth_mipro_adapter_inprocess.py` (for single-stage tasks)
   - `synth_iris_adapter.py` (MIPRO parts)
   - `run_mipro_local.py` (if single-stage)

2. **Test Files** - Update tests to use new patterns:
   - MIPRO single-stage tests

3. **README Files** - Update documentation:
   - `examples/blog_posts/mipro/README.md`
   - `examples/blog_posts/langprobe/task_specific/iris/README.md`

### 🟢 LOW PRIORITY (Nice to Have)
1. **Config Files** - Verify TOML parsing works (should be backward compatible)
2. **Example Scripts** - Verify still work
3. **GEPA Adapters** - No changes needed (simplification not in scope)

## Update Strategy

### Phase 1: Task Apps (Step.info Removal)
1. Remove `template_messages` storage from all task apps
2. Ensure `inference_url` has `?cid=...` (trainer adds this automatically)
3. Verify `mean_return` is used for scoring (not `outcome_score`)

### Phase 2: Single-Stage MIPRO Migration
1. Identify single-stage vs multi-stage tasks
2. Migrate single-stage adapters to `MIPROConfig.simple()`
3. Keep multi-stage adapters using full constructor

### Phase 3: Documentation Updates
1. Update task app requirements documentation
2. Update MIPRO examples to show `simple()` API
3. Update README files

### Phase 4: Test Updates
1. Update tests to use new patterns
2. Add tests for `MIPROConfig.simple()`
3. Verify backward compatibility tests pass

## Verification Checklist

After updates, verify:
- [ ] All task apps removed `step.info.messages` storage
- [ ] All single-stage MIPRO adapters use `MIPROConfig.simple()`
- [ ] All multi-stage MIPRO adapters use full constructor (unchanged)
- [ ] All tests pass
- [ ] All TOML configs still work (backward compatibility)
- [ ] Documentation is updated
- [ ] No stale examples remain

## Notes

- **GEPA simplification**: Not in scope for this refactor - GEPA adapters don't need changes
- **Multi-stage**: Full `MIPROConfig()` constructor remains unchanged - no updates needed
- **Backward compatibility**: TOML parser should support both old and new formats during migration
- **Task apps**: Only need to remove `step.info.messages`, everything else stays the same

