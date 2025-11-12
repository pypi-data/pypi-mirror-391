# dsf_quantum_sdk/__init__.py
"""
DSF Quantum SDK - Proprietary Adaptive Quantum Scoring

Copyright © 2025 Jaime Alexander Jimenez
All Rights Reserved.

This software is proprietary and confidential. Use requires a valid license key.
Unauthorized copying, distribution, or reverse engineering is prohibited.

License Tiers:
- Free: Basic simulator, limited features
- Professional: Advanced features + IBM Quantum access
- Enterprise: Full features + custom support


---

Two execution modes:

1. Synchronous (evaluate):
   - Fast simulator evaluations (~5-15s)
   - Blocks until result available
   - Best for development/testing
   - IBM hardware NOT supported

2. Asynchronous (submit_async):
   - IBM Quantum hardware (REQUIRED)
   - Complex simulator circuits
   - Non-blocking (returns job_id)
   - No timeout limits

Example usage:

    >>> from dsf_quantum_sdk import QuantumSDK, create_block, create_config
    >>> 
    >>> # Create configuration
    >>> config = create_config([
    ...     create_block('flujo_caja', [0.5, 0.3, 0.2], [1.4, 1.2, 1.0]),
    ...     create_block('comportamiento', [0.2, 0.3, 0.5], [1.8, 1.4, 1.0])
    ... ], global_adjustment=0.01)
    >>> 
    >>> # Sync evaluation (simulator only)
    >>> sdk = QuantumSDK(license_key='your-license-key')
    >>> result = sdk.evaluate(data, config, backend='simulator')
    >>> print(f"Score: {result.score:.4f}")
    >>> 
    >>> # Async evaluation (IBM hardware - Professional/Enterprise)
    >>> job_id = sdk.submit_async(
    ...     data, config, 
    ...     backend='ibm_quantum',
    ...     ibm_credentials={'token': '...', 'backend_name': 'ibm_brisbane'}
    ... )
    >>> result = sdk.wait_for_result(job_id, timeout=600)
    >>> print(f"Score: {result.score:.4f}")
"""

__version__ = '1.1.0'
__license__ = 'Proprietary'
__copyright__ = 'Copyright © 2025 Jaime Alexander Jimenez, operating as "Uptech"'

from .client import QuantumSDK, create_block, create_config
from .models import Block, QuantumConfig, QuantumResult, JobStatus
from .exceptions import (
    QuantumSDKError,
    ValidationError,
    APIError,
    RateLimitError
)

__all__ = [
    'QuantumSDK',
    'Block',
    'QuantumConfig',
    'QuantumResult',
    'JobStatus',
    'create_block',
    'create_config',
    'QuantumSDKError',
    'ValidationError',
    'APIError',
    'RateLimitError',
    '__version__'
]