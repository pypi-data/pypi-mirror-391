# campo_estatico_mdf/solver.py
from __future__ import annotations
import numpy as np
from typing import Dict, Tuple, Optional

class LaplaceSolver2D:
    """
    Resuelve la ecuación de Laplace en 2D con MDF (stencil de 5 puntos) y condiciones
    de borde Dirichlet. Ofrece Jacobi y Gauss-Seidel, y calcula E = -∇V.
    """

    def __init__(
        self,
        N: int,
        bc: Dict[str, float],
        epsilon: float = 1e-5,
        max_iter: int = 50_000,
        method: str = "jacobi",
        Lx: float = 1.0,
        Ly: float = 1.0,
        seed: Optional[int] = None,
    ) -> None:
        """
        Parámetros
        ----------
        N : int
            Tamaño del mallado (N×N). N >= 3 recomendado.
        bc : dict
            Voltajes de contorno. Claves: 'left','right','top','bottom'.
        epsilon : float
            Tolerancia de convergencia (max|ΔV| < epsilon).
        max_iter : int
            Máximo de iteraciones.
        method : str
            "jacobi" o "gauss_seidel".
        Lx, Ly : float
            Dimensiones físicas del dominio (para dx, dy).
        seed : int | None
            Semilla opcional para reproducibilidad si se añade ruido inicial.
        """
        if N < 3:
            raise ValueError("N debe ser >= 3")
        self.N = int(N)
        self.bc = self._validate_bc(bc)
        self.epsilon = float(epsilon)
        self.max_iter = int(max_iter)
        self.method = method.lower()
        if self.method not in {"jacobi", "gauss_seidel"}:
            raise ValueError("method debe ser 'jacobi' o 'gauss_seidel'")

        self.Lx = float(Lx)
        self.Ly = float(Ly)
        self.dx = self.Lx / (self.N - 1)
        self.dy = self.Ly / (self.N - 1)

        if seed is not None:
            np.random.seed(seed)

        # Matriz de potencial
        self.V = np.zeros((self.N, self.N), dtype=np.float64)
        self._init_grid()

        # Resultados
        self.n_iter_: Optional[int] = None
        self.err_hist_: list[float] = []

    @staticmethod
    def _validate_bc(bc: Dict[str, float]) -> Dict[str, float]:
        keys = {"left", "right", "top", "bottom"}
        if not keys.issubset(set(bc.keys())):
            raise KeyError("bc debe incluir 'left','right','top','bottom'")
        return {k: float(bc[k]) for k in keys}

    # -------------------------
    # Inicialización y contorno
    # -------------------------
    def _init_grid(self) -> None:
        """Inicializa V y aplica condiciones de contorno Dirichlet."""
        self.V.fill(0.0)
        self._apply_boundary_conditions(self.V)

    @staticmethod
    def _apply_boundary_conditions(V: np.ndarray, bc: Optional[Dict[str, float]] = None) -> None:
        """
        Aplica los contornos Dirichlet sobre V.
        Si bc es None, se asume que V ya trae la info de borde (no hace nada).
        """
        # Para permitir uso sin bc explícito, se usa atributo por fuera.
        # Método estático con bc opcional para reuso en Jacobi.
        if bc is None:
            return
        N = V.shape[0]
        V[:, 0] = bc["left"]      # x = 0
        V[:, -1] = bc["right"]    # x = Lx
        V[0, :] = bc["top"]       # y = 0   (fila 0 es "arriba")
        V[-1, :] = bc["bottom"]   # y = Ly  (fila -1 es "abajo")

    # -------------------------
    # Solución numérica
    # -------------------------
    def solve(self) -> Tuple[np.ndarray, int, float]:
        """
        Ejecuta el solver seleccionado.

        Returns
        -------
        V : np.ndarray
            Potencial convergido (N×N).
        n_iter : int
            Número de iteraciones realizadas.
        err_final : float
            Error máximo en la última iteración.
        """
        if self.method == "jacobi":
            return self._solve_jacobi()
        else:
            return self._solve_gauss_seidel()

    def _solve_jacobi(self) -> Tuple[np.ndarray, int, float]:
        N = self.N
        V = self.V.copy()
        V_new = V.copy()
        self.err_hist_.clear()

        for k in range(1, self.max_iter + 1):
            # Promedio de vecinos (interior)
            V_new[1:-1, 1:-1] = 0.25 * (
                V[2:, 1:-1] + V[:-2, 1:-1] + V[1:-1, 2:] + V[1:-1, :-2]
            )

            # Reimponer contornos
            self._apply_boundary_conditions(V_new, self.bc)

            # Criterio de convergencia
            err = float(np.max(np.abs(V_new - V)))
            self.err_hist_.append(err)
            if err < self.epsilon:
                self.V = V_new
                self.n_iter_ = k
                return self.V, self.n_iter_, err

            # Siguiente iteración
            V, V_new = V_new, V

        # No convergió dentro de max_iter
        self.V = V
        self.n_iter_ = self.max_iter
        return self.V, self.n_iter_, self.err_hist_[-1]

    def _solve_gauss_seidel(self) -> Tuple[np.ndarray, int, float]:
        N = self.N
        V = self.V.copy()
        self.err_hist_.clear()

        for k in range(1, self.max_iter + 1):
            err_max = 0.0
            # Actualización in-place (usa valores recién actualizados)
            for i in range(1, N - 1):
                for j in range(1, N - 1):
                    nuevo = 0.25 * (V[i + 1, j] + V[i - 1, j] + V[i, j + 1] + V[i, j - 1])
                    diff = abs(nuevo - V[i, j])
                    if diff > err_max:
                        err_max = diff
                    V[i, j] = nuevo

            # Reimponer contornos (por seguridad numérica)
            self._apply_boundary_conditions(V, self.bc)

            self.err_hist_.append(err_max)
            if err_max < self.epsilon:
                self.V = V
                self.n_iter_ = k
                return self.V, self.n_iter_, err_max

        self.V = V
        self.n_iter_ = self.max_iter
        return self.V, self.n_iter_, self.err_hist_[-1]

    # -------------------------
    # Campo eléctrico
    # -------------------------
    def compute_e_field(self, V: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calcula el campo eléctrico E = -∇V. Por convención:
        Ex = -∂V/∂x, Ey = -∂V/∂y

        Usa numpy.gradient con espaciamientos dx, dy.
        """
        if V is None:
            V = self.V
        # Nota: numpy.gradient devuelve derivadas respecto a cada eje en orden de ejes.
        # Para una matriz V[filas(y), columnas(x)]:
        # dV_dy, dV_dx = np.gradient(V, dy, dx)
        dV_dy, dV_dx = np.gradient(V, self.dy, self.dx, edge_order=2)
        Ex = -dV_dx
        Ey = -dV_dy
        return Ex, Ey

    # -------------------------
    # Utilidades
    # -------------------------
    def reset(self) -> None:
        """Reinicia la malla a 0 y reimpone contornos."""
        self._init_grid()

    def solution(self) -> np.ndarray:
        """Devuelve la última solución V."""
        return self.V

    def convergence_info(self) -> Tuple[Optional[int], list[float]]:
        """Devuelve (n_iter, historial_errores)."""
        return self.n_iter_, self.err_hist_
