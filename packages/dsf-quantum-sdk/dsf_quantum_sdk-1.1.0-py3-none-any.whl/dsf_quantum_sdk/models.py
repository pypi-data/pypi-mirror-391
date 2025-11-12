# dsf_quantum_sdk/models.py
"""Data models for Quantum SDK"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class Block:
    """
    Block configuration for hierarchical quantum scoring.
    
    Attributes:
        name: Block identifier (must match data keys)
        influence: Weight per value in block
        priority: Criticality per value in block
        risk_adjustment: Penalty factor (0.0-1.0)
        block_influence: Global weight for this block
        block_priority: Global criticality for this block
    """
    name: str
    influence: List[float]
    priority: List[float]
    risk_adjustment: float = 0.0
    block_influence: float = 1.0
    block_priority: float = 1.0
    
    def __post_init__(self):
        """Validate block configuration"""
        if not self.name:
            raise ValueError("Block name cannot be empty")
        
        if not isinstance(self.influence, list) or len(self.influence) == 0:
            raise ValueError(f"Block '{self.name}' influence must be non-empty list")
        
        if not isinstance(self.priority, list) or len(self.priority) == 0:
            raise ValueError(f"Block '{self.name}' priority must be non-empty list")
        
        if len(self.influence) != len(self.priority):
            raise ValueError(
                f"Block '{self.name}' influence and priority must have same length"
            )
        
        if not 0.0 <= self.risk_adjustment <= 1.0:
            raise ValueError(f"Block '{self.name}' risk_adjustment must be 0.0-1.0")
    
    def to_dict(self) -> Dict:
        """Convert to API-compatible dictionary."""
        return {
            'name': self.name,
            'influence': self.influence,
            'priority': self.priority,
            'risk_adjustment': self.risk_adjustment,
            'block_influence': self.block_influence,
            'block_priority': self.block_priority
        }
    
    def __repr__(self):
        return (f"Block(name='{self.name}', "
                f"size={len(self.influence)}, "
                f"risk={self.risk_adjustment:.2f})")


class QuantumConfig:
    """
    Configuration builder for hierarchical quantum scoring.
    
    Example:
        >>> config = QuantumConfig()
        ...     .add_block('flujo_caja', 
        ...               influence=[0.5, 0.3, 0.2],
        ...               priority=[1.4, 1.2, 1.0],
        ...               risk_adjustment=0.1)
        ...     .add_block('comportamiento',
        ...               influence=[0.2, 0.3, 0.5],
        ...               priority=[1.8, 1.4, 1.0])
        ...     .set_global_adjustment(0.01)
    """
    
    def __init__(self):
        self.blocks: List[Block] = []
        self.global_adjustment: float = 0.0
    
    def add_block(
        self,
        name: str,
        influence: List[float],
        priority: List[float],
        risk_adjustment: float = 0.0,
        block_influence: float = 1.0,
        block_priority: float = 1.0
    ) -> 'QuantumConfig':
        """
        Add a block to configuration.
        
        Args:
            name: Block identifier (must match data keys)
            influence: Weight per value in block
            priority: Criticality per value in block
            risk_adjustment: Penalty factor (0.0-1.0)
            block_influence: Global weight for this block
            block_priority: Global criticality for this block
            
        Returns:
            Self for chaining
            
        Example:
            >>> config.add_block(
            ...     'flujo_caja',
            ...     influence=[0.5, 0.3, 0.2],
            ...     priority=[1.4, 1.2, 1.0],
            ...     risk_adjustment=0.1,
            ...     block_influence=0.8,
            ...     block_priority=1.2
            ... )
        """
        block = Block(
            name=name,
            influence=influence,
            priority=priority,
            risk_adjustment=risk_adjustment,
            block_influence=block_influence,
            block_priority=block_priority
        )
        self.blocks.append(block)
        return self
    
    def remove_block(self, name: str) -> 'QuantumConfig':
        """
        Remove a block from configuration.
        
        Args:
            name: Block name to remove
            
        Returns:
            Self for chaining
        """
        self.blocks = [b for b in self.blocks if b.name != name]
        return self
    
    def set_global_adjustment(self, adjustment: float) -> 'QuantumConfig':
        """
        Set global penalty adjustment.
        
        Args:
            adjustment: Global penalty factor (0.0-1.0)
            
        Returns:
            Self for chaining
        """
        if not 0.0 <= adjustment <= 1.0:
            raise ValueError("global_adjustment must be 0.0-1.0")
        self.global_adjustment = adjustment
        return self
    
    def to_dict(self) -> Dict:
        """Convert to API-compatible dictionary."""
        if not self.blocks:
            raise ValueError("Configuration must have at least one block")
        
        return {
            'blocks': [block.to_dict() for block in self.blocks],
            'global_adjustment': self.global_adjustment
        }
    
    def __repr__(self):
        block_names = [b.name for b in self.blocks]
        return f"QuantumConfig(blocks={block_names}, global_adj={self.global_adjustment})"


@dataclass
class QuantumResult:
    """
    Result from quantum evaluation.
    
    Attributes:
        score: Quantum score (0.0-1.0)
        backend: Backend used ('simulator' or 'ibm_quantum')
        execution_type: Execution method ('simulator_qae' or 'ibm_hardware')
        shots: Number of quantum measurements
        tier: License tier used
        job_id: Job ID if async execution
    """
    score: float
    backend: str = 'simulator'
    execution_type: str = 'simulator_qae'
    shots: int = 1024
    tier: str = 'free'
    job_id: Optional[str] = None
    
    @classmethod
    def from_response(cls, response: Dict) -> 'QuantumResult':
        """Create from API response."""
        return cls(
            score=response.get('score', 0.0),
            backend=response.get('backend', 'simulator'),
            execution_type=response.get('execution_type', 'simulator_qae'),
            shots=response.get('shots', 1024),
            tier=response.get('tier', 'free'),
            job_id=response.get('job_id')
        )
    
    @property
    def is_hardware(self) -> bool:
        """Check if executed on real quantum hardware."""
        return self.backend == 'ibm_quantum'
    
    @property
    def is_async(self) -> bool:
        """Check if this is an async job result."""
        return self.job_id is not None
    
    def __repr__(self):
        hw = "HW" if self.is_hardware else "SIM"
        return (f"QuantumResult(score={self.score:.4f}, "
                f"{hw}, shots={self.shots}, tier='{self.tier}')")


@dataclass
class JobStatus:
    """
    Status of async quantum job.
    
    Attributes:
        job_id: Job identifier
        status: Current status ('queued', 'running', 'completed', 'failed')
        created_at: Timestamp when job was created
        completed_at: Timestamp when job completed (if applicable)
        result: Result if completed
        error: Error message if failed
    """
    job_id: str
    status: str
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[QuantumResult] = None
    error: Optional[str] = None
    
    @classmethod
    def from_response(cls, response: Dict) -> 'JobStatus':
        """Create from API response."""
        result = None
        if response.get('status') == 'completed' and 'result' in response:
            result = QuantumResult.from_response(response['result'])
        
        return cls(
            job_id=response.get('job_id', ''),
            status=response.get('status', 'unknown'),
            created_at=response.get('created_at'),
            completed_at=response.get('completed_at'),
            result=result,
            error=response.get('error')
        )
    
    @property
    def is_completed(self) -> bool:
        """Check if job completed successfully."""
        return self.status == 'completed'
    
    @property
    def is_failed(self) -> bool:
        """Check if job failed."""
        return self.status == 'failed'
    
    @property
    def is_running(self) -> bool:
        """Check if job is currently running."""
        return self.status in ('queued', 'running')
    
    def __repr__(self):
        return f"JobStatus(id='{self.job_id}', status='{self.status}')"