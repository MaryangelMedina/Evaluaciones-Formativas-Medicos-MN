# Integrador FUESMEN 2026

App independiente para Unidades 9, 10 y 11. 60 preguntas; identificación, navegación, revisión y resultado final.

Desplegar como app NUEVA en Streamlit con ruta `examen_fuesmen_2026/app.py` y Python 3.12. No sustituye las apps de la raíz del repositorio.

Requiere un Google Apps Script NUEVO con contrato `fuesmen.integrador.v1` y Secrets `RESULTS_WEBHOOK_URL` y `RESULTS_WEBHOOK_TOKEN`. Sin un backend compatible, la app bloquea el inicio. La clave se aloja únicamente en el proyecto privado de Apps Script.

`secrets.example.toml` contiene sólo ejemplos. No subir credenciales ni el backend docente a GitHub. Las imágenes provienen de las clases FUESMEN aportadas para este examen.

La corrección se realiza al entregar; las soluciones no se muestran al alumno. El avance antes de la entrega permanece en la sesión y puede perderse al cerrarla o recargarla completamente.
