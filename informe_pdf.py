from flask import Blueprint, send_file, jsonify
from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape
import MallaCurricular as m
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

informe_bp = Blueprint('informe_pdf', __name__)
AZUL = colors.HexColor('#16365D')
VERDE = colors.HexColor('#DDF4E9')
ROJO = colors.HexColor('#FBE4E7')
CELESTE = colors.HexColor('#E5F0FF')

def numero(valor):
    try:
        return int(valor or 0)
    except (TypeError, ValueError):
        return 0

def texto(valor):
    return escape(str(valor if valor is not None else ''))

def pagina(canvas, doc):
    canvas.saveState()
    ancho, alto = A4
    canvas.setStrokeColor(colors.HexColor('#D5DCE6'))
    canvas.line(1.7*cm, 1.45*cm, ancho-1.7*cm, 1.45*cm)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#65758B'))
    canvas.drawString(1.7*cm, 1.1*cm, 'Ruta Academica | Informe de estado de materias')
    canvas.drawRightString(ancho-1.7*cm, 1.1*cm, f'Pagina {doc.page}')
    canvas.restoreState()

@informe_bp.get('/api/informe/pdf')
def descargar_informe_pdf():
    plan = m.carrera_actual() if m.planes else None
    if not plan:
        return jsonify(error='No hay una carrera activa'), 404

    materias = m.materias(plan)
    estados = [(materia, m.estado(materia)) for materia in materias]
    total = len(estados)
    aprobadas = sum(estado == 'APROBADA' for _, estado in estados)
    disponibles = sum(estado == 'DISPONIBLE' for _, estado in estados)
    bloqueadas = sum(estado == 'BLOQUEADA' for _, estado in estados)
    creditos = sum(numero(mat.get('creditos')) for mat, _ in estados)
    creditos_ok = sum(numero(mat.get('creditos')) for mat, est in estados if est == 'APROBADA')
    avance = 100 * aprobadas / total if total else 0

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='TituloRuta', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=19, leading=24, textColor=AZUL, spaceAfter=12))
    styles.add(ParagraphStyle(name='SubRuta', parent=styles['Heading2'], fontSize=12, leading=16, textColor=AZUL, spaceBefore=15, spaceAfter=8))
    styles.add(ParagraphStyle(name='CeldaRuta', fontName='Helvetica', fontSize=8, leading=11))
    styles.add(ParagraphStyle(name='CabRuta', fontName='Helvetica-Bold', fontSize=8, leading=11, textColor=colors.white))
    styles.add(ParagraphStyle(name='InfoRuta', fontName='Helvetica', fontSize=9, leading=14, spaceAfter=7))
    p = lambda valor, estilo='CeldaRuta': Paragraph(texto(valor), styles[estilo])

    contenido = [Paragraph('Informe de estado academico', styles['TituloRuta']),
                 p(plan.get('nombre', 'Carrera sin nombre'), 'InfoRuta'),
                 p('Generado: ' + datetime.now().strftime('%d/%m/%Y %H:%M'), 'InfoRuta'),
                 Spacer(1, 9)]
    resumen = [
        ['Materias totales', str(total), 'Aprobadas', str(aprobadas)],
        ['Disponibles', str(disponibles), 'Bloqueadas', str(bloqueadas)],
        ['Avance', f'{avance:.1f} %', 'Creditos', f'{creditos_ok} / {creditos}']
    ]
    tabla = Table([[p(x) for x in fila] for fila in resumen], colWidths=[3.8*cm, 3.1*cm, 3.8*cm, 3.1*cm])
    tabla.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#F0F4F9')),
                               ('BOX',(0,0),(-1,-1),0.5,colors.HexColor('#D5DFEC')),
                               ('INNERGRID',(0,0),(-1,-1),0.35,colors.HexColor('#D5DFEC')),
                               ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                               ('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9)]))
    contenido.extend([tabla, Spacer(1, 10), Paragraph('Detalle por semestre', styles['SubRuta'])])

    for indice, semestre in enumerate(plan.get('semestres', []), start=1):
        filas = [[p('Codigo','CabRuta'), p('Asignatura','CabRuta'), p('Estado','CabRuta'), p('Requisitos pendientes','CabRuta')]]
        for mat in [x for x in materias if numero(x.get('semestre')) == indice]:
            codigo = mat.get('codigo','')
            nombre = mat.get('nombre','')
            estado = m.estado(mat)
            pendientes = m.pendientes(mat)
            nombres = []
            for cod in pendientes:
                ref = m.buscar(cod)
                nombres.append((ref or {}).get('nombre', cod))
            filas.append([p(codigo), p(nombre), p(estado), p(', '.join(nombres) if nombres else 'Ninguno')])
        if len(filas) == 1:
            continue
        tabla = Table(filas, colWidths=[2.2*cm, 5.2*cm, 2.5*cm, 4.9*cm], repeatRows=1, hAlign='LEFT')
        estilos = [('BACKGROUND',(0,0),(-1,0),AZUL),('VALIGN',(0,0),(-1,-1),'TOP'),
                   ('LINEBELOW',(0,0),(-1,-1),0.3,colors.HexColor('#D7DFE8')),
                   ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
                   ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]
        for i, mat in enumerate([x for x in materias if numero(x.get('semestre')) == indice], start=1):
            estado = m.estado(mat)
            fondo = VERDE if estado == 'APROBADA' else ROJO if estado == 'BLOQUEADA' else CELESTE
            estilos.append(('BACKGROUND',(2,i),(2,i),fondo))
        tabla.setStyle(TableStyle(estilos))
        contenido.append(Paragraph(f'Semestre {indice}', styles['SubRuta']))
        contenido.append(tabla)

    contenido.append(Spacer(1, 12))
    contenido.append(p('Estados calculados al momento de generar el informe. Los requisitos pendientes se obtienen del plan de estudios activo.', 'InfoRuta'))
    salida = BytesIO()
    doc = SimpleDocTemplate(salida, pagesize=A4, rightMargin=1.7*cm, leftMargin=1.7*cm,
                            topMargin=1.8*cm, bottomMargin=1.9*cm,
                            title='Informe de estado academico')
    doc.build(contenido, onFirstPage=pagina, onLaterPages=pagina)
    salida.seek(0)
    nombre = 'informe_estado_academico_' + datetime.now().strftime('%Y%m%d_%H%M') + '.pdf'
    return send_file(salida, mimetype='application/pdf', as_attachment=True, download_name=nombre)
