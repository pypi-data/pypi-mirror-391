from wplzx.core import theta_from_triplet, z_rotation_statevector

def test_theta_and_state():
    a, alpha, k = 8, 3.14159/4, 1
    theta = theta_from_triplet(a, alpha, k)
    psi = z_rotation_statevector(theta)
    print("a, alpha, k =", a, alpha, k)
    print("→ Computed theta =", theta)
    print("→ Statevector =", psi)

if __name__ == "__main__":
    test_theta_and_state()
