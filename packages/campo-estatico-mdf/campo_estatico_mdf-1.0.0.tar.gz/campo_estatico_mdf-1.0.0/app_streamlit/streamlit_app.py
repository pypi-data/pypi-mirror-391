# app_streamlit/streamlit_app.py
import time
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

from campo_estatico_mdf import LaplaceSolver2D

st.set_page_config(
    page_title="Solución 2D: Laplace por MDF",
    page_icon="🧮",
    layout="wide",
)

st.title("🧮 Solución del campo electrostático 2D (MDF)")
st.caption("Métodos: Jacobi y Gauss-Seidel • El usuario define el mallado N y los contornos")

with st.sidebar:
    st.header("Parámetros de simulación")
    N = st.number_input("Tamaño de la malla (N × N)", min_value=11, max_value=401, value=51, step=2,
                        help="Usa impares moderados (31/51/101). Costo ~ O(N² · iter).")
    epsilon = st.number_input("ε (tolerancia de convergencia)", min_value=1e-8, max_value=1e-2, value=1e-5, step=1e-6, format="%.1e")
    max_iter = st.number_input("Máximo de iteraciones", min_value=1000, max_value=200000, value=20000, step=1000)
    method = st.selectbox("Método numérico", ["jacobi", "gauss_seidel"])

    st.subheader("Condiciones de contorno (Voltaje)")
    col_l, col_r = st.columns(2)
    with col_l:
        v_left = st.number_input("Izquierda (x=0)", value=1.0, step=0.1)
        v_top = st.number_input("Arriba (y=0)", value=0.0, step=0.1)
    with col_r:
        v_right = st.number_input("Derecha (x=Lx)", value=0.0, step=0.1)
        v_bottom = st.number_input("Abajo (y=Ly)", value=1.0, step=0.1)

    Lx = st.number_input("Lx (longitud en x)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
    Ly = st.number_input("Ly (longitud en y)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)

    run_btn = st.button("▶️ Ejecutar simulación", use_container_width=True)

# Contenedor de resultados
status = st.empty()
col_v, col_e = st.columns([1.1, 1.0])

# Validación ligera
if run_btn:
    try:
        bc = {"left": float(v_left), "right": float(v_right),
              "top": float(v_top), "bottom": float(v_bottom)}
        solver = LaplaceSolver2D(
            N=int(N), bc=bc,
            epsilon=float(epsilon),
            max_iter=int(max_iter),
            method=str(method),
            Lx=float(Lx), Ly=float(Ly)
        )

        t0 = time.perf_counter()
        V, n_iter, err = solver.solve()
        Ex, Ey = solver.compute_e_field(V)
        t1 = time.perf_counter()

        status.success(f" Convergencia en {n_iter} iteraciones · error final = {err:.3e} · tiempo = {t1 - t0:.2f}s")

        # ---- Figura 1: Heatmap de V ----
        with col_v:
            st.subheader("Mapa de potencial V(x,y)")
            fig1, ax1 = plt.subplots()
            im = ax1.imshow(V, origin="upper", extent=[0, Lx, Ly, 0])
            ax1.set_xlabel("x")
            ax1.set_ylabel("y")
            ax1.set_title("Potencial V (unidades arbitrarias)")
            plt.colorbar(im, ax=ax1, shrink=0.9, label="V")
            st.pyplot(fig1, use_container_width=True)
            plt.close(fig1)

        # ---- Figura 2: Quiver del campo E ----
        with col_e:
            st.subheader("Campo eléctrico E(x,y) = −∇V")
            # Submuestreo para que el quiver sea legible
            step = max(1, int(N // 25))  # aprox 25 flechas por eje
            y = np.linspace(0, Ly, N)
            x = np.linspace(0, Lx, N)
            X, Y = np.meshgrid(x, y)

            fig2, ax2 = plt.subplots()
            ax2.quiver(X[::step, ::step], Y[::step, ::step],
                       Ex[::step, ::step], Ey[::step, ::step],
                       pivot="mid", scale=50)
            ax2.set_xlim([0, Lx])
            ax2.set_ylim([Ly, 0])  # y=0 arriba en la imagen original
            ax2.set_xlabel("x")
            ax2.set_ylabel("y")
            ax2.set_title("Campo E (dirección y magnitud relativa)")
            st.pyplot(fig2, use_container_width=True)
            plt.close(fig2)

        # ---- Métricas adicionales ----
        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Iteraciones", f"{n_iter}")
        c2.metric("Error final", f"{err:.3e}")
        c3.metric("dx", f"{solver.dx:.3e}")
        c4.metric("dy", f"{solver.dy:.3e}")

        with st.expander("Historial de error (primeros 10 y últimos 10)"):
            hist = solver.err_hist_
            st.write("Longitud:", len(hist))
            st.write("Primeros 10:", [f"{h:.2e}" for h in hist[:10]])
            st.write("Últimos 10:", [f"{h:.2e}" for h in hist[-10:]])

    except Exception as ex:
        status.error(f" Error en la simulación: {ex}")
else:
    st.info("Configura los parámetros en la barra lateral y presiona **Ejecutar simulación**.")
