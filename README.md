# Evaluación Formativa FUESMEN 2026

App interactiva en Streamlit para el Curso de Metodología y Aplicación de Radioisótopos.

## Qué hace

- 40 preguntas, 8 por unidad.
- Corrección inmediata.
- Muestra "Correcto" o "Incorrecto".
- Si es incorrecta, muestra la respuesta correcta.
- Retroalimentación pedagógica inmediata.
- Resultado total y por unidad.
- Permite volver a intentarlo.
- Permite descargar un CSV con el resultado personal.

## Archivos

- `app.py`: aplicación principal.
- `questions.json`: banco de preguntas.
- `requirements.txt`: dependencias.

## Subir a GitHub

1. Crear un repositorio nuevo en GitHub.
2. Subir estos tres archivos a la raíz del repositorio.
3. Confirmar los cambios.

## Publicar en Streamlit Community Cloud

1. Entrar a https://share.streamlit.io
2. Iniciar sesión con GitHub.
3. Elegir `Create app`.
4. Seleccionar el repositorio.
5. En `Main file path`, elegir `app.py`.
6. Presionar `Deploy`.

Una vez desplegada, la app tendrá una URL que puede enviarse por correo a los estudiantes.

## Importante sobre permanencia

El banco de preguntas queda guardado en GitHub y puede reutilizarse en futuras cohortes.

Los resultados individuales NO se guardan de forma centralizada en esta versión. Cada estudiante puede descargar su resultado al finalizar. Si se desea conservar automáticamente nombre, DNI, puntaje y respuestas, se puede agregar posteriormente una conexión a Google Sheets o una base de datos.

## Registro automático en Google Sheets

1. Crear una Google Sheet nueva.
2. En la planilla: Extensiones > Apps Script.
3. Pegar el contenido de `guardar_resultados_google_sheets.gs`.
4. Implementar > Nueva implementación > Aplicación web.
5. Ejecutar como: Yo.
6. Quién tiene acceso: Cualquiera.
7. Copiar la URL que termina en `/exec`.
8. En Streamlit Community Cloud > App > Settings > Secrets, agregar:

RESULTS_WEBHOOK_URL = "PEGAR_AQUI_LA_URL_DE_APPS_SCRIPT"

La planilla crea automáticamente dos hojas:
- `Resumen`: puntaje por unidad y total.
- `Respuestas`: una fila por pregunta con respuesta elegida, respuesta correcta y resultado.
