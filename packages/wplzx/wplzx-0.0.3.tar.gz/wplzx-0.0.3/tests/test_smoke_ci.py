import numpy as np
from wplzx.wzcc.quantize import theta_from_triplet_wzcc, snap_phase
from wplzx.wzcc.verify import statevector_from_rz, global_phase_equal

def test_wzcc_roundtrip():
    a, alpha, k = 8, np.pi/4, 1            # θ = π/2
    theta = theta_from_triplet_wzcc(a, alpha, k)
    theta_noisy = theta + 0.01             # 약간의 편차
    theta_snap = snap_phase(theta_noisy, a)

    psi = statevector_from_rz(theta_noisy)
    phi = statevector_from_rz(theta_snap)

    # CI에서 실제 검증: 스냅 후 상태가 전역 위상까지 동일해야 함
    assert global_phase_equal(psi, phi), "Snapped state must equal (up to phase)"
