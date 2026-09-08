import json
import uuid
from pathlib import Path
from datetime import datetime

import pandas as pd
import requests
import streamlit as st


st.set_page_config(
    page_title="FUESMEN | Segunda Evaluación Formativa",
    page_icon="☢️",
    layout="centered",
)

BASE_DIR = Path(__file__).resolve().parent
EVALUACION_ID = "evaluacion_2"


@st.cache_data
def cargar_banco():
    return json.loads(
        (BASE_DIR / "questions_evaluacion_2.json").read_text(encoding="utf-8")
    )


BANCO = cargar_banco()
TOTAL = sum(len(unidad["questions"]) for unidad in BANCO)


def inicializar_estado():
    valores = {
        "iniciado": False,
        "unidad": 0,
        "pregunta": 0,
        "respondida": False,
        "seleccion": None,
        "resultados": [],
        "nombre": "",
        "dni": "",
        "guardado": False,
        "error_guardado": "",
        "intento_id": "",
        "resumen_oficial": None,
    }
    for clave, valor in valores.items():
        if clave not in st.session_state:
            st.session_state[clave] = valor


def obtener_webhook():
    try:
        return st.secrets["RESULTS_WEBHOOK_URL"]
    except Exception:
        return None


def enviar_a_google(payload):
    url = obtener_webhook()
    if not url:
        return None, "No está configurado RESULTS_WEBHOOK_URL en Streamlit Secrets."

    try:
        respuesta = requests.post(url, json=payload, timeout=20)
        if not respuesta.ok:
            return None, f"Error HTTP {respuesta.status_code}: {respuesta.text[:200]}"
        datos = respuesta.json()
        if not datos.get("ok"):
            return None, datos.get("error", "Google devolvió una respuesta no válida.")
        return datos, ""
    except Exception as error:
        return None, f"No se pudo conectar con el sistema de registro: {error}"


def comprobar_respuesta(id_pregunta, seleccion):
    return enviar_a_google(
        {
            "evaluacion_id": EVALUACION_ID,
            "accion": "comprobar",
            "id_pregunta": id_pregunta,
            "seleccion": seleccion,
        }
    )


def guardar_resultado():
    if st.session_state.guardado:
        return True

    payload = {
        "evaluacion_id": EVALUACION_ID,
        "accion": "guardar",
        "intento_id": st.session_state.intento_id,
        "fecha_hora_cliente": datetime.now().isoformat(timespec="seconds"),
        "nombre": st.session_state.nombre,
        "dni": st.session_state.dni,
        "respuestas": [
            {
                "id_pregunta": fila["id_pregunta"],
                "seleccion": fila["seleccion"],
            }
            for fila in st.session_state.resultados
        ],
    }

    datos, error = enviar_a_google(payload)
    if datos:
        st.session_state.guardado = True
        st.session_state.error_guardado = ""
        st.session_state.resumen_oficial = datos
        return True

    st.session_state.error_guardado = error
    return False


def avanzar():
    st.session_state.respondida = False
    st.session_state.seleccion = None

    u = st.session_state.unidad
    p = st.session_state.pregunta

    if p + 1 < len(BANCO[u]["questions"]):
        st.session_state.pregunta += 1
    elif u + 1 < len(BANCO):
        st.session_state.unidad += 1
        st.session_state.pregunta = 0
    else:
        st.session_state.unidad = len(BANCO)


def reiniciar():
    st.session_state.iniciado = False
    st.session_state.unidad = 0
    st.session_state.pregunta = 0
    st.session_state.respondida = False
    st.session_state.seleccion = None
    st.session_state.resultados = []
    st.session_state.nombre = ""
    st.session_state.dni = ""
    st.session_state.guardado = False
    st.session_state.error_guardado = ""
    st.session_state.intento_id = ""
    st.session_state.resumen_oficial = None


inicializar_estado()

st.title("Segunda Evaluación Formativa")
st.subheader("Curso de Metodología y Aplicación de Radioisótopos")
st.caption("Fundación Escuela de Medicina Nuclear (FUESMEN)")

if not st.session_state.iniciado:
    st.info(
        "Esta actividad es formativa y no posee calificación oficial. "
        "La corrección inmediata y las explicaciones funcionan como guía de estudio."
    )

    nombre = st.text_input("Apellido y nombre")
    dni = st.text_input("DNI")

    st.markdown(
        """
        **Cómo funciona**

        - 30 preguntas: 10 por unidad.
        - Incluye las unidades 6, 7 y 8.
        - Elegís una opción y presionás **Comprobar**.
        - Después de responder verás la corrección y una explicación.
        - Al finalizar verás el resultado total y por unidad.
        - Podés volver a intentarlo.
        """
    )

    if st.button("Comenzar evaluación", type="primary", use_container_width=True):
        if not nombre.strip() or not dni.strip():
            st.warning("Completá apellido y nombre y DNI para comenzar.")
        else:
            st.session_state.nombre = nombre.strip()
            st.session_state.dni = dni.strip()
            st.session_state.intento_id = str(uuid.uuid4())
            st.session_state.iniciado = True
            st.rerun()

elif st.session_state.unidad < len(BANCO):
    u = st.session_state.unidad
    p = st.session_state.pregunta
    unidad = BANCO[u]
    pregunta = unidad["questions"][p]

    respondidas = len(st.session_state.resultados)
    st.progress(respondidas / TOTAL)
    st.caption(f"Pregunta {respondidas + 1} de {TOTAL}")
    st.header(unidad["unit"])
    st.markdown(f"### Pregunta {p + 1}")
    st.write(pregunta["q"])

    seleccion = st.radio(
        "Elegí una opción:",
        options=list(range(len(pregunta["opts"]))),
        format_func=lambda indice: pregunta["opts"][indice],
        index=None,
        disabled=st.session_state.respondida,
        key=f"radio_{pregunta['id']}",
    )

    if not st.session_state.respondida:
        if st.button("Comprobar", type="primary", use_container_width=True):
            if seleccion is None:
                st.warning("Seleccioná una respuesta antes de comprobar.")
            else:
                datos, error = comprobar_respuesta(pregunta["id"], seleccion)
                if not datos:
                    st.error(error)
                else:
                    indice_correcto = int(datos["indice_correcto"])
                    st.session_state.respondida = True
                    st.session_state.seleccion = seleccion
                    st.session_state.resultados.append(
                        {
                            "unidad": unidad["unit"],
                            "numero_unidad": u + 6,
                            "numero_pregunta": p + 1,
                            "id_pregunta": pregunta["id"],
                            "pregunta": pregunta["q"],
                            "seleccion": seleccion,
                            "respuesta_elegida": pregunta["opts"][seleccion],
                            "respuesta_correcta": pregunta["opts"][indice_correcto],
                            "correcta": bool(datos["correcta"]),
                            "feedback": datos["feedback"],
                        }
                    )
                    st.rerun()
    else:
        resultado = st.session_state.resultados[-1]
        if resultado["correcta"]:
            st.success("✅ ¡Correcto!")
        else:
            st.error("❌ Incorrecto.")
            st.markdown(f"**Respuesta correcta:** {resultado['respuesta_correcta']}")

        st.info(resultado["feedback"])

        texto_boton = "Siguiente pregunta"
        if p == len(unidad["questions"]) - 1 and u < len(BANCO) - 1:
            texto_boton = "Continuar con la siguiente unidad"
        elif u == len(BANCO) - 1 and p == len(unidad["questions"]) - 1:
            texto_boton = "Ver resultado final"

        if st.button(texto_boton, type="primary", use_container_width=True):
            avanzar()
            st.rerun()

else:
    if not st.session_state.guardado:
        guardar_resultado()

    resultados = pd.DataFrame(st.session_state.resultados)
    aciertos = int(resultados["correcta"].sum())
    porcentaje = round(aciertos / TOTAL * 100, 1)

    if st.session_state.resumen_oficial:
        aciertos = int(st.session_state.resumen_oficial["total_correctas"])
        porcentaje = float(st.session_state.resumen_oficial["porcentaje"])

    st.balloons()
    st.title("Resultado final")
    st.write(f"**Estudiante:** {st.session_state.nombre}")
    st.write(f"**DNI:** {st.session_state.dni}")

    columna_1, columna_2 = st.columns(2)
    columna_1.metric("Puntaje", f"{aciertos}/{TOTAL}")
    columna_2.metric("Porcentaje", f"{porcentaje}%")

    resumen = (
        resultados.groupby("unidad")["correcta"]
        .agg(["sum", "count"])
        .reset_index()
        .rename(columns={"unidad": "Unidad", "sum": "Correctas", "count": "Total"})
    )
    resumen["Resultado"] = (
        resumen["Correctas"].astype(str) + "/" + resumen["Total"].astype(str)
    )

    st.subheader("Resultado por unidad")
    st.dataframe(
        resumen[["Unidad", "Resultado"]],
        use_container_width=True,
        hide_index=True,
    )

    if porcentaje >= 80:
        st.success("Muy buen dominio general. Revisá especialmente las respuestas incorrectas.")
    elif porcentaje >= 60:
        st.warning("Buen punto de partida. Conviene repasar las unidades con menor resultado.")
    else:
        st.warning("Te recomendamos repasar los contenidos y volver a realizar la evaluación.")

    if st.session_state.guardado:
        st.success("Tus respuestas quedaron registradas correctamente.")
    else:
        st.warning("No se pudo registrar automáticamente el resultado.")
        if st.session_state.error_guardado:
            st.caption(st.session_state.error_guardado)
        if st.button("Reintentar el registro", use_container_width=True):
            guardar_resultado()
            st.rerun()

    csv = resumen.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Descargar mi resultado",
        data=csv,
        file_name="resultado_segunda_evaluacion_formativa_FUESMEN.csv",
        mime="text/csv",
        use_container_width=True,
    )

    if st.button("Volver a intentarlo", type="primary", use_container_width=True):
        reiniciar()
        st.rerun()

st.divider()
st.caption(
    "Segunda evaluación formativa – Curso de Metodología y Aplicación de Radioisótopos | FUESMEN"
)
