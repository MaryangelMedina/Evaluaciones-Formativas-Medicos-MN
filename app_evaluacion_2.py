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

CALCULOS = [
    {
        "id": "calc_01",
        "titulo": "Fuente puntual de cesio-137: distancia y exposición",
        "consigna": (
            "Una fuente puntual de cesio-137 tiene una actividad de 100 mCi. "
            "La constante de tasa de exposición es 0,32 R·m²/(h·Ci). "
            "¿A qué distancia la tasa será 8 mR/h y cuál será la exposición en 10 horas?"
        ),
        "ecuaciones": [
            r"\dot{X}=\frac{\Gamma\,A}{r^2}",
            r"r=\sqrt{\frac{\Gamma\,A}{\dot{X}}}",
            r"X=\dot{X}\,t",
        ],
        "unidades": [
            "Convertí 100 mCi a Ci para que coincida con la constante Γ.",
            "Convertí 8 mR/h a R/h antes de reemplazar en la ecuación.",
            "Para la exposición acumulada podés volver a trabajar en mR/h y horas.",
        ],
        "campos": [
            ("actividad_ci", "Actividad convertida a Ci", "Ci"),
            ("tasa_r_h", "Tasa convertida a R/h", "R/h"),
            ("distancia_m", "Distancia calculada", "m"),
            ("exposicion_mr", "Exposición acumulada en 10 h", "mR"),
        ],
    },
    {
        "id": "calc_02",
        "titulo": "Kerma en agua",
        "consigna": (
            "Un haz de fotones de 1 MeV actúa durante 10 s. La tasa de fluencia "
            "de energía es 0,02 J/(cm²·s) y μtr/ρ = 0,0311 cm²/g. Calculá el kerma en cGy."
        ),
        "ecuaciones": [
            r"\Psi=\dot{\Psi}\,t",
            r"K=\Psi\left(\frac{\mu_{tr}}{\rho}\right)",
        ],
        "unidades": [
            "Al multiplicar J/cm² por cm²/g, el resultado queda en J/g.",
            "Recordá que 1 J/g = 1000 J/kg = 1000 Gy.",
            "Para expresar el resultado en cGy, usá 1 Gy = 100 cGy.",
        ],
        "campos": [
            ("fluencia_energia", "Fluencia de energía en 10 s", "J/cm²"),
            ("kerma_j_g", "Kerma antes de convertir", "J/g"),
            ("kerma_gy", "Kerma", "Gy"),
            ("kerma_cgy", "Kerma", "cGy"),
        ],
    },
    {
        "id": "calc_03",
        "titulo": "Dosis equivalente por radiación gamma y beta",
        "consigna": (
            "Un tejido recibe por separado 3 mGy de radiación gamma y 1 mGy de "
            "radiación beta. Para ambas radiaciones, wR = 1. Calculá la dosis "
            "equivalente aportada por cada radiación y la dosis equivalente total."
        ),
        "ecuaciones": [
            r"H_T=\sum_R w_R\,D_{T,R}",
            r"H_T=w_{R,\gamma}D_{T,\gamma}+w_{R,\beta}D_{T,\beta}",
        ],
        "unidades": [
            "Usá wR = 1 para radiación gamma y wR = 1 para radiación beta.",
            "La dosis absorbida se ingresa siempre en mGy.",
            "La dosis equivalente se obtiene y se informa siempre en mSv.",
            "Como ambos factores valen 1, cada valor numérico en mGy coincide con su aporte en mSv.",
        ],
        "campos": [
            ("d_gamma_mgy", "Dosis absorbida por gamma", "mGy"),
            ("d_beta_mgy", "Dosis absorbida por beta", "mGy"),
            ("h_gamma_msv", "Dosis equivalente por gamma", "mSv"),
            ("h_beta_msv", "Dosis equivalente por beta", "mSv"),
            ("h_total_msv", "Dosis equivalente total en el tejido", "mSv"),
        ],
    },
    {
        "id": "calc_04",
        "titulo": "Dosis efectiva en una exposición uniforme de cuerpo entero",
        "consigna": (
            "Una persona recibe una dosis absorbida uniforme de 20 mGy de "
            "radiación gamma en todo el cuerpo. Para radiación gamma wR = 1. "
            "Calculá primero la dosis equivalente y luego la dosis efectiva total."
        ),
        "ecuaciones": [
            r"H_T=w_R\,D_T",
            r"E=\sum_T w_T\,H_T",
            r"\sum_T w_T=1\quad\Rightarrow\quad E=H_T",
        ],
        "unidades": [
            "La dosis absorbida se ingresa siempre en mGy.",
            "La dosis equivalente y la dosis efectiva se informan siempre en mSv.",
            "En una exposición uniforme de todo el cuerpo, la suma de los factores tisulares es 1.",
        ],
        "campos": [
            ("dosis_absorbida_mgy", "Dosis absorbida por radiación gamma", "mGy"),
            ("dosis_equivalente_msv", "Dosis equivalente", "mSv"),
            ("suma_factores_tisulares", "Suma de los factores de ponderación tisular", "sin unidad"),
            ("dosis_efectiva_msv", "Dosis efectiva total", "mSv"),
        ],
    },
]


def inicializar_estado():
    valores = {
        "iniciado": False,
        "etapa": "calculos",
        "calculo_actual": 0,
        "calculos_resultados": [],
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


def comprobar_calculo(id_ejercicio, valores):
    return enviar_a_google(
        {
            "evaluacion_id": EVALUACION_ID,
            "accion": "comprobar_calculo",
            "id_ejercicio": id_ejercicio,
            "valores": valores,
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
        "calculos": [
            {
                "id_ejercicio": fila["id_ejercicio"],
                "valores": fila["valores"],
            }
            for fila in st.session_state.calculos_resultados
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
    st.session_state.etapa = "calculos"
    st.session_state.calculo_actual = 0
    st.session_state.calculos_resultados = []
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

        - Primero completarás 4 ejercicios guiados: dos de dosimetría y dos de dosis equivalente/efectiva.
        - Después responderás 30 preguntas: 10 por unidad.
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
            st.session_state.etapa = "calculos"
            st.session_state.iniciado = True
            st.rerun()

elif st.session_state.etapa == "calculos":
    indice = st.session_state.calculo_actual

    if indice >= len(CALCULOS):
        st.session_state.etapa = "preguntas"
        st.rerun()

    ejercicio = CALCULOS[indice]
    st.progress(indice / (len(CALCULOS) + TOTAL))
    st.caption(f"Ejercicio guiado {indice + 1} de {len(CALCULOS)}")
    st.header("Unidad 6 – Taller guiado de dosimetría")
    st.subheader(ejercicio["titulo"])
    st.write(ejercicio["consigna"])
    st.warning(
        "⚠️ Antes de reemplazar los datos, verificá que todas las unidades sean compatibles."
    )
    st.markdown("#### 1. Ecuación general y manipulación")
    for ecuacion in ejercicio["ecuaciones"]:
        st.latex(ecuacion)

    st.markdown("#### 2. Preparación de las unidades")
    for indicacion in ejercicio["unidades"]:
        st.markdown(f"- {indicacion}")

    resultado_previo = next(
        (
            fila
            for fila in st.session_state.calculos_resultados
            if fila["id_ejercicio"] == ejercicio["id"]
        ),
        None,
    )

    if resultado_previo is None:
        with st.form(f"form_{ejercicio['id']}"):
            st.markdown("#### 3. Reemplazá los datos y completá la planilla")
            valores = {}
            for clave, etiqueta, unidad_medida in ejercicio["campos"]:
                valores[clave] = st.number_input(
                    f"{etiqueta} ({unidad_medida})",
                    value=None,
                    format="%.6g",
                    key=f"{ejercicio['id']}_{clave}",
                )
            enviado = st.form_submit_button(
                "Comprobar ejercicio", type="primary", use_container_width=True
            )

        if enviado:
            if any(valor is None for valor in valores.values()):
                st.warning("Completá todos los casilleros antes de comprobar.")
            else:
                datos, error = comprobar_calculo(ejercicio["id"], valores)
                if not datos:
                    st.error(error)
                else:
                    st.session_state.calculos_resultados.append(
                        {
                            "id_ejercicio": ejercicio["id"],
                            "titulo": ejercicio["titulo"],
                            "valores": valores,
                            "todo_correcto": bool(datos["todo_correcto"]),
                            "pasos": datos["pasos"],
                            "desarrollo": datos["desarrollo"],
                        }
                    )
                    st.rerun()
    else:
        if resultado_previo["todo_correcto"]:
            st.success("✅ Todos los pasos están correctos.")
        else:
            st.warning("Revisá los pasos señalados. Esta corrección forma parte del aprendizaje.")

        tabla_pasos = pd.DataFrame(resultado_previo["pasos"])
        tabla_pasos["Estado"] = tabla_pasos["correcto"].map(
            {True: "✅ Correcto", False: "⚠️ Revisar"}
        )
        tabla_pasos = tabla_pasos.rename(
            columns={
                "etiqueta": "Paso",
                "valor_ingresado": "Tu resultado",
                "valor_esperado": "Resultado esperado",
                "unidad": "Unidad",
            }
        )
        st.dataframe(
            tabla_pasos[["Paso", "Tu resultado", "Resultado esperado", "Unidad", "Estado"]],
            use_container_width=True,
            hide_index=True,
        )
        st.markdown("#### Desarrollo guiado")
        st.info(resultado_previo["desarrollo"])

        texto = "Siguiente ejercicio"
        if indice == len(CALCULOS) - 1:
            texto = "Continuar con las preguntas"

        if st.button(texto, type="primary", use_container_width=True):
            st.session_state.calculo_actual += 1
            if st.session_state.calculo_actual >= len(CALCULOS):
                st.session_state.etapa = "preguntas"
            st.rerun()

elif st.session_state.unidad < len(BANCO):
    u = st.session_state.unidad
    p = st.session_state.pregunta
    unidad = BANCO[u]
    pregunta = unidad["questions"][p]

    respondidas = len(st.session_state.resultados)
    st.progress((len(CALCULOS) + respondidas) / (len(CALCULOS) + TOTAL))
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

    calculos_correctos = sum(
        1 for fila in st.session_state.calculos_resultados if fila["todo_correcto"]
    )
    st.subheader("Taller guiado de cálculo")
    st.write(
        f"**Ejercicios resueltos completamente en el primer intento:** "
        f"{calculos_correctos}/{len(CALCULOS)}"
    )
    st.caption(
        "Los ejercicios son formativos: la planilla muestra los pasos esperados "
        "para que puedas revisar el procedimiento."
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
