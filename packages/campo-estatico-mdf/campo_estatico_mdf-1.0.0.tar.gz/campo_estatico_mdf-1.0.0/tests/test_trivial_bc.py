import numpy as np
from campo_estatico_mdf import LaplaceSolver2D

def test_trivial_all_zero_boundaries():
    N = 31
    bc = {"left": 0.0, "right": 0.0, "top": 0.0, "bottom": 0.0}
    solver = LaplaceSolver2D(
        N=N, bc=bc, epsilon=1e-6, max_iter=5000, method="jacobi", Lx=1.0, Ly=1.0
    )
    V, n_iter, err = solver.solve()

    # Toda la solución debe ser ~0 (dentro de tolerancia)
    assert np.allclose(V, 0.0, atol=5e-5)

    # Campo eléctrico debe ser ~0 también
    Ex, Ey = solver.compute_e_field(V)
    assert np.allclose(Ex, 0.0, atol=5e-4)
    assert np.allclose(Ey, 0.0, atol=5e-4)

    # Convergencia registrada
    assert err < solver.epsilon
    assert n_iter <= solver.max_iter
