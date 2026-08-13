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
