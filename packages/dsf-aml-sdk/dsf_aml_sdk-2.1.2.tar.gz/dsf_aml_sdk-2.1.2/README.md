DSF AML SDK
Fix ML failures in production → Generate critical variants automatically → Retrain in <30s

🎯 Primary Use Cases
1. 🔥 Failure Correction Loop (Production-Ready)
Problem: When your LLM/ML model fails in production (adversarial prompt, edge case), fixing it is slow and manual.
Solution: API takes the failure as seed → generates critical variants automatically → delivers labeled dataset for retraining.
pythonfrom dsf_aml_sdk import AMLSDK, Config

sdk = AMLSDK(license_key='PRO-XXXX', tier='professional')

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

💡 What are variants? Each variant represents a new, labeled data point similar to the failure case, designed to improve robustness during retraining.

Differentiator: Automated end-to-end in <30s. No ML expertise required. No direct competitors.

2. 🛡️ Preventive Robustness Datasets
Problem: Models trained on clean data fail on edge cases and adversarial inputs.
Solution: Pre-generate datasets focused on decision boundaries before deployment.
pythonfrom dsf_aml_sdk import AMLSDK, Config

sdk = AMLSDK(license_key='PRO-XXXX', tier='professional')

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
Differentiator: Automated uncertainty-based curation. No packaged competitor.

🚀 Why DSF AML?
Competitive landscape gaps:

Scale AI/Gretel: Generic synthetic data (no failure focus)
Cleanlab/Snorkel: Clean existing data (don't generate variants)
Lakera/Giskard: Test post-deployment (don't generate retraining data)

Your position: Only automated pipeline from failure → variants → labeled datasets.

⚙️ Architecture Overview
SDK:      pip install dsf-aml-sdk
All requests route through /api/evaluate → serverless architecture with no local dependencies.

📦 Installation
bashpip install dsf-aml-sdk

🎯 Quick Start: Failure Correction
pythonfrom dsf_aml_sdk import AMLSDK, Config

sdk = AMLSDK(license_key='PRO-2026-12-31-XXXX', tier='professional')

# 💡 Config defines metrics your model evaluates (accuracy, latency, etc.)
config = (sdk.create_config()
    .add_field('model_accuracy', 0.95, 2.5, 2.0)
    .add_field('latency_ms', 100, 1.8, 1.5)
    .add_field('error_rate', 0.05, 2.2, 2.5)
)

# 1. Report failure
failed_input = {'model_accuracy': 0.60, 'latency_ms': 500, 'error_rate': 0.20}

# 2. Generate correction variants
fix = sdk.fix_failure(failed_input, config)

# 3. Use fix['critical_samples'] to retrain
print(f"Generated {len(fix['critical_samples'])} variants for retraining")

💡 Secondary Benefit: Knowledge Distillation
Train lightweight surrogates for 10-50× faster inference with minimal data:
pythonfrom dsf_aml_sdk import AMLSDK, Config

sdk = AMLSDK(license_key='PRO-XXXX', tier='professional')

# Distill complex scoring logic into fast surrogate
sdk.distill_train(config, samples=1000, batch_size=100)

# Sub-millisecond CPU inference
score = sdk.distill_predict(sample, config)  # typically <1ms

# Batch scoring (70-90% less data needed)
scores = sdk.distill_predict_batch(dataset, config)
Use when: You need high-throughput scoring without GPUs.

🆚 Tier Comparison

| Feature                | Community         |   Professional     |    Enterprise       |
|------------------------|------------------:|-------------------:|--------------------:|
| Failure correction     | ❌                |  ✅               | ✅ (unlimited)      |
| Preventive datasets    | Limited (100/day) |  ✅               | ✅ (full pipeline)  |
| Batch evaluation       | ❌                |  ✅ (≤1000)       | ✅ (≤1000)          |
| Distillation           | ❌                |  ✅               | ✅ + export         |
| Full cycle pipeline    | ❌                |  ❌               | ✅                  |


📖 Core Methods
Failure Correction
pythonsdk.fix_failure(failed_input: dict, config, k_variants=20) → dict
Preventive Datasets
pythonsdk.pipeline_identify_seeds(dataset, config, top_k_percent=0.1) → dict
sdk.pipeline_generate_critical(config, original_dataset, **kwargs) → dict
Distillation
pythonsdk.distill_train(config, samples=1000) → dict
sdk.distill_predict(data: dict, config) → float
sdk.distill_predict_batch(data_batch, config) → list[float]

📈 ROI Metrics
Failure Correction

⏱ Time to fix: Hours → <30s
🧩 Downtime reduction: 80–95%

Preventive Datasets

📉 Data volume reduction: 70–90%
🧠 Model robustness: +40–60%
💰 Infrastructure savings: ~85%


📞 Support

Docs: https://dsfuptech.cloud
Issues: contacto@dsfuptech.cloud
Enterprise: contacto@dsfuptech.cloud


📄 License
Proprietary — © 2025 Jaime Alexander Jimenez, operating as "Uptech"
DSF AML SDK and DSF Quantum SDK are licensed software products.
Community tier for non-commercial use. Professional and Enterprise require valid license key.
