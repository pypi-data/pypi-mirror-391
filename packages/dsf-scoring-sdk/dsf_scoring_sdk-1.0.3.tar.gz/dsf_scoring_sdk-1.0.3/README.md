# DSF Adaptive Scoring SDK

An **enterprise-grade adaptive credit scoring system** that replaces static risk models and hard-coded rules with a configurable, intelligent decision engine.

---

## 🚀 Why DSF Scoring?

Traditional risk models are static — they’re trained once and quickly become outdated, failing to adapt to new market conditions or applicant behaviors.  
The DSF Scoring SDK transforms your credit logic into a **configurable, self-adjusting scoring engine** that evolves based on real-world data and context.

---

## 🧠 Core Concepts

Instead of rigid, static rules (e.g., “DTI must be < 0.4”), DSF lets you define risk policies as weighted **features**.  
The system then evaluates how well each applicant matches an *ideal profile*, producing a dynamic **credit score**.

This shifts your scoring logic from hard-coded rules to a **living configuration** that’s easy to maintain and evolve.

---

## ⚙️ Installation

```bash
pip install dsf-scoring-sdk
💡 Ensure the package name dsf-scoring-sdk matches your PyPI registration.

🧩 Quick Start
Community Edition (Free)
Perfect for testing, MVPs, or low-volume use.

python
Copiar código
from dsf_scoring_sdk import CreditScoreClient, LicenseError

# 1. Configure your features
config = {
    "monthly_income": {"default": 3000, "weight": 1.8, "criticality": 2.0},
    "debt_to_income": {"default": 0.3, "weight": 2.5, "criticality": 3.0}
}

# 2. Define the applicant
applicant = {"monthly_income": 2800, "debt_to_income": 0.42}

# 3. Evaluate
try:
    with CreditScoreClient(api_key="dsf_api_prod_XXXXX", tier="community") as client:
        result = client.evaluate(applicant, config)
        print(f"Decision: {result['decision']}")
        print(f"Score: {result['score']:.4f}")
        print(f"Threshold: {result['threshold']}")
except LicenseError as e:
    print(f"License Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
Professional Edition (Batch Processing)
python
Copiar código
from dsf_scoring_sdk import CreditScoreClient

client = CreditScoreClient(
    api_key="dsf_api_prod_XXXXX",
    tier="professional",
    license_key="PRO-2026-12-31-XXXX-XXXX"
)

# (Config from previous example)
applicants = [
    {"monthly_income": 5000, "debt_to_income": 0.25},
    {"monthly_income": 2100, "debt_to_income": 0.55},
    {"monthly_income": 3100, "debt_to_income": 0.31}
]

results = client.evaluate_batch(applicants, config)

print(f"Adaptive Threshold: {results['threshold']:.4f}")
print(f"Batch Decisions: {results['decisions']}")
print(f"Batch Scores: {results['scores']}")

client.close()
Enterprise Edition (Adaptive Weighting)
python
Copiar código
from dsf_scoring_sdk import CreditScoreClient

client = CreditScoreClient(
    api_key="dsf_api_prod_XXXXX",
    tier="enterprise",
    license_key="ENT-2026-12-31-XXXX-XXXX"
)

result = client.evaluate(applicant, config)
metrics = result.get('metrics', {})

print(f"Enterprise Metrics: {metrics}")
# Output:
# { ... 'adaptive_weights': True, 'adjustment_factor': 0.3, ... }
🤖 Hybrid Model Integration
You can integrate machine learning models or third-party risk systems directly into your scoring pipeline.

FICO + Internal Model Example
python
Copiar código
# 1. Load your internal model
risk_model = load_my_internal_model('risk_v2.pkl')

# 2. Define a hybrid configuration
hybrid_config = {
    "fico_score": {"default": 720, "weight": 2.0, "criticality": 2.0},
    "employment_months": {"default": 36, "weight": 1.5, "criticality": 1.0},
    "internal_risk_score": {"default": 0.15, "weight": 2.5, "criticality": 3.0}
}

# 3. Evaluate with hybrid inputs
def evaluate_hybrid_applicant(user_data):
    internal_score = risk_model.predict_proba(user_data)[0][1]
    applicant_context = {
        "fico_score": user_data.get('fico'),
        "employment_months": user_data.get('employment_months'),
        "internal_risk_score": internal_score
    }
    with CreditScoreClient(api_key="...", tier="professional", license_key="...") as client:
        return client.evaluate(applicant_context, hybrid_config)
💡 Benefits of the Hybrid Approach
Configurable Weighting: Balance internal ML models, FICO, and alternative data.

Transparent Decisions: Every score is auditable and explainable.

No Retraining: Adjust model influence dynamically without retraining.

📊 Tier Comparison
Feature	             Community	Professional	Enterprise
Max Batch Size	         1	        100	           500
Max Payload	           512 KB	   1 MB	          2 MB
Model Metrics	        ❌	      ✅	            ✅
Adaptive Threshold	    ❌	      ✅	            ✅
Adaptive Weighting	    ❌	      ❌	            ✅
Support	             Community	   Email	  Priority (SLA)

🧬 Enterprise Features
Adaptive Feature Weighting
Backend algorithm automatically adjusts feature weights based on data magnitude.

Blends expert-defined weight with learned weight using an adjustment_factor (default 0.3).

Prevents model drift and improves resilience to changing market conditions.

🧱 Scoring Feature Examples
Traditional (Bureau Data)
credit_score, debt_to_income, previous_defaults, loan_to_value, months_since_last_delinquency

Alternative (Thin-File)
monthly_income, employment_months, education_level, rent_to_income_ratio, utility_payment_history

Hybrid (Model Outputs)
internal_risk_score, fraud_model_score

💼 Licensing
Professional and Enterprise tiers enable persistence and learning features such as:

Adaptive thresholds

Batch processing

Real-time metrics

Adaptive feature weighting (Enterprise only)

Licensing Contact
📧 contacto@dsfuptech.cloud
Professional License: PRO-YYYY-MM-DD-XXXX-XXXX
Enterprise License: ENT-YYYY-MM-DD-XXXX-XXXX

🧩 Example Use Cases
Thin-File Lending (No Credit History)
python
Copiar código
config = {
    "monthly_income": {"default": 3500, "weight": 2.0, "criticality": 2.0},
    "employment_months": {"default": 24, "weight": 1.5, "criticality": 1.5},
    "rent_to_income_ratio": {"default": 0.3, "weight": 2.0, "criticality": 2.5},
    "utility_payments_on_time": {"default": 1.0, "weight": 1.0, "criticality": 3.0}
}
Traditional Lending
python
Copiar código
config = {
    "credit_score": {"default": 700, "weight": 2.5, "criticality": 3.0},
    "debt_to_income": {"default": 0.35, "weight": 2.0, "criticality": 2.0},
    "loan_to_value": {"default": 0.8, "weight": 1.5, "criticality": 2.0}
}
🧾 API Reference
CreditScoreClient
python
Copiar código
CreditScoreClient(
    api_key: str,
    license_key: Optional[str] = None,
    tier: str = "community",
    base_url: Optional[str] = None,
    timeout: int = 30
)
Methods
Method	Description
evaluate(applicant, config)	Evaluate a single applicant.
evaluate_batch(applicants, config)	Evaluate multiple applicants (Pro/Enterprise).
close()	Close the HTTP session.

Supports with CreditScoreClient(...) as client: context usage.

Config Structure
python
Copiar código
config = {
    "feature_name": {
        "default": <ideal_value>,
        "weight": <float, 1.0–5.0>,
        "criticality": <float, 1.0–5.0>
    }
}
🧮 Migration from Static Rules
Before
python
Copiar código
def legacy_score(applicant):
    score = 500
    if applicant['credit_score'] > 700:
        score += 100
    elif applicant['credit_score'] > 650:
        score += 50
    if applicant['debt_to_income'] < 0.3:
        score += 75
    elif applicant['debt_to_income'] < 0.4:
        score += 25
    if applicant['employment_months'] > 24:
        score += 50
    return score > 650
After
python
Copiar código
config = {
    "credit_score": {"default": 720, "weight": 2.0, "criticality": 2.0},
    "debt_to_income": {"default": 0.3, "weight": 2.5, "criticality": 2.5},
    "employment_months": {"default": 36, "weight": 1.5, "criticality": 1.0}
}

result = client.evaluate(applicant, config)
print(f"Decision: {result['decision']}")



Support
Issues: contacto@dsfuptech.cloud

Professional/Enterprise Support: contacto@dsfuptech.cloud

License
Community Edition is free for evaluation and low-volume use. Professional and Enterprise tiers are subject to commercial licensing terms.

© 2025 DSF UpTech. Created by Jaime Alexander Jimenez. Powered by Adaptive Formula technology.