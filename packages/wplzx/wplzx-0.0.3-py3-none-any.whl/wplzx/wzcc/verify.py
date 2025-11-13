import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def statevector_from_rz(theta: float) -> Statevector:
    qc = QuantumCircuit(1)
    qc.rz(theta, 0)
    return Statevector.from_instruction(qc)

def global_phase_equal(psi: Statevector, phi: Statevector, tol: float = 1e-9) -> bool:
    """
    두 statevector가 전역 위상까지 같은지 검사.
    |<psi|phi>|가 1과 충분히 가까우면 True.
    """
    norm_psi = np.linalg.norm(psi.data)
    norm_phi = np.linalg.norm(phi.data)
    if abs(norm_psi - 1) > 1e-12:
        psi = psi / norm_psi
    if abs(norm_phi - 1) > 1e-12:
        phi = phi / norm_phi
    inner = (psi.data.conj() @ phi.data).item()
    return abs(abs(inner) - 1.0) <= tol

def phase_distance(psi: Statevector, phi: Statevector) -> float:
    """
    전역 위상을 최적으로 보정했을 때의 2-노름 거리.
    """
    inner = (psi.data.conj() @ phi.data).item()
    phase = np.exp(-1j * np.angle(inner)) if inner != 0 else 1.0
    return np.linalg.norm(psi.data - phase * phi.data)
