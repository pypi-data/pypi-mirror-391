# Authorization Control SDK

Enterprise-grade authorization and access control system using adaptive scoring algorithms. Replace complex permission matrices and nested if/else chains with intelligent, configurable authorization rules.

## Why Authorization Control?

Traditional authorization systems, whether homegrown `if/else` matrices or complex policy engines, become brittle and difficult to manage as roles, resources, and business rules evolve. This SDK transforms your authorization logic into a **configurable scoring system** that makes nuanced decisions based on the full context of an access request.

---

## Core Concepts

Instead of rigid, binary rules, this SDK allows you to define authorization policies as a collection of weighted **factors**. The system evaluates how well a given request context matches an ideal state, producing a **permission score**. This moves your logic from brittle code to a flexible configuration.

---

## Installation

```bash
# Standard version
pip install dsf-access-sdk

# For optimized performance (requires C++ compiler)
pip install dsf-access-sdk[optimized]
```

---

## Quick Start

### Community Edition (Free)

```python
from auth_control import PermissionManager

pm = PermissionManager()

context = {
    'role_hierarchy_level': 2,      # employee
    'action_severity': 1,            # read
    'resource_sensitivity_level': 2, # internal
    'user_seniority_years': 3,
    'department_match': True,
    'compliance_training': True
}

allowed, score, message = pm.can_access(context)
print(f"Access: {message}")
```

### Professional Edition

```python
from auth_control import PermissionManager, PermissionContext

# Initialize with license
pm = PermissionManager(
    tier='professional',
    license_key='PRO-2026-12-31-XXXX-XXXX'
)

# Use the structured context model for clarity and auto-complete
context = PermissionContext(
    user_id='u-123',
    user_role='manager',
    action='delete',
    resource_id='doc-456',
    resource_sensitivity='internal'
)

# The SDK's helper method simplifies common checks
is_allowed = pm.check_role_permission(
    role='manager',
    action='delete',
    resource_sensitivity='internal'
)
print(f"Is manager allowed to delete internal resource? {'Yes' if is_allowed else 'No'}")

# Access performance metrics to monitor your authorization system
metrics = pm.get_metrics()
print(f"Adaptive decision threshold: {metrics.current_threshold:.3f}")
```

### Enterprise Edition

```python
from auth_control import PermissionManager, Field
from auth_control.policies import PolicyPresets

# Initialize with a strict policy preset and license
pm = PermissionManager(
    tier='enterprise', 
    license_key='ENT-2026-12-31-XXXX-XXXX',
    policy=PolicyPresets.strict_security()
)

# Adjust the learning algorithm's behavior
pm.set_adjustment_factor(0.4) # 60% expert policy, 40% algorithm-optimized

# ... process authorization requests ...

# View how the system has adapted the importance of different policies
metrics = pm.get_metrics()
print(f"Policy weight optimizations: {metrics.weight_changes}")
```

---

## Hybrid Model Integration

The SDK accepts **any predictive model** as an additional authorization factor, creating powerful ensemble systems that combine expert rules, ML models, behavioral analytics, and external security services.

### ML Model Integration

```python
import joblib
from transformers import pipeline

# Load security models
anomaly_detector = joblib.load('user_behavior_anomaly.pkl')
text_classifier = pipeline('text-classification', model='security/phishing-detector')

# Define hybrid authorization factors combining rules + ML models
security_factors = [
    # Traditional expert rules
    Field('role_hierarchy_level', 3, importance=4.0, sensitivity=3.0),
    Field('resource_sensitivity_level', 2, importance=4.0, sensitivity=4.0),
    
    # ML models as authorization factors
    Field('behavior_anomaly_score', 0.2, importance=4.5, sensitivity=4.0),
    Field('request_legitimacy_score', 0.8, importance=3.5, sensitivity=3.0)
]

# Process authorization with hybrid ensemble
def authorize_request(user, action, resource, request_context):
    # Get ML model predictions
    user_features = extract_behavior_features(user, request_context)
    anomaly_score = anomaly_detector.predict_proba([user_features])[0][1]
    
    request_text = f"{action} {resource['type']} {request_context.get('justification', '')}"
    legitimacy = text_classifier(request_text)[0]['score']
    
    # Combine with traditional authorization factors
    hybrid_context = {
        'role_hierarchy_level': get_role_level(user['role']),
        'resource_sensitivity_level': resource['sensitivity'],
        'behavior_anomaly_score': anomaly_score,
        'request_legitimacy_score': legitimacy
    }
    
    return pm.can_access(hybrid_context)
```

### External Security Services Integration

```python
import requests
from datetime import datetime

# External APIs and statistical models as authorization factors
enterprise_factors = [
    # Core authorization rules
    Field('user_clearance_level', 3, importance=5.0, sensitivity=4.0),
    Field('time_restriction_compliance', True, importance=3.0, severity=4.0),
    
    # External security services
    Field('identity_verification_score', 0.9, importance=4.0, sensitivity=3.5),
    Field('device_trust_score', 0.8, importance=3.5, sensitivity=3.0),
    
    # Statistical risk model
    Field('access_pattern_zscore', 0.5, importance=3.0, sensitivity=2.5)
]

def advanced_authorization_check(user, device, action, resource):
    # Call external identity verification service
    id_response = requests.post('https://identity-api.com/verify', 
                               json={'user_id': user['id'], 'session_token': user['token']})
    identity_score = id_response.json().get('confidence', 0.0)
    
    # Device trust scoring from MDM service
    device_response = requests.get(f'https://mdm-api.com/device/{device["id"]}/trust')
    device_trust = device_response.json().get('trust_score', 0.0)
    
    # Statistical analysis of access patterns
    recent_accesses = get_user_access_history(user['id'], days=30)
    access_zscore = calculate_access_pattern_anomaly(recent_accesses, action, resource)
    
    # Combine all authorization signals
    hybrid_context = {
        'user_clearance_level': user['clearance_level'],
        'time_restriction_compliance': is_within_allowed_hours(),
        'identity_verification_score': identity_score,
        'device_trust_score': device_trust,
        'access_pattern_zscore': max(0, min(1, (access_zscore + 3) / 6))  # Normalize
    }
    
    return pm.can_access(hybrid_context)
```

### Benefits of Hybrid Authorization

- **Defense in depth**: Multiple independent signals reduce false positives/negatives
- **Configurable weighting**: Control how much each security layer contributes
- **Transparent decisions**: Each factor's contribution is auditable
- **Adaptive security**: ML models learn from access patterns automatically
- **Graceful degradation**: If external services fail, core rules still function

---

## Tier Comparison

| Feature                          |  Community |      Professional       |       Enterprise        |
|----------------------------------|------------|-------------------------|-------------------------|
| **Decisions/month**              | Unlimited* |      Unlimited          |       Unlimited         |
| **Standard Policies**            |    ✅      |          ✅            |          ✅             |
| **Policy Presets**               |    ❌      |          ✅            |          ✅             |
| **Adaptive Threshold**           |    ❌      |          ✅            |          ✅             |
| **Performance metrics**          |    ❌      |          ✅            |          ✅    Enhanced |
| **Policy Weight Optimization**   |    ❌      |          ❌            |          ✅             |
| **Support**                      |  Community |         Email           |     Priority SLA         |
| **License validity**             |    N/A     |        Annual           |        Annual            |

*Community tier is free for evaluation. Production use requires registration.

---

## Enterprise Features

### Weight Calibration (Enterprise Exclusive)
Enterprise tier automatically calibrates field weights based on data patterns:

```python
# Control the balance between expert and algorithm weights
sdk.set_adjustment_factor(0.3)  # Default: 70% expert, 30% algorithm

# Factor range:
# 0.0 = 100% expert weights (trust configuration)
# 0.5 = 50/50 mix
# 1.0 = 100% algorithm weights (full automation)
```

The algorithm tracks field magnitudes and uses sqrt dampening to prevent extreme values from dominating, then mixes expert and proposed weights according to your adjustment factor.

---

## Core Features

### Role-Based Access Control (RBAC) with Nuances

Instead of a rigid matrix, define roles by a hierarchy level and let the score handle the edge cases. The check_role_permission() helper makes this easy.

```python
# Check hierarchical permissions
allowed = pm.check_role_permission('employee', 'read', 'internal')
```

### Attribute-Based Access Control (ABAC)
Combine user attributes, resource properties, and environmental context into a single, holistic decision.

```python
from auth_control import Field

# Add a custom attribute to the standard policy
custom_policy = get_standard_policies()
custom_policy.append(
    Field('mfa_verified', reference=True, importance=5.0, sensitivity=5.0)
)
pm.configure(custom_policy)

# Now, the MFA status will be a critical factor in all decisions
context['mfa_verified'] = user.has_mfa_enabled()
result = pm.can_access(context)
```

```python
context = {
    'department_match': True,
    'time_restriction_compliance': True,
    'project_phase_risk': 2,
    'resource_ownership_match': False
}
allowed, score, msg = pm.can_access(context)
```

### Policy Presets

```python
from auth_control.policies import PolicyPresets

# Strict security mode
pm.set_policies(PolicyPresets.strict_security())

# Relaxed mode for development
pm.set_policies(PolicyPresets.relaxed())
```

### Dynamic Policy Adjustments
Respond to real-time events without deploying new code.

```python
# Scenario: Security incident detected. Immediately restrict all non-essential access.
print("Activating emergency lockdown mode...")
pm.set_confidence_level(0.85) # Increases decision threshold

# Scenario: After-hours maintenance window.
print("Relaxing policies for maintenance...")
pm.set_confidence_level(0.55) # Lowers decision threshold
```

---

### Authorization Factors

**Critical Factors (High Impact)**

- role_hierarchy_level - User's role level (1-4)
- action_severity - Action risk level (1-4)
- resource_sensitivity_level - Data classification (1-4)

**Contextual Factors (Medium Impact)**

- user_seniority_years - Experience in organization
- department_match - Department-resource alignment
- time_restriction_compliance - Time-based rules
- compliance_training - Required certifications

**Secondary Factors (Low Impact)**

- team_size_factor - Team management scope
- project_phase_risk - Development/Production
- weekend_restriction - Time-based policies

---

## Professional & Enterprise Licensing

Professional and Enterprise tiers include:
- Adaptive confidence learning from evaluation patterns
- Real-time performance metrics and insights
- Support for complex data structures
- Production-ready optimization algorithms
- Enterprise: Automatic weight calibration

**To purchase a license:**
- Professional: $299/month or $2,999/year
- Enterprise: Contact for custom pricing
- Email: jaimeajl@hotmail.com

**License format:**
- Professional: `PRO-YYYY-MM-DD-XXXX-XXXX`
- Enterprise: `ENT-YYYY-MM-DD-XXXX-XXXX`

---

## Use Cases

### GitHub-Style Repository Access

```python
context = {
    'role_hierarchy_level': 3,  # maintainer
    'action_severity': 2,        # write
    'resource_sensitivity_level': 2,  # private repo
    'department_match': True,
    'branch_protection': True
}
```

### Healthcare Records (HIPAA)

```python
context = {
    'role_hierarchy_level': 3,  # doctor
    'resource_sensitivity_level': 4,  # patient data
    'compliance_training': True,  # HIPAA certified
    'emergency_override': False
}
```

### Financial Systems

```python
context = {
    'role_hierarchy_level': 2,  # analyst
    'action_severity': 1,        # read only
    'resource_sensitivity_level': 3,  # financial data
    'audit_trail_enabled': True,
    'mfa_verified': True
}
```

---

## API Reference

### PermissionManager

**Initialization:**

```python
PermissionManager(
    tier='community',
    license_key=None,
    custom_policies=None
)
```

**Methods:**

- can_access(context) - Evaluate authorization request
- check_role_permission(role, action, resource) - Simple role check
- set_policies(policies) - Update authorization policies
- set_confidence_level(level) - Change security level
- get_metrics() - Performance stats (Pro/Ent)
- set_adjustment_factor(factor) - Weight calibration (Ent)

### Field Configuration

```python
Field(
    name='factor_name',
    reference=expected_value,
    importance=1.0,  # 1.0-5.0
    sensitivity=1.5   # 1.0-5.0
)
```

---

## Migration from Traditional Systems

### Before:

```python
if user_role == 'admin':
    if resource_type == 'critical':
        if user_seniority < 2:
            return False
    return True
elif user_role == 'manager':
    if action == 'delete':
        return False
    # ... 50+ more conditions
```

### After:

```python
pm = PermissionManager()
allowed, score, message = pm.can_access(context)
```

---

## Support

- **Documentation:** https://docs.authcontrol.ai
- **Community:** https://github.com/authcontrol/sdk/discussions
- **Issues:** https://github.com/authcontrol/sdk/issues
- **Professional/Enterprise Support:** jaimeajl@hotmail.com

---

## License

MIT License for Community Edition. Professional and Enterprise editions are subject to commercial licensing terms.

© 2025 Authorization Control SDK. Powered by Adaptive Formula technology.