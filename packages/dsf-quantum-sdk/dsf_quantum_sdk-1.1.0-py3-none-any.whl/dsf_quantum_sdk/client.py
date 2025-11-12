# dsf_quantum_sdk/client.py
"""DSF Quantum SDK - Lightweight client with async support"""

import requests
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin
import time
from functools import wraps
import logging
import json
from types import SimpleNamespace

from . import __version__
from .exceptions import ValidationError, APIError, RateLimitError
from .models import QuantumConfig, QuantumResult, JobStatus, Block

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator with rate limit awareness"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except RateLimitError as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Rate limited. Retrying after {e.retry_after}s...")
                        time.sleep(e.retry_after)
                    last_exception = e
                except (requests.RequestException, APIError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
            raise last_exception
        return wrapper
    return decorator


class QuantumSDK:
    
    BASE_URL = "https://dsf-quantum-qefh4sjio-api-dsfuptech.vercel.app/api"
    
    def __init__(
        self,
        license_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 120,
        max_retries: int = 3,
        verify_ssl: bool = True
    ):
       
        self.license_key = license_key
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self.max_retries = max_retries
        self.verify_ssl = verify_ssl
        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': f'DSF-Quantum-SDK/{__version__}'
        })
    
    def _validate_config(self, config: Dict) -> None:
        """Validate hierarchical config structure"""
        if not isinstance(config, dict):
            raise ValidationError("Config must be a dictionary")
        
        if 'blocks' not in config:
            raise ValidationError("Config must contain 'blocks' key")
        
        blocks = config['blocks']
        if not isinstance(blocks, list) or len(blocks) == 0:
            raise ValidationError("'blocks' must be a non-empty list")
        
        for idx, block in enumerate(blocks):
            required = ['name', 'influence', 'priority']
            for field in required:
                if field not in block:
                    raise ValidationError(f"Block {idx} missing required field: {field}")
    
    def _validate_data(self, data: Dict, config: Dict) -> None:
        """Validate data matches config blocks"""
        if not isinstance(data, dict):
            raise ValidationError("Data must be a dictionary")
        
        block_names = {b['name'] for b in config['blocks']}
        data_keys = set(data.keys())
        
        missing = block_names - data_keys
        if missing:
            raise ValidationError(f"Missing data for blocks: {missing}")
        
        for name, values in data.items():
            if not isinstance(values, list):
                raise ValidationError(f"Data for '{name}' must be a list")
            if len(values) == 0:
                raise ValidationError(f"Data for '{name}' cannot be empty")
    
    @retry_on_failure(max_retries=3, delay=1.5)
    def _make_request(self, endpoint: str, payload: Dict) -> Dict:
       
        base = self.base_url.rstrip("/")
        ep = endpoint.strip().lstrip("/")
        
        url = ""
        
        if ep in ("", "enqueue"):
            url = base
            
        elif ep.startswith("status/"):
           
            url = f"{base}/evaluate/{ep}"
        
        else:
            url = urljoin(f"{base}/", ep)

        try:
            if ep.startswith("status/"):
                resp = self.session.get(url, timeout=self.timeout, verify=self.verify_ssl)
            else:
                resp = self.session.post(url, json=payload, timeout=self.timeout, verify=self.verify_ssl)
                
        except requests.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")
        
        if resp.status_code == 429:
            try:
                err = resp.json()
            except ValueError:
                err = {}
            retry_after = err.get("retry_after") or resp.headers.get("Retry-After", "60")
            try:
                retry_after_int = int(retry_after)
            except (ValueError, TypeError):
                retry_after_int = 60
            raise RateLimitError(
                err.get("error", "Rate limited"),
                retry_after=retry_after_int,
                limit=err.get("limit")
            )
        
        try:
            j = resp.json()
        except ValueError:
            j = {}
        
        if resp.status_code >= 400:
            msg = j.get("error", f"API returned HTTP {resp.status_code}")
            raise APIError(msg, status_code=resp.status_code)
        
        return j
    
    def evaluate(
        self,
        data: Dict[str, List[float]],
        config: Union[Dict[str, Any], QuantumConfig],
        backend: str = 'simulator',
        shots: int = 1024,
        num_eval_qubits: int = 6,
    ) -> QuantumResult:
        
        # Convert QuantumConfig to dict if needed
        if isinstance(config, QuantumConfig):
            config = config.to_dict()
        
        # Validate inputs
        self._validate_config(config)
        self._validate_data(data, config)
        
        if backend not in ['simulator', 'ibm_quantum']:
            raise ValidationError("backend must be 'simulator' or 'ibm_quantum'")
        
        if backend == 'ibm_quantum':
            raise ValueError(
                "Synchronous evaluation does not support IBM Quantum hardware. "
                "Use submit_async() or evaluate_async() instead."
            )
        
        payload = {
            'data': data,
            'config': config,
            'backend': backend,
            'shots': shots,
            'num_eval_qubits': num_eval_qubits
        }
        
        if self.license_key:
            payload['license_key'] = self.license_key
        
        response = self._make_request('', payload)
        
        if 'job_id' in response and response.get('status') in ('processing', 'queued'):
            job_id = response['job_id']
            logger.warning(f"Evaluation exceeded sync timeout, polling job {job_id}...")
            return self.wait_for_result(job_id, poll_interval=2, timeout=120)
        
        return QuantumResult.from_response(response)
    
    # ----------------------------------
    # ASYNC METHODS
    # ----------------------------------
    
    def submit_async(
        self,
        data: Dict[str, List[float]],
        config: Union[Dict[str, Any], QuantumConfig],
        backend: str = 'simulator',
        shots: int = 1024,
        num_eval_qubits: int = 6,
        ibm_credentials: Optional[Dict[str, str]] = None
    ) -> str:
            
        
        # Convert QuantumConfig to dict if needed
        if isinstance(config, QuantumConfig):
            config = config.to_dict()
        
        # Validate inputs
        self._validate_config(config)
        self._validate_data(data, config)
        
        if backend not in ['simulator', 'ibm_quantum']:
            raise ValidationError("backend must be 'simulator' or 'ibm_quantum'")
        
        if backend == 'ibm_quantum' and not ibm_credentials:
            raise ValidationError("ibm_credentials required for IBM backend")
        
        if ibm_credentials:
            if not isinstance(ibm_credentials, dict) or 'token' not in ibm_credentials:
                raise ValidationError("ibm_credentials must contain 'token'")
        
        # Build payload
        payload = {
            'data': data,
            'config': config,
            'backend': backend,
            'shots': shots
        }
        
        if backend == 'simulator':
            payload['num_eval_qubits'] = num_eval_qubits
        
        if self.license_key:
            payload['license_key'] = self.license_key
        
        if ibm_credentials:
            payload['ibm_credentials'] = ibm_credentials
        
        # Submit to async queue (POST /enqueue)
        response = self._make_request('enqueue', payload)
        job_id = response.get('job_id')
        
        if not job_id:
            raise APIError("Server did not return job_id")
        
        logger.info(f"Quantum job submitted: {job_id} (backend: {backend})")
        return job_id
    
    def wait_for_result(self, job_id: str, timeout: int = 7200, poll_interval: int = 30) -> dict:
        """Espera resultados consultando endpoint de status."""
        start = time.time()
        
        while time.time() - start < timeout:
            try:
                resp = requests.get(f"{self.base_url}/evaluate/status/{job_id}", timeout=10) 
                
                if resp.status_code == 404:
                    print(f"⚠️ Job {job_id} no encontrado")
                    time.sleep(poll_interval)
                    continue
                
                resp.raise_for_status()
                data = resp.json()
                status = data.get("status")
                
                if status == "completed":
                    result = data.get("result", {})
                    return result
                elif status == "failed":
                    raise Exception(data.get("error", "Job failed"))
                
                elif status in ["queued", "running", "queued_ibm", "queued_global"]:
                    print(f"⏳ Processing... | Status: {status} | Esperando {poll_interval}s") 
                else:
                    print(f"⏳ Processing (Status: {status}) | Esperando {poll_interval}s")
                
                time.sleep(poll_interval)
            except Exception as e:
                print(f"❌ Error: {e} | Esperando {poll_interval}s") # También se hace más informativo el mensaje de error
                time.sleep(poll_interval)
        
        raise TimeoutError(f"Job {job_id} timeout después de {timeout}s")
    
    def get_job_status(self, job_id: str) -> JobStatus:
       
        base = self.base_url.rstrip("/")
        url = f"{base}/status/{job_id}"
        
        try:
            resp = self.session.get(url, timeout=self.timeout, verify=self.verify_ssl)
            if resp.status_code == 200:
                result = resp.json()
                logger.debug(f"Job {job_id} status: {result.get('status')}")
                return JobStatus.from_response(result)
        except:
            pass
        
        # Fallback to POST
        response = self._make_request('status', {'job_id': job_id})
        return JobStatus.from_response(response)
    
       
    def evaluate_async(
        self,
        data: Dict[str, List[float]],
        config: Union[Dict[str, Any], QuantumConfig],
        backend: str = 'simulator',
        shots: int = 1024,
        num_eval_qubits: int = 6,
        ibm_credentials: Optional[Dict[str, str]] = None,
        poll_interval: int = 5,
        timeout: int = 600
    ) -> QuantumResult:
        
        job_id = self.submit_async(
            data, config, backend, shots, num_eval_qubits, ibm_credentials
        )
        logger.info(f"Quantum job submitted: {job_id}, polling every {poll_interval}s")
        return self.wait_for_result(job_id, poll_interval, timeout)
    
    def healthcheck(self) -> Dict[str, Any]:
        """Check API health status"""
        url = urljoin(self.base_url, 'health')
        response = self.session.get(url, timeout=10)
        return response.json()
    
    def create_config(self) -> QuantumConfig:
       
        return QuantumConfig()
    
    def close(self):
        """Close session and cleanup"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def __repr__(self):
        return f"QuantumSDK(url='{self.base_url}', backend='simulator|ibm_quantum')"


# ----------------------------------
# HELPER FUNCTIONS
# ----------------------------------

def create_block(
    name: str,
    influence: List[float],
    priority: List[float],
    risk_adjustment: float = 0.0,
    block_influence: float = 1.0,
    block_priority: float = 1.0
) -> Block:
    
    return Block(
        name=name,
        influence=influence,
        priority=priority,
        risk_adjustment=risk_adjustment,
        block_influence=block_influence,
        block_priority=block_priority
    )


def create_config(blocks: List[Block], global_adjustment: float = 0.0) -> QuantumConfig:
    
    config = QuantumConfig()
    for block in blocks:
        config.add_block(
            name=block.name,
            influence=block.influence,
            priority=block.priority,
            risk_adjustment=block.risk_adjustment,
            block_influence=block.block_influence,
            block_priority=block.block_priority
        )
    config.set_global_adjustment(global_adjustment)
    return config