# DSF AML SDK

**Fix ML failures in production → Generate critical variants automatically → Retrain in <30s**

---

## 🎯 Primary Use Cases

### 1. 🔥 Failure Correction Loop (Production-Ready)

**Problem:** When your LLM/ML model fails in production (adversarial prompt, edge case), fixing it is slow and manual.

**Solution:** API takes the failure as seed → generates critical variants automatically → delivers labeled dataset for retraining.

```python
from dsf_aml_sdk import AMLSDK

sdk = AMLSDK(license_key='PRO-2026-12-31-XXXX', tier='professional')

# Production failure detected
failed_case = {'input': 'malicious prompt', 'context': {...}}

# Generate variants for retraining
variants = sdk.fix_failure(
    failed_input=failed_case,
    config=your_config,
    k_variants=20
)

# Retrain your model with variants['critical_samples']
# → Model now robust to similar attacks
```

💡 **What are variants?** Each variant represents a new, labeled data point similar to the failure case, designed to improve robustness during retraining.

**Differentiator:** Automated end-to-end in <30s. No ML expertise required. No direct competitors.

---

### 2. 🛡️ Preventive Robustness Datasets

**Problem:** Models trained on clean data fail on edge cases and adversarial inputs.

**Solution:** Pre-generate datasets focused on decision boundaries before deployment.

```python
from dsf_aml_sdk import AMLSDK

sdk = AMLSDK(license_key='PRO-2026-12-31-XXXX', tier='professional')

# Before deployment: curate critical training data
seeds = sdk.pipeline_identify_seeds(
    dataset=training_data,
    config=config,
    top_k_percent=0.1  # Focus on hardest 10%
)

# Generate synthetic variants at boundaries
critical_data = sdk.pipeline_generate_critical(
    config=config,
    original_dataset=training_data,
    k_variants=10,
    epsilon=0.08
)

# Train model with critical_data → 70-90% less data, more robust
```

**Differentiator:** Automated uncertainty-based curation. No packaged competitor.

---

### 3. 📊 Labeled Training Data Generation

**Problem:** Creating high-quality labeled datasets for ML training is expensive and time-consuming.

**Solution:** Generate synthetic labeled datasets at scale for training your own models.

```python
from dsf_aml_sdk import AMLSDK

sdk = AMLSDK(license_key='PRO-2026-12-31-XXXX', tier='professional')

# Generate 1000 labeled samples
result = sdk.distill_train(config, samples=1000)

# Export for training (Enterprise)
dataset = sdk.distill_export()

# Use dataset['distilled_samples'] to train YOUR model
# Each sample contains: features + target_score
# → Train sklearn, PyTorch, TensorFlow models with 70-90% less data
```

💡 **What you receive:** A ready-to-use dataset with pre-computed labels based on your config. Perfect for training lightweight surrogates or custom ML models.

**Differentiator:** Automated data generation focused on critical regions. 10-50× faster training with minimal data.

---

## 🚀 Why DSF AML?

**Competitive landscape gaps:**

- **Scale AI/Gretel:** Generic synthetic data (no failure focus)
- **Cleanlab/Snorkel:** Clean existing data (don't generate variants)
- **Lakera/Giskard:** Test post-deployment (don't generate retraining data)

**Your position:** Only automated pipeline from failure → variants → labeled datasets.

---

## 📦 Installation

```bash
pip install dsf-aml-sdk
```

---

## 🎯 Quick Start: Failure Correction

```python
from dsf_aml_sdk import AMLSDK

sdk = AMLSDK(license_key='PRO-2026-12-31-XXXX', tier='professional')

# 💡 Config defines metrics your model evaluates (accuracy, latency, etc.)
config = {
    'model_accuracy': {'default': 0.95, 'weight': 2.5, 'criticality': 2.0},
    'latency_ms': {'default': 100, 'weight': 1.8, 'criticality': 1.5},
    'error_rate': {'default': 0.05, 'weight': 2.2, 'criticality': 2.5}
}

# 1. Report failure
failed_input = {'model_accuracy': 0.60, 'latency_ms': 500, 'error_rate': 0.20}

# 2. Generate correction variants
fix = sdk.fix_failure(failed_input, config, k_variants=20)

# 3. Use fix['critical_samples'] to retrain
print(f"Generated {len(fix['critical_samples'])} variants for retraining")
print(f"Metrics: {fix['metrics']}")
```

---

## 📊 Model Metrics (Professional & Enterprise)

All heavy operations return comprehensive metrics:

```python
{
  "tier": "professional",
  "evaluations": 62,
  "threshold": 0.6698,
  "storage": "redis",
  "avg_score": 0.7296,
  "min_score": 0.5217,
  "max_score": 0.8467
}
```

**Metrics explanation:**
- `evaluations`: Total number of evaluations processed
- `threshold`: Adaptive decision threshold
- `storage`: Persistence layer (redis = persistent, memory = ephemeral)
- `avg_score/min_score/max_score`: Score statistics

---

🆚 Tier Comparison

| Feature                | Community         |   Professional     |    Enterprise       |
|------------------------|------------------:|-------------------:|--------------------:|
| Failure correction     | ❌                |  ✅               | ✅ (unlimited)      |
| Preventive datasets    | Limited (100/day) |  ✅                | ✅ (full pipeline)  |
| Batch evaluation       | ❌                |  ✅ (≤1000)       | ✅ (≤1000)          |
| Distillation           | ❌                |  ✅               | ✅ + export         |
| Full cycle pipeline    | ❌                |  ❌               | ✅                  |

---

## 📖 Core Methods

### Failure Correction

```python
sdk.fix_failure(failed_input: dict, config, k_variants=20) → dict
```

Returns:
```python
{
  "status": "completed",
  "total_generated": 20,
  "critical_samples": [...],
  "metrics": {...}
}
```

### Preventive Datasets

```python
sdk.pipeline_identify_seeds(dataset, config, top_k_percent=0.1) → dict
sdk.pipeline_generate_critical(config, original_dataset, **kwargs) → dict
```

### Labeled Data Generation

```python
sdk.distill_train(config, samples=1000) → dict  # Generate labeled dataset
sdk.distill_export() → dict  # Export for training (Enterprise)
```

### Evaluation

```python
# Individual evaluation
result = sdk.evaluate(data, config)
print(f"Score: {result.score}")
print(f"Metrics: {result.metrics}")  # Now included

# Batch evaluation
results = sdk.batch_evaluate(data_points, config)
scores = [r.score for r in results]
metrics = results[0].batch_metrics  # Batch metrics available
```

---

## 📈 ROI Metrics

### Failure Correction
- ⏱ **Time to fix:** Hours → <30s
- 🧩 **Downtime reduction:** 80–95%

### Preventive Datasets
- 📉 **Data volume reduction:** 70–90%
- 🧠 **Model robustness:** +40–60%
- 💰 **Infrastructure savings:** ~85%

### Labeled Data Generation
- 📊 **Data generation speed:** 10-50× faster than manual labeling
- 🎯 **Training efficiency:** 70-90% less data needed
- 💸 **Cost savings:** ~90% vs. human labeling

---

## 🔧 Advanced Configuration

### Config Structure

```python
config = {
    "feature_name": {
        "default": <ideal_value>,      # Target value
        "weight": <float, 1.0–5.0>,    # Feature importance
        "criticality": <float, 1.0–5.0> # Sensitivity to deviations
    }
}
```

### Example: Credit Scoring

```python
config = {
    'credit_score': {'default': 650, 'weight': 2.5, 'criticality': 2.0},
    'person_income': {'default': 60000, 'weight': 2.0, 'criticality': 1.8},
    'loan_percent_income': {'default': 0.20, 'weight': 2.2, 'criticality': 2.5},
    'previous_defaults': {'default': 'No', 'weight': 2.0, 'criticality': 1.0}
}
```

---

## 🛠️ Complete Example

```python
import pandas as pd
from dsf_aml_sdk import AMLSDK

# Load data
df = pd.read_csv('loan_data.csv')
data = df[['credit_score', 'person_income', 'loan_percent_income']].head(100).to_dict('records')

# Initialize SDK
sdk = AMLSDK(license_key='PRO-2026-12-31-XXXX', tier='professional')

# Define config
config = {
    'credit_score': {'default': 650, 'weight': 2.5, 'criticality': 2.0},
    'person_income': {'default': 60000, 'weight': 2.0, 'criticality': 1.8},
    'loan_percent_income': {'default': 0.20, 'weight': 2.2, 'criticality': 2.5}
}

# TEST 1: Fix production failure
failed_case = {
    'credit_score': 580,
    'person_income': 35000,
    'loan_percent_income': 0.45
}

fix = sdk.fix_failure(failed_input=failed_case, config=config, k_variants=10)
print(f"✅ Generated {fix['total_generated']} variants")
print(f"📊 Metrics: {fix['metrics']}")

# TEST 2: Preventive dataset
seeds = sdk.pipeline_identify_seeds(dataset=data[:50], config=config, top_k_percent=0.15)
critical_data = sdk.pipeline_generate_critical(config=config, original_dataset=data[:50], k_variants=20)
print(f"✅ Critical dataset: {critical_data['total_generated']} variants")

# TEST 3: Labeled data generation
result = sdk.distill_train(config, samples=200)
print("✅ Labeled dataset generated")

# TEST 4: Individual evaluation
test_case = data[0]
result = sdk.evaluate(test_case, config)
print(f"📈 Score: {result.score:.3f}")
print(f"📊 Metrics: {result.metrics}")

# TEST 5: Batch evaluation
batch_results = sdk.batch_evaluate(data[:10], config)
print(f"📊 Avg score: {sum(r.score for r in batch_results)/len(batch_results):.3f}")
print(f"📊 Batch metrics: {batch_results[0].batch_metrics}")
```

---

## 📞 Support

- **Docs:** https://dsfuptech.cloud
- **Issues:** contacto@dsfuptech.cloud
- **Enterprise:** contacto@dsfuptech.cloud

---

## 📄 License

**Proprietary** — © 2025 Jaime Alexander Jimenez, operating as "Uptech"

DSF AML SDK and DSF Quantum SDK are licensed software products.

- **Community tier:** Non-commercial use
- **Professional/Enterprise:** Requires valid license key

Contact: contacto@dsfuptech.cloud
