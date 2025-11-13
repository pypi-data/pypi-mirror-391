Tutorial
========

Ejemplo básico de uso:

.. code-block:: python

   from campo_estatico_mdf import LaplaceSolver2D

   N = 51
   bc = {"left": 1.0, "right": 0.0, "top": 0.0, "bottom": 1.0}
   solver = LaplaceSolver2D(N=N, bc=bc, epsilon=1e-5, max_iter=20000, method="jacobi")

   V, n_iter, err = solver.solve()
   Ex, Ey = solver.compute_e_field(V)

   print(f"Iteraciones: {n_iter}, Error final: {err:.3e}")
