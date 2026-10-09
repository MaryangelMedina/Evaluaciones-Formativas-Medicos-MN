"""Examen: sólo preguntas públicas; evaluación y registro en Apps Script."""
import csv
import hashlib
import io
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
import streamlit as st

BASE = Path(__file__).resolve().parent
EVALUACION_ID = 'integrador_9_10_11_2026'
SCHEMA = 'fuesmen.integrador.v1'
st.set_page_config(page_title='FUESMEN | Examen integrador 2026', page_icon='☢️', layout='centered')

@st.cache_data
def cargar_banco():
    units = json.loads((BASE / 'questions.json').read_text(encoding='utf-8'))
    flat = [dict(q, unidad=u['numero_unidad'], unit=u['unit']) for u in units for q in u['questions']]
    if len(flat) != 60 or len({q['id'] for q in flat}) != 60:
        raise ValueError('Banco inválido')
    return units, flat

UNITS, QUESTIONS = cargar_banco()
CATALOG = [{'id':q['id'], 'unidad':q['unidad'], 'pregunta':q['q'], 'opciones':q['opts']} for q in QUESTIONS]
CATALOG_HASH = hashlib.sha256(json.dumps(CATALOG, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()

def enviar(payload):
    try:
        url = str(st.secrets['RESULTS_WEBHOOK_URL'])
        token = str(st.secrets['RESULTS_WEBHOOK_TOKEN'])
        if not url.startswith('https://script.google.com/macros/s/') or not url.endswith('/exec'):
            return None, 'La dirección de registro no tiene el formato esperado.'
        # Solicitud sólo desde el servidor; el token jamás se renderiza.
        response = requests.post(url, json=dict(payload, token=token), timeout=(5, 25))
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict) or data.get('ok') is not True:
            return None, 'El registro rechazó la solicitud. Contactá al docente.'
        return data, ''
    except Exception:
        logging.warning('Falló la comunicación con el registro; detalles omitidos para proteger la configuración.')
        return None, 'No se pudo contactar al registro. Podés reintentar; no se confirmó el envío.'

def verificar():
    data, error = enviar({'accion':'verificar_esquema', 'evaluacion_id':EVALUACION_ID, 'schema':SCHEMA, 'catalogo_hash':CATALOG_HASH})
    if not data:
        return False, error
    if data.get('schema') != SCHEMA or data.get('evaluacion_id') != EVALUACION_ID or data.get('catalogo_hash') != CATALOG_HASH or data.get('total_preguntas') != 60:
        return False, 'El registro no es compatible con este examen. El docente debe revisar su configuración.'
    return True, ''

def validar_resumen(data):
    if data.get('schema') != SCHEMA or data.get('evaluacion_id') != EVALUACION_ID or data.get('intento_id') != st.session_state.intento_id:
        raise ValueError('Identificación incompatible')
    if data.get('registrado') is not True or data.get('total_preguntas') != 60:
        raise ValueError('Registro no confirmado')
    total = data.get('total_correctas')
    if type(total) is not int or not 0 <= total <= 60:
        raise ValueError('Puntaje inválido')
    if type(data.get('porcentaje')) not in (int, float) or abs(data['porcentaje'] - round(total / 60 * 100, 1)) > .01:
        raise ValueError('Porcentaje inconsistente')
    rows = data.get('por_unidad', [])
    if len(rows) != 3 or {r.get('unidad') for r in rows} != {9, 10, 11}:
        raise ValueError('Unidades inválidas')
    for r in rows:
        if r.get('total') != 20 or type(r.get('correctas')) is not int or not 0 <= r['correctas'] <= 20:
            raise ValueError('Resumen inconsistente')
    if sum(r['correctas'] for r in rows) != total:
        raise ValueError('Suma inconsistente')
    return data

def guardar():
    payload = {'accion':'guardar', 'evaluacion_id':EVALUACION_ID, 'schema':SCHEMA,
               'catalogo_hash':CATALOG_HASH, 'intento_id':st.session_state.intento_id,
               'fecha_hora_cliente':datetime.now(ZoneInfo('America/Argentina/Mendoza')).isoformat(timespec='seconds'),
               'nombre':st.session_state.nombre, 'dni':st.session_state.dni,
               'respuestas':[{'id_pregunta':q['id'], 'seleccion':st.session_state.answers[q['id']]} for q in QUESTIONS], 'calculos':[]}
    data, error = enviar(payload)
    if data:
        try:
            st.session_state.resumen = validar_resumen(data)
            st.session_state.error = ''
        except (ValueError, TypeError, KeyError):
            st.session_state.error = 'El registro devolvió un resumen incompatible; solicitá revisión al docente antes de volver a enviar.'
    else:
        st.session_state.error = error

defaults = dict(iniciado=False, pos=0, answers={}, nombre='', dni='', intento_id='', terminado=False, resumen=None, error='')
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.title('Examen integrador 2026')
st.subheader('Curso de Metodología de Radioisótopos')
st.caption('Fundación Escuela de Medicina Nuclear — FUESMEN')

if not st.session_state.iniciado:
    st.write('Unidades 9, 10 y 11. Son 60 preguntas: 20 por unidad. Cada respuesta correcta vale un punto. El resultado se expresa también sobre 100.')
    st.write('Podés navegar y revisar tus respuestas antes de finalizar. La entrega queda cerrada al enviarla. Las soluciones no se muestran durante el examen.')
    st.caption('Tu nombre, DNI y respuestas se registrarán para la evaluación del curso. Una recarga completa o cierre de sesión puede perder el avance antes de la entrega.')
    with st.form('identificacion'):
        nombre = st.text_input('Apellido y nombre', max_chars=150)
        dni = st.text_input('DNI', max_chars=12)
        start = st.form_submit_button('Comenzar evaluación', type='primary')
    if start:
        if len(nombre.strip()) < 3 or not dni.strip().isascii() or not dni.strip().isdigit() or not 6 <= len(dni.strip()) <= 12:
            st.warning('Ingresá apellido y nombre y un DNI válido, sólo con números.')
        else:
            compatible, error = verificar()
            if not compatible:
                st.error(error)
            else:
                st.session_state.update(iniciado=True, nombre=nombre.strip(), dni=dni.strip(), intento_id=str(uuid.uuid4()))
                st.rerun()
elif not st.session_state.terminado:
    q = QUESTIONS[st.session_state.pos]
    st.progress(len(st.session_state.answers) / 60)
    st.caption(f"Pregunta {st.session_state.pos + 1} de 60 · Respondidas: {len(st.session_state.answers)}")
    st.header(q['unit'])
    st.write(q['q'])
    if q.get('image'):
        st.image(str(BASE / q['image']), caption='Figura de la presentación de clase, adaptada por recorte.')
    with st.form('pregunta_' + q['id']):
        selected = st.radio('Elegí una opción:', q['opts'], index=st.session_state.answers.get(q['id']))
        submitted = st.form_submit_button('Guardar respuesta', type='primary')
    if submitted:
        if selected is None:
            st.warning('Seleccioná una opción.')
        else:
            st.session_state.answers[q['id']] = q['opts'].index(selected)
            st.rerun()
    if q['id'] in st.session_state.answers:
        st.success('Respuesta guardada para este intento.')
    left, right = st.columns(2)
    if left.button('Anterior', disabled=st.session_state.pos == 0):
        st.session_state.pos -= 1
        st.rerun()
    if right.button('Siguiente', disabled=st.session_state.pos == 59):
        st.session_state.pos += 1
        st.rerun()
    labels = [f"{i+1}. Unidad {item['unidad']}" + (' · respondida' if item['id'] in st.session_state.answers else '') for i,item in enumerate(QUESTIONS)]
    destination = st.selectbox('Ir a otra pregunta', range(60), index=st.session_state.pos,
                               format_func=lambda i, labels=labels: labels[i])
    if st.button('Ir'):
        st.session_state.pos = destination
        st.rerun()
    st.caption('Guardá la opción seleccionada antes de navegar. Podés modificar respuestas hasta la entrega.')
    if len(st.session_state.answers) == 60:
        confirm = st.checkbox('Revisé mis respuestas y deseo entregar el examen.')
        if st.button('Finalizar y registrar', type='primary', disabled=not confirm):
            st.session_state.terminado = True
            guardar()
            st.rerun()
    else:
        st.caption(f"Faltan {60-len(st.session_state.answers)} respuestas para habilitar la entrega.")
else:
    st.header('Resultado final')
    st.write(f"Estudiante: {st.session_state.nombre}")
    if st.session_state.resumen:
        data = st.session_state.resumen
        a,b = st.columns(2)
        a.metric('Puntaje', f"{data['total_correctas']}/60")
        b.metric('Resultado sobre 100', f"{data['porcentaje']:.1f}")
        rows = [{'Unidad':r['unidad'],'Correctas':r['correctas'],'Total':r['total']} for r in data['por_unidad']]
        st.table(rows)
        st.success('Entrega registrada correctamente.')
        buffer=io.StringIO(); writer=csv.DictWriter(buffer,fieldnames=['Unidad','Correctas','Total']);writer.writeheader();writer.writerows(rows)
        st.download_button('Descargar mi resultado',buffer.getvalue().encode('utf-8-sig'),'resultado_integrador_FUESMEN_2026.csv','text/csv')
        st.caption(f"Identificador del intento: {st.session_state.intento_id}")
    else:
        st.warning('El registro de la entrega todavía no está confirmado. Conservá esta sesión abierta.')
        st.error(st.session_state.error)
        if st.button('Reintentar el registro'):
            guardar()
            st.rerun()
st.divider()
st.caption('Curso de Metodología de Radioisótopos 2026 · Unidades 9, 10 y 11 · FUESMEN')
