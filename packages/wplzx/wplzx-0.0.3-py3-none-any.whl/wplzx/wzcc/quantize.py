import numpy as np

def theta_from_triplet_wzcc(a: int, alpha: float, k: float) -> float:
    """theta = alpha + 2π k / a (WZCC 관점 동일식)"""
    if a <= 0:
        raise ValueError("a must be positive")
    return float(alpha + 2.0*np.pi*(k/a))

def snap_phase(theta: float, a: int, alpha0: float = 0.0) -> float:
    """
    그리드: alpha0 + 2π*n/a 에 theta를 가장 가까운 점으로 스냅.
    - a: 그리드 분해능(예: a=8 → T-격자)
    - alpha0: 기준 오프셋(기본 0)
    """
    if a <= 0:
        raise ValueError("a must be positive")
    step = 2.0*np.pi / a
    n = round((theta - alpha0) / step)
    return float(alpha0 + n*step)
