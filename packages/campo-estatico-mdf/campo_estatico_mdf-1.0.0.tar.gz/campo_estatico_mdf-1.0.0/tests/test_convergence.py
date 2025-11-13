import numpy as np
from campo_estatico_mdf import LaplaceSolver2D

def test_convergence_classic_plate():
    N = 51
    # Dos lados a 1V y dos a 0V (problema clásico)
    bc = {"left": 1.0, "right": 0.0, "top": 0.0, "bottom": 1.0}
    solver = LaplaceSolver2D(
        N=N, bc=bc, epsilon=1e-5, max_iter=20000, method="jacobi", Lx=1.0, Ly=1.0
    )
    V, n_iter, err = solver.solve()

    # Converge dentro de max_iter con error final bajo
    assert err < solver.epsilon
    assert n_iter <= solver.max_iter

    # Potencial acotado entre min(bc) y max(bc) (propiedad física esperable con Dirichlet)
    vmin, vmax = min(bc.values()), max(bc.values())
    assert V.min() >= vmin - 1e-3
    assert V.max() <= vmax + 1e-3

    # Tamaño correcto
    assert V.shape == (N, N)
