import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

__all__ = [
    "theta_from_triplet",
    "z_rotation_statevector",
]

def theta_from_triplet(a: int, alpha: float, k: float) -> float:
    """
    Map (a, alpha, k) in WPL-ZX to physical angle theta (radians):
        theta = alpha + 2*pi*k/a
    Notes
    -----
    - k can be fractional (e.g., 1/2) if your winding index is in (1/a)Z.
    - Returns a Python float.
    """
    if a <= 0:
        raise ValueError("a must be a positive integer")
    return float(alpha + 2.0 * np.pi * (k / a))

def z_rotation_statevector(theta: float) -> Statevector:
    """
    Build a 1-qubit circuit with an RZ(theta), return the statevector.
    """
    qc = QuantumCircuit(1)
    qc.rz(theta, 0)
    return Statevector.from_instruction(qc)
