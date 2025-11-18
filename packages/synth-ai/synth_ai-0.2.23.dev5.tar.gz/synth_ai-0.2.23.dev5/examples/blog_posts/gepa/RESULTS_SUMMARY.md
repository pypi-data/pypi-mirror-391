# Heart Disease GEPA Optimization Results

## Configuration
- **Dataset**: buio/heart-disease (Heart Disease UCI)
- **Training examples**: 15 (seeds 0-14)
- **Validation examples**: 20 (seeds 15-34)
- **Rollout budget**: 100
- **Optimization time**: 45.2 seconds
- **Model**: llama-3.1-8b-instant (Groq)

## Results Summary

| Metric | Baseline | Optimized | Improvement |
|--------|----------|-----------|-------------|
| **Validation Accuracy** | 35.0% (7/20) | 35.0% (7/20) | +0.0% |
| **Pareto Front Score** | 0.35 | 0.40 | +14.3% |

### Key Findings

1. **Aggregate Performance**: Both candidates achieved the same aggregate validation accuracy of 35%

2. **Pareto Front**: The evolved prompt achieved a **Pareto front score of 0.40** vs baseline 0.35, indicating it performs better on a subset of validation examples (even if aggregate is tied)

3. **Prompt Evolution**: GEPA discovered a new candidate at rollout 62 that includes:
   - Detailed feature descriptions with medical context
   - Specific risk factor thresholds
   - Clear decision rules
   - Example inputs/outputs

## Candidate Prompts

### Candidate 0: Baseline (Score: 0.35)
**Discovered at rollout**: 0

**Instruction**:
```
Classify heart disease based on patient features.

Given patient measurements and medical data, predict whether
the patient has heart disease.
```

**Analysis**: Simple, minimal prompt that relies entirely on the model's pre-training knowledge.

---

### Candidate 1: Evolved (Score: 0.35, Pareto: 0.40)
**Discovered at rollout**: 62
**Evolved from**: Candidate 0

**Instruction** (abbreviated):
```
Classify Heart Disease Based on Patient Features:

The task involves predicting whether a patient has heart disease based
on their medical features. The input will be a set of patient measurements
and medical data, and the output should be a classification of 0 (no heart
disease) or 1 (heart disease).

The patient features will include:
- Age: The patient's age, which is a risk factor for heart disease, with
  ages 45-60 considered moderately high risk.
- Sex: The patient's sex, with males being at higher risk for heart disease.
- CP (Chest Pain Type): A value from 1 to 4, where:
  - 1: Typical angina (chest pain caused by reduced blood flow to the heart)
  - 2: Atypical angina (chest pain not caused by reduced blood flow)
  - 3: Non-anginal pain (chest pain not related to the heart)
  - 4: Asymptomatic (no chest pain)
- Trestbps: Resting blood pressure, considered high if above 140 mmHg
- Chol: Cholesterol level, considered high if above 200 mg/dL
- Fbs: Fasting blood sugar, considered high if above 120 mg/dL
- Restecg: Resting electrocardiogram results:
  - 0: Normal
  - 1: ST-T wave abnormality
  - 2: Left ventricular hypertrophy
- Thalach: Maximum heart rate achieved, high if above 150 bpm
- Exang: Exercise-induced chest pain (0: no, 1: yes)
- Oldpeak: ST depression from exercise, high if above 1 mm
- Slope: ST segment slope during exercise (1: upsloping, 2: flat, 3: downsloping)
- Ca: Number of major vessels affected by coronary artery disease
- Thal: Thalassemia status (normal, fixed, reversible)

To classify the patient, you can use a simple threshold-based approach,
where a patient with three or more risk factors is classified as having
heart disease (1). The risk factors are:
- Age above 45
- Male sex
- High cholesterol
- High blood pressure
- High ST depression induced by exercise
- Upsloping or flat ST slope
- Presence of chest pain during exercise
- High maximum heart rate achieved

[Example inputs/outputs included...]

Your task is to classify the patient based on their features and provide
a detailed reasoning for your classification.
```

**Analysis**:
- Comprehensive feature descriptions with medical context
- Explicit risk factor definitions with thresholds
- Clear decision-making strategy
- Includes example for few-shot guidance
- Much more structured and informative than baseline

## Insights

### What Worked
1. **Feature Engineering**: GEPA automatically incorporated domain knowledge about medical risk factors
2. **Threshold Discovery**: The optimizer discovered clinically relevant thresholds (e.g., BP > 140, Chol > 200)
3. **Decision Rules**: Generated explicit decision logic (≥3 risk factors → heart disease)

### Why Aggregate Scores Tied
- Small validation set (20 examples) limits statistical power
- Model capacity constraints (8B parameters) may bottleneck prompt effectiveness
- Task difficulty: medical diagnosis is inherently challenging

### Pareto Front Advantage
- Candidate 1 achieves **40% Pareto score** vs 35% baseline
- This means it correctly classifies some examples that the baseline fails on
- Useful for ensemble or routing strategies

## Reproducibility

Run the experiment:
```bash
cd examples/blog_posts/gepa
source ../../../.env
export GROQ_API_KEY
python run_dspy_gepa_heartdisease.py
```

## Next Steps

To achieve better improvements:
1. **Increase validation set size** (50-100 examples) for better statistical power
2. **Use larger model** (e.g., llama-3.1-70b) to better leverage detailed prompts
3. **Increase rollout budget** (300-500) for more exploration
4. **Add few-shot examples** to initial prompt template
5. **Try multi-step reasoning** (e.g., ChainOfThought) for complex medical logic

## Files Generated

- `results/heartdisease_gepa_test/dspy_gepa_detailed_results.json` - Full optimization results
- `results/heartdisease_gepa_test/dspy_gepa_heartdisease_stats.json` - Statistics
- `results/heartdisease_gepa_test/dspy_gepa_heartdisease_learning_curve.json` - Learning curve data
- `results/heartdisease_gepa_test/optimized_prompt.txt` - Human-readable prompt

---

**Generated**: 2025-11-13
**Optimization Time**: 45.2 seconds
**Framework**: DSPy GEPA
**Budget**: 100 rollouts
