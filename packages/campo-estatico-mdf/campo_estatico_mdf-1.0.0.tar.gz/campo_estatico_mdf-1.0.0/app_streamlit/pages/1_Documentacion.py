# app_streamlit/pages/1_Documentacion.py
import os
import streamlit as st

st.set_page_config(page_title="Documentación", page_icon="📚", layout="wide")

st.title("📚 Documentación del proyecto (Sphinx)")
st.write(
    """
Esta página muestra/enlaza la documentación técnica generada con **Sphinx**:

- Derivación breve del stencil MDF y de los métodos iterativos (Jacobi / Gauss-Seidel).
- Referencia de la API (`LaplaceSolver2D`).
- Tutoriales y ejemplos.

En la **Fase 4**, publicaremos la documentación en **GitHub Pages** y la incrustaremos aquí.
"""
)

# Definir una variable de entorno DOCS_URL
docs_url = "https://SanCriolloB.github.io/campo-estatico-mdf/"

if docs_url:
    st.success("Documentación publicada. Abre el enlace o usa el iframe más abajo.")
    st.markdown(f"🔗 **Abrir documentación:** [{docs_url}]({docs_url})")
    with st.expander("Ver en esta página (iframe)"):
        try:
            import streamlit.components.v1 as components
            components.iframe(docs_url, height=800, scrolling=True)
        except Exception as e:
            st.warning(f"No fue posible incrustar el iframe: {e}")
else:
    st.info(
        "Aún no hay URL publicada. Cuando la tengamos (Fase 4), "
        "configuraremos la variable de entorno **DOCS_URL** para mostrarla aquí."
    )
