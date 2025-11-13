# examples/placa_basica.py
import numpy as np
from campo_estatico_mdf import LaplaceSolver2D

def main():
    # Mallado y contornos (ejemplo clásico: dos lados a 1.0 V y dos a 0.0 V)
    N = 51
    bc = {
        "left": 1.0,     # x=0
        "right": 0.0,    # x=Lx
        "top": 0.0,      # y=0
        "bottom": 1.0    # y=Ly
    }

    solver = LaplaceSolver2D(
        N=N,
        bc=bc,
        epsilon=1e-5,
        max_iter=20000,
        method="jacobi",    # cambia a "gauss_seidel" para probar el otro
        Lx=1.0,
        Ly=1.0
    )

    V, n_iter, err = solver.solve()
    Ex, Ey = solver.compute_e_field(V)

    print(f"[OK] Convergencia: iteraciones = {n_iter}, error final = {err:.3e}")
    print(f"V.shape = {V.shape}, Ex.mean={Ex.mean():.3e}, Ey.mean={Ey.mean():.3e}")

if __name__ == "__main__":
    main()
