# campo-estatico-mdf

Solver 2D de Laplace por diferencias finitas (Jacobi/Gauss-Seidel) y cálculo del campo eléctrico.
Incluye GUI en **Streamlit** (multipágina) y, en Fase 4, documentación **Sphinx**.

## Ejecutar GUI (Streamlit)
```bash
# activar entorno
source .venv/Scripts/activate   # Windows (Git Bash)
# pip install dependencias
pip install -r requirements.txt
# instalar paquete backend en editable
pip install -e .
# correr la app
streamlit run app_streamlit/streamlit_app.py
```

### Páginas
- **Simulación**: define N, ε, max_iter, método, y contornos. Muestra `V`, `E` y métricas.
- **Documentación**: enlaza/embebe Sphinx (se publicará en Fase 4). Puedes exportar `DOCS_URL` para mostrarla en la app.

> Si ves problemas con el render de quiver en mallas muy grandes, reduce N o sube el `step` de submuestreo.
