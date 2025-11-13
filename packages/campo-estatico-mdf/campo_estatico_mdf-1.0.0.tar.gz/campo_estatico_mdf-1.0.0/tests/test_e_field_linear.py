import numpy as np
from campo_estatico_mdf import LaplaceSolver2D

def test_e_field_linear_synthetic():
    N = 40
    a, b, c = 2.0, -1.0, 0.5  # V = a x + b y + c
    bc = {"left": 0.0, "right": 0.0, "top": 0.0, "bottom": 0.0}

    # Creamos el solver solo para tener dx, dy y reutilizar compute_e_field
    solver = LaplaceSolver2D(
        N=N, bc=bc, epsilon=1e-6, max_iter=1, method="jacobi", Lx=1.0, Ly=1.0
    )

    # Construimos la malla física
    x = np.linspace(0.0, solver.Lx, N)
    y = np.linspace(0.0, solver.Ly, N)
    X, Y = np.meshgrid(x, y)  # Ojo: V[filas(y), columnas(x)]

    V = a * X + b * Y + c

    Ex, Ey = solver.compute_e_field(V)

    # Esperado: Ex ~ -a, Ey ~ -b (constantes)
    # Permitimos pequeña tolerancia por discretización de gradiente
    assert np.allclose(Ex.mean(), -a, atol=5e-3)
    assert np.allclose(Ey.mean(), -b, atol=5e-3)

    # Además, el desvío estándar debe ser pequeño (campo casi constante)
    assert Ex.std() < 5e-2
    assert Ey.std() < 5e-2
