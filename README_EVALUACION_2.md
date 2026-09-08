# Segunda Evaluación Formativa FUESMEN 2026

Evaluación interactiva de las unidades 6, 7 y 8 del Curso de Metodología y Aplicación de Radioisótopos. Incluye cuatro ejercicios guiados de cálculo y 30 preguntas conceptuales.

## Archivos que se suben al mismo repositorio de GitHub

- `app_evaluacion_2.py`: aplicación de la segunda evaluación.
- `questions_evaluacion_2.json`: preguntas y opciones, sin la clave de respuestas.
- `README_EVALUACION_2.md`: estas instrucciones.

El archivo `requirements.txt` existente sirve para las dos evaluaciones y no necesita modificaciones.

## Archivo que NO debe subirse a GitHub

- `NO_SUBIR_A_GITHUB_google_apps_script.gs`

Este archivo contiene la clave de corrección. Debe pegarse únicamente en Apps Script, dentro de la misma planilla de Google Sheets utilizada por la primera evaluación.

## Actualizar el sistema de Google Sheets

1. Abrir la planilla que ya registra la primera evaluación.
2. Ir a **Extensiones > Apps Script**.
3. Reemplazar el código anterior por el contenido completo de `NO_SUBIR_A_GITHUB_google_apps_script.gs`.
4. Guardar el proyecto.
5. Ir a **Implementar > Administrar implementaciones**.
6. Editar la implementación existente.
7. Seleccionar **Nueva versión** y presionar **Implementar**.

Al actualizar la implementación existente, la dirección terminada en `/exec` se conserva. La primera evaluación seguirá guardándose en las pestañas `Resumen` y `Respuestas`.

La segunda evaluación creará automáticamente:

- `Resumen_Evaluacion_2`: una fila por intento, con resultados de las unidades 6, 7 y 8.
- `Respuestas_Evaluacion_2`: una fila por pregunta respondida.
- `Calculos_Evaluacion_2`: una fila por cada paso de los cuatro ejercicios guiados.

Cada intento utiliza un identificador único. Si Streamlit repite el envío por una recarga, Apps Script reconoce el identificador y no duplica las filas.

## Crear la segunda aplicación en Streamlit

1. Subir a la raíz del repositorio `app_evaluacion_2.py` y `questions_evaluacion_2.json`.
2. Entrar en Streamlit Community Cloud.
3. Crear una aplicación nueva seleccionando el mismo repositorio y la misma rama.
4. En **Main file path**, escribir `app_evaluacion_2.py`.
5. En **Settings > Secrets**, usar el mismo secreto de la primera evaluación:

```toml
RESULTS_WEBHOOK_URL = "URL_DE_LA_IMPLEMENTACION_DE_APPS_SCRIPT"
```

6. Implementar la aplicación.

## Prueba obligatoria antes de compartirla

1. Ingresar un nombre y DNI de prueba.
2. Completar los cuatro ejercicios guiados y comprobar ecuaciones, unidades y resultados.
3. Responder las 30 preguntas.
4. Verificar la corrección y la retroalimentación de cada pregunta.
5. Confirmar el resultado total y por unidad.
6. Revisar que aparezca una fila en `Resumen_Evaluacion_2`.
7. Revisar que aparezcan 30 filas en `Respuestas_Evaluacion_2`.
8. Revisar los pasos registrados en `Calculos_Evaluacion_2`.
9. Recargar la pantalla final y comprobar que no se dupliquen los registros.

## Seguridad

La clave no está incluida en `questions_evaluacion_2.json` ni en `app_evaluacion_2.py`. La corrección se realiza en el servicio privado de Google y la respuesta correcta se devuelve únicamente después de que el alumno selecciona una opción.
