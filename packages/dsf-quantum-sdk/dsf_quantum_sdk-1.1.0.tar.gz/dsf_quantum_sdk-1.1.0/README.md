# DSF Quantum SDK

**First Commercial Quantum Decision Intelligence Platform**

Transform enterprise data into actionable quantum scores without quantum physics expertise. Validated on IBM Quantum hardware (127 qubits) and applicable across industries.

---

## 🚀 Why DSF Quantum?

Critical business decisions (credit scoring, risk assessment, ESG rating, healthcare) traditionally use linear models that ignore complex correlations and hierarchical dependencies.

**DSF Quantum is the first quantum orchestration layer that converts enterprise data into quantified decisions without requiring quantum physics knowledge.**

### How It Works

```
┌──────────────┐       ┌───────────────────┐      ┌──────────────┐
│ JSON Input   │ ───▶ │ Quantum Backend   │ ───▶ │ Score 0-1    │
│ (Features)   │       │ (IBM/Simulator)   │      │ + Breakdown  │
└──────────────┘       └───────────────────┘      └──────────────┘
```

**Key Advantages:**

- ✅ **Hierarchical evaluation** via quantum superposition
- ✅ **Real IBM Quantum hardware** (127 qubits) or free simulator
- ✅ **No quantum code** - simple REST API and Python SDK
- ✅ **Async orchestration** - parallel batch processing
- ✅ **Cross-industry** - fintech, healthcare, supply chain, energy, ESG

**Important note:** IBM Quantum is not mandatory - the API operates completely with simulator at no additional cost or external dependencies.

---

## 📦 Installation

```bash
pip install dsf-quantum-sdk
```

**Requirements:**
- Python >= 3.8
- Compatible with Linux, macOS, and Windows
- Internet connection (cloud-based API)
- No quantum hardware dependencies

**Full installation with optional dependencies:**

```bash
pip install dsf-quantum-sdk[ibm]  # Includes qiskit-ibm-runtime
```

**Note:** DSF Quantum is a cloud-based service. The SDK connects to the production API - no local backend installation required.

---

## 🎯 Quick Start

### Simulator (Fast Development)

```python
from dsf_quantum_sdk import QuantumSDK, create_config, create_block

# Configure hierarchical blocks
config = create_config(
    blocks=[
        create_block(
            name='financial_health',
            influence=[0.5, 0.3, 0.2],  # Relative feature weights
            priority=[1.5, 1.2, 1.0],   # Criticality levels
            block_influence=1.2,         # Block weight
            block_priority=2.0           # Block criticality
        ),
        create_block(
            name='operational_risk',
            influence=[0.6, 0.4],
            priority=[1.3, 1.0],
            block_influence=0.8,
            block_priority=1.5
        )
    ],
    global_adjustment=0.01
)

# Normalized data [0-1]
data = {
    'financial_health': [0.75, 0.82, 0.68],
    'operational_risk': [0.55, 0.91]
}

# Synchronous evaluation (no license_key required)
with QuantumSDK() as sdk:
    result = sdk.evaluate(
        data=data,
        config=config.to_dict(),
        backend='simulator',
        shots=1024
    )
    
print(f"Score: {result['score']:.4f}")
print(f"Blocks: {result['blocks']}")
```

### IBM Quantum (Production)

```python
import os
from dsf_quantum_sdk import QuantumSDK

# Requires Professional or Enterprise license_key
with QuantumSDK(license_key='PRO-2026-12-31-XXXX') as sdk:
    job_id = sdk.submit_async(
        data=data,
        config=config.to_dict(),
        backend='ibm_quantum',
        shots=1024,
        ibm_credentials={
            'token': os.getenv('IBM_QUANTUM_TOKEN'),
            'backend_name': 'least_busy'  # Recommended: automatic selection
        }
    )
    
    # Automatic polling with timeout
    result = sdk.wait_for_result(
        job_id, 
        timeout=3600,      # 1 hour
        poll_interval=30   # Check every 30s
    )
    
print(f"Score: {result['score']:.4f}")
print(f"Backend used: {result['backend']}")
```

---

## 🧠 Multi-Domain Examples

### 1. Credit Risk Assessment (Fintech)

Evaluate credit risk combining payment behavior and cash flow.

```python
from dsf_quantum_sdk import QuantumSDK, create_config, create_block

config = create_config(
    blocks=[
        create_block(
            name='payment_behavior',
            influence=[0.2, 0.3, 0.5],    # credit_score, history, defaults
            priority=[1.8, 1.4, 1.0],
            risk_adjustment=0.05,
            block_influence=1.5,
            block_priority=2.5
        ),
        create_block(
            name='cash_flow',
            influence=[0.5, 0.3, 0.2],    # income, debt_ratio, stability
            priority=[1.4, 1.2, 1.0],
            risk_adjustment=0.10,
            block_influence=0.8,
            block_priority=1.2
        )
    ]
)

data = {
    'payment_behavior': [0.85, 0.72, 0.91],
    'cash_flow': [0.65, 0.45, 0.78]
}

with QuantumSDK() as sdk:
    result = sdk.evaluate(data, config.to_dict(), backend='simulator')
    print(f"Credit Score: {result['score']:.4f}")
```

### 2. Healthcare Patient Risk

Clinical risk prediction combining medical indicators and lifestyle factors.

```python
config = create_config(
    blocks=[
        create_block(
            name='clinical_indicators',
            influence=[0.4, 0.3, 0.3],    # vitals, labs, medical_history
            priority=[2.0, 1.5, 1.2],
            block_influence=1.8,
            block_priority=3.0
        ),
        create_block(
            name='lifestyle_factors',
            influence=[0.5, 0.5],         # physical_activity, nutrition
            priority=[1.3, 1.0],
            block_influence=0.6,
            block_priority=1.0
        )
    ]
)

data = {
    'clinical_indicators': [0.42, 0.68, 0.55],
    'lifestyle_factors': [0.71, 0.83]
}

with QuantumSDK() as sdk:
    result = sdk.evaluate(data, config.to_dict())
    print(f"Patient Risk: {result['score']:.4f}")
```

### 3. Supply Chain Vendor Scoring

Vendor evaluation based on operational performance and regulatory compliance.

```python
config = create_config(
    blocks=[
        create_block(
            name='performance',
            influence=[0.4, 0.3, 0.3],    # delivery_time, quality, cost
            priority=[1.5, 1.3, 1.0],
            block_influence=1.2,
            block_priority=2.0
        ),
        create_block(
            name='compliance',
            influence=[0.6, 0.4],         # certifications, audit_results
            priority=[2.0, 1.5],
            block_influence=1.5,
            block_priority=2.5
        )
    ]
)

data = {
    'performance': [0.88, 0.92, 0.76],
    'compliance': [0.95, 0.89]
}
```

### 4. ESG Corporate Rating

Multi-dimensional rating for Environmental, Social, and Governance factors.

```python
config = create_config(
    blocks=[
        create_block(
            name='environmental',
            influence=[0.4, 0.3, 0.3],    # emissions, waste, energy_use
            priority=[1.5, 1.2, 1.0],
            block_influence=1.0,
            block_priority=1.5
        ),
        create_block(
            name='social',
            influence=[0.5, 0.5],         # labor_practices, community_impact
            priority=[1.3, 1.0],
            block_influence=1.0,
            block_priority=1.3
        ),
        create_block(
            name='governance',
            influence=[0.6, 0.4],         # board_structure, ethics
            priority=[1.8, 1.2],
            block_influence=1.2,
            block_priority=2.0
        )
    ]
)

data = {
    'environmental': [0.72, 0.65, 0.81],
    'social': [0.88, 0.79],
    'governance': [0.91, 0.85]
}
```

### 5. Manufacturing Predictive Maintenance

Failure prediction for industrial machinery combining sensors and historical data.

```python
config = create_config(
    blocks=[
        create_block(
            name='sensor_data',
            influence=[0.3, 0.3, 0.2, 0.2],  # temp, vibration, pressure, speed
            priority=[1.5, 1.4, 1.2, 1.0],
            block_influence=1.4,
            block_priority=2.2
        ),
        create_block(
            name='maintenance_history',
            influence=[0.5, 0.5],             # failure_rate, time_since_service
            priority=[1.6, 1.3],
            block_influence=1.0,
            block_priority=1.8
        )
    ]
)

data = {
    'sensor_data': [0.78, 0.65, 0.82, 0.71],
    'maintenance_history': [0.45, 0.88]
}
```

---

## 🔧 IBM Quantum Setup

### 1. Get IBM Quantum Token

1. Create free account at [IBM Quantum](https://quantum.ibm.com/)
2. Navigate to **Account → API Tokens**
3. Copy token and store securely:

```bash
export IBM_QUANTUM_TOKEN='your_ibm_quantum_token_here'
```

### 2. Select Backend

**Available IBM backends:**
- `least_busy` - **Recommended**: automatic selection of least saturated backend
- `ibm_torino` - 127 qubits, typically ~2-5s/job
- `ibm_kyoto` - 127 qubits
- `ibm_osaka` - 127 qubits

**Note:** Available backends may change. Check [IBM Quantum Services](https://quantum.ibm.com/services) for updated list.

```python
ibm_credentials = {
    'token': os.getenv('IBM_QUANTUM_TOKEN'),
    'backend_name': 'least_busy'  # Recommended option
}
```

### 3. Estimate Costs and Times

**IBM Quantum Open Plan (Free):**
- 10 minutes/month compute time
- Access to all public backends
- Shared queue (variable latency)

**IBM Quantum Premium:**
- Unlimited compute time
- Priority hardware access
- Guaranteed SLA
- Dedicated queue

**Estimated time per job:**
- Example: 4 blocks + 1 global = 5 quantum circuits
- ~2-5s per circuit on `ibm_torino`
- **Total: ~10-25s execution + queue time**
- Queue time: 5-30 minutes (variable based on demand)

---

## ⚡ Best Practices

### 1. Data Normalization

**All features must be normalized to [0, 1] range before sending to SDK.**

```python
from sklearn.preprocessing import MinMaxScaler
import numpy as np

# Normalize raw features
raw_data = {
    'financial_health': [75000, 82000, 68000],      # Income in USD
    'operational_risk': [55, 91]                     # Scores 0-100
}

data_normalized = {}
scaler = MinMaxScaler()

for block_name, values in raw_data.items():
    arr = np.array(values).reshape(-1, 1)
    data_normalized[block_name] = scaler.fit_transform(arr).flatten().tolist()

print(data_normalized)
# {'financial_health': [0.5, 1.0, 0.0], 'operational_risk': [0.0, 1.0]}
```

**Note:** All returned scores are normalized [0-1], enabling direct integration with AI pipelines, BI dashboards, and classical decision systems.

### 2. Batch Processing

For multiple evaluations, use async jobs in parallel:

```python
from dsf_quantum_sdk import QuantumSDK

job_ids = []

with QuantumSDK(license_key='PRO-2026-12-31-XXXX') as sdk:
    for sample in dataset:
        job_id = sdk.submit_async(
            data=extract_features(sample),
            config=config.to_dict(),
            backend='ibm_quantum',
            ibm_credentials=credentials
        )
        job_ids.append(job_id)
    
    # Process results
    results = []
    for job_id in job_ids:
        try:
            result = sdk.wait_for_result(job_id, timeout=3600)
            results.append({
                'score': result['score'],
                'blocks': result['blocks']
            })
        except TimeoutError:
            print(f"Job {job_id} timeout - can be retried")
```

### 3. Error Handling

```python
from dsf_quantum_sdk import QuantumSDK
from dsf_quantum_sdk.exceptions import APIError, RateLimitError
import time

with QuantumSDK() as sdk:
    try:
        result = sdk.evaluate(data, config, backend='simulator')
    except RateLimitError as e:
        print(f"Rate limit reached. Retry after {e.retry_after}s")
        time.sleep(e.retry_after)
        result = sdk.evaluate(data, config, backend='simulator')
    except APIError as e:
        print(f"API error: {e.status_code} - {e.message}")
        # Implement fallback or logging
```

### 4. Threshold Tuning

Optimize decision thresholds for your domain:

```python
# Evaluate complete dataset
scores = [result['score'] for result in results]
actuals = [sample['actual_label'] for sample in dataset]

# Test different thresholds
for threshold in [0.3, 0.4, 0.5, 0.6, 0.7]:
    predictions = [1 if s >= threshold else 0 for s in scores]
    
    # Calculate metrics
    accuracy = sum(p == a for p, a in zip(predictions, actuals)) / len(actuals)
    precision = sum(p == 1 and a == 1 for p, a in zip(predictions, actuals)) / sum(predictions)
    
    print(f"Threshold {threshold}: Accuracy={accuracy:.2%}, Precision={precision:.2%}")
```

### 5. Integration with AI Pipelines

```python
# Compatible with popular frameworks
from dsf_quantum_sdk import QuantumSDK
import pandas as pd

def quantum_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Add quantum score as additional feature"""
    sdk = QuantumSDK()
    
    scores = []
    for _, row in df.iterrows():
        data = extract_features(row)
        result = sdk.evaluate(data, config.to_dict())
        scores.append(result['score'])
    
    df['quantum_score'] = scores
    return df

# Use in ML pipeline
X_train = quantum_feature_engineering(X_train)
model.fit(X_train, y_train)
```

---

## 📊 Performance

**Latency:**
- **Simulator:** 1-5 seconds per evaluation
- **IBM Quantum:** 5-30 minutes (includes queue time)

**Throughput:**
- **Simulator:** ~100 evaluations/minute
- **IBM Quantum:** ~50-100 evaluations/hour (parallel processing)

**Scalability:**
- Batch processing: up to 1000 simultaneous jobs
- Automatic recovery from transient failures
- Built-in retry logic

**Benchmarks:**
- Performed on `ibm_torino` (127 qubits)
- Optimized Qiskit Runtime
- Typical fidelity: 95-98% on real hardware

---

## 🔒 Security & Compliance

### Data in Transit
- **HTTPS/TLS 1.3** enforced on all communications
- API key authentication with JWT tokens
- Encrypted payloads for sensitive data

### Data at Rest
- **Limited TTL:** 10 minutes (simulator), 24 hours (IBM jobs)
- No persistence of sensitive data or PII
- Anonymous logs for debugging

### Compliance
- **GDPR alignment:** EU data residency available
- **SOC 2 Type II:** In progress (Q2 2026)
- **HIPAA-ready:** Configurations available for healthcare

### Infrastructure
- Deployed on Google Cloud Run (auto-scaling)
- Tenant isolation in Enterprise tier
- 24/7 monitoring with automatic alerts

---

## 🆚 Backend Comparison

|      Feature      | Simulator        | IBM Quantum        |
|-------------------|------------------|--------------------|
| **Latency**       | 1-5s             | 5-30min            |
| **Cost**          | Free             | IBM plan required  |
| **Fidelity**      | Ideal (100%)     | ~95-98%            |
| **Qubits**        | Unlimited        | 127 (hardware)     |
| **Typical use**   | Dev/Test/Pilot   | Production         |
| **Rate limits**   | 100 req/hour     | Per IBM plan       |
| **Availability**  | 99.9%            | Variable (queue)   |

**Recommendation:** Use simulator for development, validation, and demos. Migrate to IBM Quantum for production when you need fidelity in critical environments.

---

## 📖 API Reference

### SDK Initialization

```python
from dsf_quantum_sdk import QuantumSDK

sdk = QuantumSDK(
    license_key: Optional[str] = None,      # Community: None, Pro/Enterprise: required
    timeout: int = 120,                     # Request timeout (seconds)
    max_retries: int = 3                    # Automatic retries
)
```

### Methods

#### evaluate()

**Synchronous** evaluation (only available with `backend='simulator'`).

```python
from dsf_quantum_sdk import QuantumSDK

result = sdk.evaluate(
    data: Dict[str, List[float]],           # Normalized features [0-1]
    config: Dict,                           # Output from create_config().to_dict()
    backend: str = 'simulator',             # 'simulator' only
    shots: int = 1024                       # Number of quantum measurements
) -> Dict

# Returns:
{
    'score': 0.7845,          # Final score [0-1]
    'backend': 'simulator',
    'shots': 1024,
    'blocks': {               # Scores per block
        'block1': 0.82,
        'block2': 0.75
    },
    'processed_at': '1761747000.123'
}
```

#### submit_async()

Submit **asynchronous** job (simulator or IBM Quantum).

```python
from dsf_quantum_sdk import QuantumSDK

job_id = sdk.submit_async(
    data: Dict[str, List[float]],
    config: Dict,
    backend: str = 'ibm_quantum',           # 'simulator' or 'ibm_quantum'
    shots: int = 1024,
    ibm_credentials: Dict = None            # Required if backend='ibm_quantum'
) -> str

# ibm_credentials format:
{
    'token': 'your_ibm_token',
    'backend_name': 'least_busy'            # or specific backend
}
```

#### wait_for_result()

Automatic polling with configurable timeout.

```python
from dsf_quantum_sdk import QuantumSDK

result = sdk.wait_for_result(
    job_id: str,
    timeout: int = 3600,                    # 1 hour
    poll_interval: int = 30                 # Check every 30s
) -> Dict

# Returns same format as evaluate()
```

#### get_status()

Query job status without waiting.

```python
from dsf_quantum_sdk import QuantumSDK

status = sdk.get_status(job_id: str) -> Dict

# Returns:
{
    'status': 'pending' | 'running' | 'completed' | 'failed',
    'created_at': '1761747000.123',
    'progress': 0.65  # Only if status='running'
}
```

### Helper Functions

#### create_config()

```python
from dsf_quantum_sdk import create_config, create_block

config = create_config(
    blocks: List[Block],                    # List of blocks
    global_adjustment: float = 0.0          # Optional global adjustment
)
```

#### create_block()

```python
from dsf_quantum_sdk import create_block

block = create_block(
    name: str,                              # Unique identifier
    influence: List[float],                 # Feature weights [0-1]
    priority: List[float],                  # Criticalities [1.0-2.0]
    block_influence: float = 1.0,           # Block weight
    block_priority: float = 1.0,            # Block criticality
    risk_adjustment: float = 0.0            # Optional penalty
)
```

---

## ⚠️ Common Issues & Troubleshooting

### 429 Rate Limit Exceeded

**Cause:** Exceeded request limit for your tier.

**Solution:**
- Community: 100 requests/hour - wait or upgrade
- Professional/Enterprise: Contact support if unexpected limits

```python
except RateLimitError as e:
    time.sleep(e.retry_after)  # Automatic retry
```

### 403 License Invalid

**Cause:** Invalid or expired license key.

**Solution:**
- Verify format: `PRO-YYYY-MM-DD-XXXX` or `ENT-YYYY-MM-DD-XXXX`
- Check expiration date
- Contact sales for renewal

### IBM Token Missing/Invalid

**Cause:** Token not configured or expired.

**Solution:**
1. Generate new token at [IBM Quantum](https://quantum.ibm.com/)
2. Verify environment variable: `echo $IBM_QUANTUM_TOKEN`
3. Confirm permissions on IBM Quantum Platform

```python
ibm_credentials = {
    'token': os.getenv('IBM_QUANTUM_TOKEN'),
    'backend_name': 'least_busy'
}
```

### Timeout on IBM Jobs

**Cause:** Saturated queues on IBM hardware.

**Solution:**
- Use `backend_name='least_busy'` for automatic selection
- Increase `timeout` in `wait_for_result()`
- Consider IBM Quantum Premium for dedicated queue
- Fallback to simulator if urgent

### IBM Connectivity Issues

**Troubleshooting:**
1. Verify internet connectivity
2. Check that IBM token is not expired
3. Try alternative backend (`least_busy`)
4. If persists: contact DSF Quantum technical support

---

## 🛠️ Deployment Guide

### Development Environment

```python
# .env
IBM_QUANTUM_TOKEN=your_token_here
DSF_LICENSE_KEY=PRO-2026-12-31-XXXX  # If applicable

# app.py
import os
from dsf_quantum_sdk import QuantumSDK

# SDK automatically connects to production API
sdk = QuantumSDK(
    license_key=os.getenv('DSF_LICENSE_KEY'),  # Optional for Community
    timeout=60
)

# Use simulator for fast testing
result = sdk.evaluate(data, config, backend='simulator')
```

### Production Deployment

```python
import os
from dsf_quantum_sdk import QuantumSDK
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use environment variables for secrets
sdk = QuantumSDK(
    license_key=os.getenv('DSF_LICENSE_KEY'),
    timeout=120,
    max_retries=3
)

# Implement robust retry logic
def evaluate_with_retry(data, config, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            result = sdk.evaluate(data, config, backend='simulator')
            return result
        except Exception as e:
            logger.error(f"Attempt {attempt+1} failed: {e}")
            if attempt == max_attempts - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

### Monitoring & Observability

```python
import time
import logging

logger = logging.getLogger(__name__)

def evaluate_with_monitoring(data, config):
    start = time.time()
    
    try:
        result = sdk.evaluate(data, config)
        elapsed = time.time() - start
        
        logger.info(f"✅ Score: {result['score']:.4f}, Time: {elapsed:.1f}s")
        
        # Send metrics to monitoring system
        metrics.gauge('quantum.score', result['score'])
        metrics.timing('quantum.latency', elapsed)
        
        return result
        
    except Exception as e:
        elapsed = time.time() - start
        logger.error(f"❌ Error: {e}, Time: {elapsed:.1f}s")
        metrics.increment('quantum.errors')
        raise
```

### Integration Recommendations

**Compatible with:**
- **Serverless:** Cloud Run, AWS Lambda, Azure Functions
- **Frameworks:** FastAPI, Flask, Django, LangChain
- **ML Platforms:** Vertex AI, SageMaker, Azure ML
- **Data Pipelines:** Apache Airflow, Prefect, Dagster

**Integration architecture:**

```
┌──────────────┐       ┌─────────────────┐      ┌──────────────┐
│ Your App     │ ───▶ │ DSF Quantum SDK │ ───▶ │ DSF Quantum  │
│ (API/ML)     │       │ (Python Client) │      │ API (Cloud)  │
└──────────────┘       └─────────────────┘      └──────────────┘
                                                        │
                                                        ▼
                                                ┌──────────────┐
                                                │ IBM Quantum  │
                                                │ (Optional)   │
                                                └──────────────┘
```

**Note:** DSF Quantum's internal architecture is proprietary and runs entirely on cloud infrastructure.

---

## 📚 Resources

- **Documentation:** [docs.dsfuptech.cloud](https://docs.dsfuptech.cloud)
- **IBM Quantum Docs:** [docs.quantum.ibm.com](https://docs.quantum.ibm.com)
- **API Reference:** [api.dsfuptech.cloud/docs](https://api.dsfuptech.cloud/docs)
- **Support:** [contacto@dsfuptech.cloud](mailto:contacto@dsfuptech.cloud)
- **Sales Inquiries:** [contacto@dsfuptech.cloud](mailto:contacto@dsfuptech.cloud)

---

## 📄 License

**DSF Quantum SDK** is proprietary cloud-based software:

- **API Service:** Not self-hosted - connects to DSF Quantum infrastructure
- **Closed architecture:** Formula and quantum algorithms are confidential
- **Community Tier:** Free for development with simulator
- **Professional/Enterprise:** Commercial license for production and IBM hardware

Contact [contacto@dsfuptech.cloud](mailto:contacto@dsfuptech.cloud) for enterprise licensing information.

**Note:** Platform source code and quantum architecture are not publicly available.

---

<div align="center">

**DSF Quantum SDK v1.0.15**

[Website](https://dsfuptech.cloud) • [Documentation](https://docs.dsfuptech.cloud) • [API Reference](https://api.dsfuptech.cloud/docs)



</div>

