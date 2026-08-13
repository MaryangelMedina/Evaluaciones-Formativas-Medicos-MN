
import streamlit as st
import json
from pathlib import Path
import pandas as pd

st.set_page_config(
    page_title="FUESMEN | Evaluación Formativa",
    page_icon="☢️",
    layout="centered"
)

@st.cache_data
def cargar_banco():
    return json.loads(Path("questions.json").read_text(encoding="utf-8"))

BANCO = cargar_banco()
TOTAL = sum(len(u["questions"]) for u in BANCO)

if "iniciado" not in st.session_state:
    st.session_state.iniciado = False
if "unidad" not in st.session_state:
    st.session_state.unidad = 0
if "pregunta" not in st.session_state:
    st.session_state.pregunta = 0
if "respondida" not in st.session_state:
    st.session_state.respondida = False
if "seleccion" not in st.session_state:
    st.session_state.seleccion = None
if "resultados" not in st.session_state:
    st.session_state.resultados = []
if "nombre" not in st.session_state:
    st.session_state.nombre = ""
if "dni" not in st.session_state:
    st.session_state.dni = ""

def reiniciar():
    st.session_state.iniciado = False
    st.session_state.unidad = 0
    st.session_state.pregunta = 0
    st.session_state.respondida = False
    st.session_state.seleccion = None
    st.session_state.resultados = []
    st.session_state.nombre = ""
    st.session_state.dni = ""

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

st.title("Evaluación Formativa")
st.subheader("Curso de Metodología y Aplicación de Radioisótopos")
st.caption("Fundación Escuela de Medicina Nuclear (FUESMEN)")

if not st.session_state.iniciado:
    st.info(
        "Esta actividad es formativa y no posee calificación oficial. "
        "La respuesta se corrige inmediatamente para que puedas utilizar la explicación como guía de estudio."
    )

    nombre = st.text_input("Apellido y nombre")
    dni = st.text_input("DNI")

    st.markdown(
        """
        **Cómo funciona**
        - 40 preguntas: 8 por unidad.
        - Elegís una respuesta y presionás **Comprobar**.
        - Inmediatamente verás si es correcta o incorrecta y la explicación.
        - Al final verás tu resultado total y por unidad.
        - Podés volver a intentarlo.
        """
    )

    if st.button("Comenzar evaluación", type="primary", use_container_width=True):
        if not nombre.strip() or not dni.strip():
            st.warning("Completá apellido y nombre y DNI para comenzar.")
        else:
            st.session_state.nombre = nombre.strip()
            st.session_state.dni = dni.strip()
            st.session_state.iniciado = True
            st.rerun()

elif st.session_state.unidad < len(BANCO):
    u = st.session_state.unidad
    p = st.session_state.pregunta
    unidad = BANCO[u]
    q = unidad["questions"][p]

    respondidas = len(st.session_state.resultados)
    st.progress(respondidas / TOTAL)
    st.caption(f"Pregunta {respondidas + 1} de {TOTAL}")
    st.header(unidad["unit"])
    st.markdown(f"### Pregunta {p + 1}")
    st.write(q["q"])

    seleccion = st.radio(
        "Elegí una opción:",
        options=list(range(len(q["opts"]))),
        format_func=lambda i: q["opts"][i],
        index=None,
        disabled=st.session_state.respondida,
        key=f"radio_{u}_{p}"
    )

    if not st.session_state.respondida:
        if st.button("Comprobar", type="primary", use_container_width=True):
            if seleccion is None:
                st.warning("Seleccioná una respuesta antes de comprobar.")
            else:
                correcta = seleccion == q["a"]
                st.session_state.respondida = True
                st.session_state.seleccion = seleccion
                st.session_state.resultados.append({
                    "unidad": unidad["unit"],
                    "pregunta": p + 1,
                    "correcta": correcta
                })
                st.rerun()
    else:
        correcta = st.session_state.seleccion == q["a"]

        if correcta:
            st.success("✅ ¡Correcto!")
        else:
            st.error("❌ Incorrecto.")
            st.markdown(
                f"**Respuesta correcta:** {q['opts'][q['a']]}"
            )

        st.info(q["fb"])

        texto_boton = "Siguiente pregunta"
        if p == len(unidad["questions"]) - 1 and u < len(BANCO) - 1:
            texto_boton = "Continuar con la siguiente unidad"
        elif u == len(BANCO) - 1 and p == len(unidad["questions"]) - 1:
            texto_boton = "Ver resultado final"

        if st.button(texto_boton, type="primary", use_container_width=True):
            avanzar()
            st.rerun()

else:
    resultados = pd.DataFrame(st.session_state.resultados)
    aciertos = int(resultados["correcta"].sum())
    porcentaje = round(aciertos / TOTAL * 100)

    st.balloons()
    st.title("Resultado final")
    st.write(f"**Estudiante:** {st.session_state.nombre}")
    st.write(f"**DNI:** {st.session_state.dni}")

    c1, c2 = st.columns(2)
    c1.metric("Puntaje", f"{aciertos}/{TOTAL}")
    c2.metric("Porcentaje", f"{porcentaje}%")

    resumen = (
        resultados.groupby("unidad")["correcta"]
        .agg(["sum", "count"])
        .reset_index()
        .rename(columns={"unidad": "Unidad", "sum": "Correctas", "count": "Total"})
    )
    resumen["Resultado"] = resumen["Correctas"].astype(str) + "/" + resumen["Total"].astype(str)

    st.subheader("Resultado por unidad")
    st.dataframe(
        resumen[["Unidad", "Resultado"]],
        use_container_width=True,
        hide_index=True
    )

    if porcentaje >= 80:
        st.success("Muy buen dominio general. Revisá especialmente las preguntas que respondiste incorrectamente.")
    elif porcentaje >= 60:
        st.warning("Buen punto de partida. Conviene repasar las unidades con menor cantidad de respuestas correctas.")
    else:
        st.warning("Te recomendamos repasar los contenidos antes del examen final y volver a realizar esta evaluación.")

    csv = resumen.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Descargar mi resultado",
        data=csv,
        file_name="resultado_evaluacion_formativa_FUESMEN.csv",
        mime="text/csv",
        use_container_width=True
    )

    if st.button("Volver a intentarlo", type="primary", use_container_width=True):
        reiniciar()
        st.rerun()

st.divider()
st.caption("Evaluación formativa – Curso de Metodología y Aplicación de Radioisótopos | FUESMEN")
