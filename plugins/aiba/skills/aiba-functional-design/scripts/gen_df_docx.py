#!/usr/bin/env python3
"""aiba-functional-design · gen_df_docx.py — Documento de Diseno Funcional (DF).

Renderiza un manifiesto JSON a un `.docx` con la estructura acordada. Existe un
unico generador a proposito: el valor del skill es que todos los DF de un
proyecto salgan iguales, y eso no se sostiene si cada invocacion arma el
documento a su manera.

El diseno es **generico**: estilos nativos de Word (Titulo 1/2/3, un estilo de
tabla con nombre, cabecera y pie), sin logotipos ni colores corporativos salvo
que el manifiesto traiga una seccion `branding`. Asi, aplicar despues una
identidad visual es cambiar los estilos, no repasar el documento parrafo a
parrafo.

Uso:
    python3 gen_df_docx.py --manifest df.json --output "docs/df/HU-01 - ....docx"
    python3 gen_df_docx.py --schema          # imprime el esquema del manifiesto

Solo depende de `python-docx`, que instala sobre la marcha si falta (misma
estrategia que `gen_hu_plan_xlsx.py`: la invocacion de python es la puerta de
permisos y el pip hereda esa aprobacion). Se puede desactivar con `--no-install`
o la variable de entorno `AIBA_DF_NO_INSTALL`.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import unicodedata
import subprocess
import sys
from datetime import date
from pathlib import Path

# La marca vive a nivel de plugin: la comparten este skill y `aiba-test-plan`.
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

import branding as marca  # noqa: E402 - despues de fijar sys.path

# --- Dependencia -------------------------------------------------------------

def _ensure_docx(allow_install: bool) -> None:
    """Importa python-docx, instalandolo al vuelo si falta."""
    try:
        import docx  # noqa: F401
        return
    except ImportError:
        pass

    if not allow_install or os.environ.get("AIBA_DF_NO_INSTALL"):
        sys.stderr.write(
            "Falta 'python-docx' y la instalacion automatica esta desactivada.\n"
            "Instalalo con:  pip install python-docx\n"
        )
        sys.exit(2)

    sys.stderr.write("Aviso: 'python-docx' no esta instalado; instalandolo automaticamente...\n")
    for cmd in (
        [sys.executable, "-m", "pip", "install", "--quiet", "python-docx"],
        [sys.executable, "-m", "pip", "install", "--quiet", "--user", "python-docx"],
    ):
        try:
            subprocess.check_call(cmd)
        except Exception:  # noqa: BLE001 - se prueba la siguiente estrategia
            continue
        try:
            import docx  # noqa: F401
            sys.stderr.write("OK: 'python-docx' instalado correctamente.\n")
            return
        except ImportError:
            continue
    sys.stderr.write("No se pudo instalar 'python-docx'. Instalalo a mano y reintenta.\n")
    sys.exit(2)


SCHEMA = """\
Esquema del manifiesto (JSON). Todo lo que falte se omite o sale como pendiente.

Los `[PENDIENTE: ...]` que escribas en cualquier campo de texto salen resaltados
en amarillo, tambien dentro de las tablas. Escribelos literales y entre
corchetes: parafrasearlos ("falta por definir") pierde el resaltado.

{
  "proyecto":  "SUPLEMENTOS",             # nombre corto; va en portada y cabecera
  "hu_id":     "HU-03",
  "titulo":    "Busqueda de Poliza",
  "version":   "1.0",
  "autor":     "Nombre Apellido",         # la persona que firma; nunca el skill
  "fecha":     "2026-08-27",              # opcional; por defecto, hoy

  "control_versiones":   [{"fecha": "...", "version": "1.0",
                           "autor": "...", "cambio": "Version inicial"}],
  "control_aprobaciones":[{"responsable": "", "cargo": "",
                           "departamento": "", "fecha": "", "version": ""}],

  "introduccion": "parrafo o lista de parrafos",
  "alcance":      "parrafo o lista de parrafos",

  "narrativa": {"como": "...", "quiero": "...", "para": "..."},

  "campos": {                              # tabla Filtros/Campos
    "columnas": ["Nombre","Editable","Oblig","Tipo","Comentario"],
    "filas": [["Ramo","Si","Si","Lista desplegable","..."]]
  },
  "integraciones": "texto o lista",
  "validaciones": {"frontal": "texto o lista", "core": "texto o lista"},
  "mensajes":     {"frontal": "...", "integracion_no_core": "...", "core": "..."},
  "pantallas":    "texto o lista",
  "imagenes":     ["docs/prototipos/hu-03.png"],

  "criterios_aceptacion": {"contexto": "...", "escenarios": ["Escenario X: ..."]},
  "especificaciones_tecnicas": "texto o lista",
  "puntos_abiertos": [{"id":"PA-01","descripcion":"...","estado":"Abierto",
                       "responsable":"","estimada":"","resolucion":""}],

  "secciones_adicionales": [{"titulo":"Glosario","contenido":"texto o lista"}],

  # Con --plantilla, la cabecera y el pie de la plantilla se respetan tal cual
  # (logo incluido) y `texto_cabecera` / `texto_pie` no se aplican.
  "branding": {                            # opcional; sin el, documento neutro
    "color_principal":  "1F3864",
    "color_secundario": "2E74B5",
    "logo":             "ruta/al/logo.png",
    "texto_cabecera":   "...",
    "texto_pie":        "..."
  }
}
"""

# El SKILL.md evita tildes por compatibilidad entre plataformas de agentes, pero
# el DOCUMENTO GENERADO lo lee y lo firma un cliente: ahi el espanol va con sus
# tildes. La regla aplica al contenido de salida, no al codigo ni a las instrucciones.
PENDIENTE = "[PENDIENTE: sin información en la documentación de origen]"

# Lo que tiene que completar una persona sale **resaltado en amarillo**. Un DF
# de veinte paginas se lee en diagonal, y un `[PENDIENTE]` en texto normal pasa
# desapercibido: acaba firmado como si fuera contenido. El resaltado es la
# unica forma de que un hueco se vea sin leer el documento entero.
# El marcador entre corchetes sigue siendo la forma correcta de escribirlo, pero
# **no puede ser la unica que se resalte**: segun el modelo que redacte, el hueco
# sale como "pendiente de definir" o "falta por confirmar con negocio", y con la
# marca literal como unico criterio esos huecos se entregaban sin resaltar. Se
# reconocen tambien las formas en prosa, que es lo que hace que el resultado no
# dependa de que modelo genero el documento.
MARCA_PENDIENTE = re.compile(
    r"\[(?:PENDIENTE|Imagen no encontrada|No se pudo insertar)[^\]]*\]"
    r"|\bpendientes? de (?:definir|concretar|confirmar|validar|detallar|decidir"
    r"|aportar|recibir|documentar)\b"
    # `a definir` se cae a proposito: "vamos a definir el alcance" no es un hueco.
    r"|\b(?:por|sin) (?:definir|concretar|confirmar|determinar|detallar|decidir)\b"
    r"|\bfalta(?:n)? por (?:definir|concretar|confirmar|detallar|decidir)\b"
    r"|\bse desconoce\b|\bno se dispone de\b|\bno consta\b",
    re.IGNORECASE)

# Lo que se escribe en una celda que alguien tiene que rellenar a mano. Va entre
# corchetes para que lo pille la marca de arriba y salga en amarillo.
CELDA_PENDIENTE = "[PENDIENTE]"

# Codigos internos que no pintan nada en un DF: quien lo revisa no tiene esos
# documentos y el codigo no le dice nada. `HU-` y `PA-` se quedan --dan nombre
# al fichero y a los puntos abiertos--. Ver la regla "Sin codigos internos".
CODIGO_INTERNO = re.compile(
    r"\b(?:RF|RNF|NFR|GAP|RN|REQ|US|EPIC|HIST)-\s?\d+", re.IGNORECASE)

# Nombres que delatan que el "autor" es la herramienta y no una persona. Del
# control de versiones responde alguien ante el cliente, y ningun skill
# responde de nada.
NO_ES_AUTOR = re.compile(
    r"aiba|aidd|aisdd|claude|gpt|copilot|assistant|gen_df|\bskills?\b|\bagente\b|\bia\b",
    re.IGNORECASE)


def autor_persona(valor) -> tuple[str, str | None]:
    """El autor, o vacio y un aviso si lo que llega es el nombre del generador."""
    v = str(valor or "").strip()
    if not v:
        return "", None
    if NO_ES_AUTOR.search(v):
        return "", (f"el autor '{v}' parece la herramienta y no una persona; se deja "
                    "vacio para que lo rellene el analista que firma el documento")
    return v, None


def codigos_internos(valor, ruta: str = "") -> list[str]:
    """Donde han quedado codigos internos en el contenido, con su ubicacion.

    No bloquea la generacion a proposito: cortar un lote de veinte HU por una
    sigla deja al analista sin los otros diecinueve documentos. Lo que hace es
    decir exactamente donde estan, para que la correccion sea de un minuto.
    """
    fuera: list[str] = []
    if isinstance(valor, dict):
        for k, v in valor.items():
            if k in ("branding", "imagenes", "hu_id"):
                continue
            fuera.extend(codigos_internos(v, f"{ruta}.{k}" if ruta else str(k)))
    elif isinstance(valor, (list, tuple)):
        for n, v in enumerate(valor):
            fuera.extend(codigos_internos(v, f"{ruta}[{n}]"))
    elif isinstance(valor, str):
        for c in dict.fromkeys(m.group(0) for m in CODIGO_INTERNO.finditer(valor)):
            fuera.append(f"{ruta or 'raiz'}: {c}")
    return fuera


def escribir_marcado(p, texto: str) -> None:
    """Escribe el texto en el parrafo, resaltando en amarillo sus marcas."""
    from docx.enum.text import WD_COLOR_INDEX

    pos = 0
    for m in MARCA_PENDIENTE.finditer(texto):
        if m.start() > pos:
            p.add_run(texto[pos:m.start()])
        p.add_run(m.group(0)).font.highlight_color = WD_COLOR_INDEX.YELLOW
        pos = m.end()
    if pos < len(texto):
        p.add_run(texto[pos:])


def parrafo_marcado(doc, texto: str, style=None):
    p = doc.add_paragraph(style=style) if style else doc.add_paragraph()
    escribir_marcado(p, texto)
    return p



# --- Utilidades de contenido -------------------------------------------------

def as_blocks(value) -> list[str]:
    """Normaliza texto suelto o lista a una lista de parrafos no vacios."""
    if value is None:
        return []
    if isinstance(value, str):
        return [b.strip() for b in value.split("\n") if b.strip()]
    if isinstance(value, (list, tuple)):
        out: list[str] = []
        for v in value:
            out.extend(as_blocks(v))
        return out
    return [str(value)]


def write_blocks(doc, value, vacio: str = PENDIENTE, est=None) -> None:
    """Escribe parrafos; las lineas que empiecen por '- ' salen como vinetas."""
    blocks = as_blocks(value)
    if not blocks:
        parrafo_marcado(doc, vacio)
        return
    for b in blocks:
        if b.startswith(("- ", "* ", "\u2022 ")):
            texto = b[1:].strip() if b[0] == "\u2022" else b[2:].strip()
            if est is not None:
                est.vineta(doc, texto)
            else:
                parrafo_marcado(doc, texto, "List Bullet")
        else:
            parrafo_marcado(doc, b)


def add_table(doc, columnas: list[str], filas: list[list[str]], accent: str | None) -> None:
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    t = doc.add_table(rows=1, cols=len(columnas))
    t.style = "Table Grid"
    for i, c in enumerate(columnas):
        celda = t.rows[0].cells[i]
        celda.text = ""
        run = celda.paragraphs[0].add_run(str(c))
        run.bold = True
        celda.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        if accent:
            marca.sombrear_celda_word(celda, accent)
    for fila in filas or []:
        celdas = t.add_row().cells
        for i, v in enumerate(fila[: len(columnas)]):
            # Por las celdas pasan tambien los `[PENDIENTE]`: un hueco dentro de
            # una tabla es tan hueco como uno en un parrafo.
            escribir_marcado(celdas[i].paragraphs[0], "" if v is None else str(v))
    doc.add_paragraph()


def add_toc(doc) -> None:
    """Indice como campo TOC, montado **igual que lo monta Word**.

    Word lo envuelve en un `w:sdt` de galeria "Table of Contents" y, sobre todo,
    reparte el campo entre varios parrafos: el `begin` en el primero del
    resultado y el `end` en el ultimo. No es decoracion.

    Meter `begin` y `end` en el **mismo** parrafo --que es lo que hacia esto--
    obliga a Word, al actualizar, a convertir un campo de un parrafo en uno de
    treinta, y al reconstruir el rango se lleva por delante las marcas de
    parrafo siguientes: desaparecia el principio de Introduccion y Alcance.
    Repartir los runs no bastaba; lo que importa es que el campo **ya nazca**
    abarcando mas de un parrafo, como el que escribe Word.
    """
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    def elem(tag: str, **attrs):
        e = OxmlElement(tag)
        for k, v in attrs.items():
            e.set(qn(k.replace("__", ":")), v)
        return e

    def run(hijo):
        r = elem("w:r")
        r.append(hijo)
        return r

    sdt = elem("w:sdt")
    pr = elem("w:sdtPr")
    dpo = elem("w:docPartObj")
    dpo.append(elem("w:docPartGallery", w__val="Table of Contents"))
    dpo.append(elem("w:docPartUnique"))
    pr.append(dpo)
    sdt.append(pr)
    contenido = elem("w:sdtContent")
    sdt.append(contenido)

    # Primer parrafo: begin, el codigo del campo, separate y el texto provisional.
    campo = elem("w:p")
    campo.append(run(elem("w:fldChar", w__fldCharType="begin")))
    instr = elem("w:instrText", xml__space="preserve")
    instr.text = r' TOC \o "1-3" \h \z \u '
    campo.append(run(instr))
    campo.append(run(elem("w:fldChar", w__fldCharType="separate")))
    aviso = elem("w:t")
    aviso.text = "Actualiza el índice en Word: clic derecho > Actualizar campos."
    campo.append(run(aviso))
    contenido.append(campo)

    # Y el `end` en **su propio parrafo**: ahi esta el arreglo.
    cierre = elem("w:p")
    cierre.append(run(elem("w:fldChar", w__fldCharType="end")))
    contenido.append(cierre)

    # `add_paragraph` sabe colocarse antes del `sectPr`; el sdt ocupa su sitio.
    ancla = doc.add_paragraph()
    ancla._p.addprevious(sdt)
    ancla._p.getparent().remove(ancla._p)


# Texto de relleno que trae la plantilla del cliente y que nadie ha sustituido.
# No se borra --puede haber un apartado del cliente que haya que rellenar de
# verdad-- pero se resalta y se canta, que es lo que no pasaba: el DF se
# entregaba con el "TITULO DEL DOCUMENTO" de la plantilla todavia puesto.
# Los angulos piden cuidado. `<[^<>]+>` tambien casa con "si el saldo < 0 y el
# plazo > 30" y con `<div>`, y resaltar eso es peor que no resaltar nada. Se
# exige que no haya espacio pegado a los angulos --un hueco se escribe `<FOO>`,
# no `< foo >`-- y que dentro haya espacio, guion bajo o mayusculas, que es lo
# que distingue un hueco de una etiqueta de marcado.
RELLENO = re.compile(
    # `(?-i:...)` mantiene el tramo sensible a mayusculas dentro de un patron que
    # no lo es: sin eso, `IGNORECASE` hace que `[A-Z]{2}` case con "di" y `<div>`
    # se marque como hueco.
    r"<(?=\S)(?=[^<>\n]*(?:[ _]|(?-i:[A-ZÁÉÍÓÚÜÑ]{2})))[^<>\n]{1,58}\S>"
    r"|\{\{[^}\n]{1,60}\}\}"                   # {{campo}}
    r"|lorem ipsum"
    r"|\btexto de (?:ejemplo|muestra|prueba|relleno)\b"
    r"|\bsustituir por\b|\brellenar (?:con|aqui|aquí)\b"
    r"|\bpendiente de (?:completar|rellenar)\b"
    r"|\bT[IÍ]TULO DEL DOCUMENTO\b"
    r"|\bnombre del (?:proyecto|cliente|documento)\b"
    r"|\bXXXX+\b|\bTBD\b",
    re.IGNORECASE)


def _con_contenido(parte) -> bool:
    """Si una cabecera o un pie tienen algo dentro: texto, imagen o campo."""
    from docx.oxml.ns import qn

    el = parte._element
    if any((t.text or "").strip() for t in el.iter(qn("w:t"))):
        return True
    return any(next(el.iter(qn(tag)), None) is not None
               for tag in ("w:drawing", "w:pict", "w:object", "w:fldChar"))


def propagar_cabecera(doc) -> list[str]:
    """Lleva la cabecera de la portada al resto de paginas si estas no tienen.

    Una plantilla con "primera pagina distinta" suele traer el logo **solo** en
    la cabecera de la portada, y el resto del documento sale sin el. Se nota al
    imprimir y es lo que se reporto. Solo se copia cuando la cabecera normal
    esta vacia: si el cliente puso ahi otra cosa, manda la suya.

    Copiar el XML no basta. La imagen se referencia por un identificador de
    relacion que **pertenece a la parte de origen**, asi que hay que registrar
    la imagen tambien en la parte de destino y reescribir el identificador, o
    el logo aparece como un recuadro roto.
    """
    import copy

    from docx.opc.constants import RELATIONSHIP_TYPE as RT
    from docx.oxml.ns import qn

    tocadas: list[str] = []
    for i, sec in enumerate(doc.sections):
        if not sec.different_first_page_header_footer:
            continue
        primera, normal = sec.first_page_header, sec.header
        if not _con_contenido(primera) or _con_contenido(normal):
            continue
        normal.is_linked_to_previous = False
        for hijo in list(normal._element):
            normal._element.remove(hijo)
        for hijo in primera._element:
            copia = copy.deepcopy(hijo)
            # `v:imagedata` es VML, de las plantillas antiguas; python-docx no
            # trae ese prefijo en su mapa de espacios de nombres.
            vml = "{urn:schemas-microsoft-com:vml}imagedata"
            for ref, attr in ((qn("a:blip"), qn("r:embed")), (vml, qn("r:id"))):
                for nodo in copia.iter(ref):
                    rid = nodo.get(attr)
                    if not rid:
                        continue
                    imagen = primera.part.related_parts[rid]
                    nodo.set(attr, normal.part.relate_to(imagen, RT.IMAGE))
            normal._element.append(copia)
        tocadas.append(str(i + 1))
    return tocadas


def poner_titulo(doc, est, titulo: str, proyecto: str) -> bool:
    """Escribe el titulo del DF en la portada de la plantilla.

    En modo esqueleto no se toca nada que no sea un apartado reconocido, y la
    portada no lo es: el DF salia con el titulo de ejemplo de la plantilla.
    Se busca el primer parrafo con estilo de titulo antes del primer apartado.
    """
    # Primero se busca el `Title`; el `Subtitle` solo si no hay ninguno. Al reves
    # se pisaria un subtitulo con sentido --"Documento de Diseño Funcional"--
    # dejando el titulo de ejemplo puesto justo encima.
    for nombre in (est("Title"), est("Subtitle")):
        if nombre is None:
            continue
        if _escribir_en_portada(doc, nombre, titulo, proyecto):
            return True
    return False


def _escribir_en_portada(doc, nombre: str, titulo: str, proyecto: str) -> bool:
    for p in doc.paragraphs:
        if nivel_titulo(p) is not None:
            break                      # ya estamos en el cuerpo del documento
        if p.style is not None and p.style.name == nombre:
            for run in list(p.runs)[1:]:
                run._r.getparent().remove(run._r)
            texto = f"{proyecto} · {titulo}" if proyecto else titulo
            if p.runs:
                p.runs[0].text = texto
            else:
                p.add_run(texto)
            return True
    return False


def marcar_relleno(doc) -> list[str]:
    """Resalta el texto de relleno que quede y dice donde esta.

    No lo borra: un apartado propio del cliente puede tener que rellenarse de
    verdad, y borrarlo dejaria el DF sin ese hueco. Lo pone en amarillo --la
    misma marca que ya se usa para lo que completa una persona-- y lo devuelve
    con el apartado en el que ha quedado, para que el skill lo resuelva antes
    de dar el documento por entregado.
    """
    from docx.enum.text import WD_COLOR_INDEX

    fuera: list[str] = []

    def revisar(p, seccion: str) -> None:
        texto = p.text
        if not texto.strip() or MARCA_PENDIENTE.search(texto):
            return                     # los [PENDIENTE] son nuestros y a proposito
        if not RELLENO.search(texto):
            return
        # Se resalta el parrafo entero y no solo el trozo: partir los runs para
        # pintar un fragmento rompe el formato que traiga la plantilla, y lo que
        # importa es que la frase se vea.
        for run in p.runs:
            run.font.highlight_color = WD_COLOR_INDEX.YELLOW
        fuera.append(f"{seccion}: {texto.strip()[:90]}")

    seccion = "(portada)"
    for p in doc.paragraphs:
        if nivel_titulo(p) is not None:
            seccion = p.text.strip() or seccion
        revisar(p, seccion)
    # Las plantillas meten el relleno tambien dentro de sus tablas.
    for t in doc.tables:
        for fila in t.rows:
            for celda in fila.cells:
                for p in celda.paragraphs:
                    revisar(p, "tabla")
    return fuera


# --- Documento ---------------------------------------------------------------

# Nombres de estilo por idioma. Word los traduce, asi que una plantilla en
# espanol trae `Titulo 1` donde el script escribe `Heading 1`. Escribir contra un
# nombre que la plantilla no tiene revienta o, peor, deja el parrafo sin formato
# y el documento parece correcto hasta que alguien lo abre.
EQUIVALENTES = {
    "Title":       ["Title", "Título", "Titulo"],
    "Subtitle":    ["Subtitle", "Subtítulo", "Subtitulo"],
    "Heading 1":   ["Heading 1", "Título 1", "Titulo 1"],
    "Heading 2":   ["Heading 2", "Título 2", "Titulo 2"],
    "Heading 3":   ["Heading 3", "Título 3", "Titulo 3"],
    # Solo estilos que **numeran de verdad**. `List Paragraph` / `Parrafo de
    # lista` esta aparte a proposito: es el estilo que Word usa como envoltorio
    # de una lista --sangria y espaciado-- pero no lleva vineta ninguna, asi que
    # tomarlo por un estilo de lista deja el DF lleno de parrafos sangrados sin
    # punto delante. Se usa como acompanante de la numeracion, nunca en su lugar.
    "List Bullet": ["List Bullet", "Lista con viñetas", "Lista con vinetas",
                    "Lista de viñetas", "Viñeta", "Bullet List"],
    "List Paragraph": ["List Paragraph", "Párrafo de lista", "Parrafo de lista"],
}


def _numera(estilo) -> bool:
    """Si el estilo, o alguno del que hereda, trae `numPr` en su definicion.

    Es lo que separa una vineta de verdad de un parrafo sangrado. Un estilo
    puede llamarse `Lista con viñetas` y no numerar --pasa cuando la plantilla
    lo trae como estilo latente sin definicion propia--, y entonces el DF sale
    con el texto corrido aunque el nombre prometa otra cosa.
    """
    from docx.oxml.ns import qn

    visto: set = set()
    while estilo is not None and id(estilo._element) not in visto:
        visto.add(id(estilo._element))
        ppr = estilo._element.find(qn("w:pPr"))
        if ppr is not None and ppr.find(qn("w:numPr")) is not None:
            return True
        estilo = estilo.base_style
    return False


def crear_vineta(doc) -> int | None:
    """Anade al documento una definicion de vineta propia y devuelve su `numId`.

    Hace falta cuando la plantilla del cliente no trae ningun estilo que numere.
    Sin esto, la unica alternativa es escribir el punto a mano en el texto, que
    ni se renumera, ni se promociona de nivel, ni se comporta como una lista al
    copiarla. Devuelve `None` si el documento no admite numeracion, y entonces
    quien llama recurre al punto literal.
    """
    from docx.oxml import parse_xml
    from docx.oxml.ns import nsdecls

    W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    try:
        num = doc.part.numbering_part.element
    except Exception:
        return None
    abstractos = num.findall(W + "abstractNum")
    aid = max((int(a.get(W + "abstractNumId")) for a in abstractos), default=-1) + 1
    nid = max((int(n.get(W + "numId")) for n in num.findall(W + "num")), default=0) + 1
    abstracto = parse_xml(
        f'<w:abstractNum {nsdecls("w")} w:abstractNumId="{aid}">'
        '<w:multiLevelType w:val="hybridMultilevel"/>'
        '<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/>'
        '<w:lvlText w:val="\uf0b7"/><w:lvlJc w:val="left"/>'
        '<w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr>'
        '<w:rPr><w:rFonts w:ascii="Symbol" w:hAnsi="Symbol" w:hint="default"/></w:rPr>'
        "</w:lvl></w:abstractNum>")
    # los `abstractNum` van antes que los `num`, y Word es estricto con el orden
    if abstractos:
        abstractos[-1].addnext(abstracto)
    else:
        num.insert(0, abstracto)
    num.append(parse_xml(f'<w:num {nsdecls("w")} w:numId="{nid}">'
                         f'<w:abstractNumId w:val="{aid}"/></w:num>'))
    return nid


def marcar_vineta(parrafo, num_id: int) -> None:
    """Cuelga el parrafo de una numeracion concreta."""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    ppr = parrafo._p.get_or_add_pPr()
    numpr = OxmlElement("w:numPr")
    for tag, val in (("w:ilvl", "0"), ("w:numId", str(num_id))):
        hijo = OxmlElement(tag)
        hijo.set(qn("w:val"), val)
        numpr.append(hijo)
    ppr.append(numpr)


class Estilos:
    """Traduce los nombres logicos a los que existen de verdad en el documento.

    Lo que no puede es fallar en silencio: cada estilo ausente se **reporta** y
    su parrafo se escribe sin estilo, en vez de reventar a mitad del documento.

    Con la vineta va un paso mas alla, porque ahi fallar en silencio es lo que
    venia pasando: el estilo se resolvia por nombre y bastaba con que la
    plantilla trajera `Parrafo de lista` para dar la lista por buena, cuando ese
    estilo sangra pero no pone vineta. El DF salia entonces como un parrafo
    corrido. Ahora el estilo solo vale si **numera de verdad**, y si ninguno lo
    hace se crea una numeracion propia en el documento.
    """

    def __init__(self, doc) -> None:
        self.doc = doc
        estilos = {s.name: s for s in doc.styles}
        self.mapa = {k: next((c for c in v if c in estilos), None)
                     for k, v in EQUIVALENTES.items()}
        # la vineta se exige que numere; el nombre solo no basta
        vineta = next((c for c in EQUIVALENTES["List Bullet"]
                       if c in estilos and _numera(estilos[c])), None)
        self.mapa["List Bullet"] = vineta
        # con que colgar los parrafos cuando la plantilla no trae vineta propia
        self.num_vineta: int | None = None if vineta else crear_vineta(doc)
        self.vineta_propia = vineta is None
        self.sin_vineta = vineta is None and self.num_vineta is None
        # `List Paragraph` nunca se reporta --es un acompanante, no un estilo
        # que haga falta--, y la vineta solo si no se ha podido suplir.
        self.faltan = sorted(k for k, v in self.mapa.items()
                             if v is None and k != "List Paragraph"
                             and not (k == "List Bullet" and not self.sin_vineta))

    def __call__(self, logico: str):
        return self.mapa.get(logico, logico)

    def vineta(self, doc, texto: str):
        """Escribe `texto` como elemento de lista, con vineta pase lo que pase.

        Tres caminos, en orden de preferencia: el estilo de la plantilla si
        numera --lo que respeta el formato del cliente--, una numeracion creada
        aqui colgada del envoltorio que Word usa para las listas, y como ultimo
        recurso el punto escrito en el texto, que al menos se ve.
        """
        estilo = self.mapa.get("List Bullet")
        if estilo:
            return parrafo_marcado(doc, texto, estilo)
        if self.num_vineta is not None:
            p = parrafo_marcado(doc, texto, self.mapa.get("List Paragraph"))
            marcar_vineta(p, self.num_vineta)
            return p
        from docx.shared import Pt

        p = parrafo_marcado(doc, "\u2022\u00a0" + texto)
        p.paragraph_format.left_indent = Pt(18)
        p.paragraph_format.first_line_indent = Pt(-12)
        return p


# Los apartados del DF, y como se llaman en las plantillas que se han visto. Se
# comparan por clave normalizada --sin tildes, sin la numeracion del titulo y en
# minusculas-- porque cada cliente los escribe a su manera y el DF tiene que
# servir para cualquiera.
ALIAS = {
    "introduccion": "introduccion",
    "alcance": "alcance",
    "filtros campos": "campos", "filtros y campos": "campos", "campos": "campos",
    "integraciones otros aplicativos": "integraciones",
    "integraciones con otros aplicativos": "integraciones",
    "integraciones": "integraciones",
    "validaciones reglas acciones": "validaciones",
    "validaciones y reglas": "validaciones", "validaciones": "validaciones",
    "especificas del frontal": "validaciones_frontal",
    "especificas del core": "validaciones_core",
    "mensajes y avisos": "mensajes", "mensajes": "mensajes",
    "especificos del frontal": "mensajes_frontal",
    "especificos de integracion no core": "mensajes_integracion",
    "especificos del core": "mensajes_core",
    "pantallas y prototipo": "pantallas", "pantallas": "pantallas",
    "criterios de aceptacion": "criterios",
    "especificaciones tecnicas": "especificaciones",
    "puntos abiertos": "puntos_abiertos",
    "control de versiones": "control_versiones",
    "control de aprobaciones": "control_aprobaciones",
}


def clave(texto: str) -> str:
    """`2.3 Validaciones / Reglas` -> `validaciones reglas`."""
    t = unicodedata.normalize("NFKD", texto or "")
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    t = re.sub(r"^[\d.\s]+", "", t.strip())
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def nivel_titulo(parrafo) -> int | None:
    """El nivel del titulo, o None si el parrafo no es un titulo."""
    m = re.match(r"^(?:Heading|T[ií]tulo)\s*([1-9])$", parrafo.style.name or "")
    return int(m.group(1)) if m else None


def plantilla_numera(doc) -> bool:
    """True si los titulos de la plantilla ya se numeran solos.

    Hay que mirar **el parrafo y no solo el estilo**: Word deja la numeracion
    enganchada a cada parrafo (`numPr` directo) tan a menudo como en el estilo, y
    mirando solo el estilo se concluye que no numera. Entonces el generador
    antepone su `1.` al que Word ya pone y sale `1. 1. Introduccion`.
    """
    from docx.oxml.ns import qn

    for p in doc.paragraphs:
        if nivel_titulo(p) and p._p.find(".//" + qn("w:numPr")) is not None:
            return True
    for nombre in EQUIVALENTES["Heading 1"] + EQUIVALENTES["Heading 2"]:
        try:
            estilo = doc.styles[nombre]
        except KeyError:
            continue
        if estilo.element.find(".//" + qn("w:numPr")) is not None:
            return True
    return False


def localizar_apartados(doc) -> dict:
    """Los apartados del DF que la plantilla ya trae, por clave.

    Devuelve `{clave: parrafo}`. No exige que sean titulos: las plantillas
    escriben "Control de Versiones" como parrafo normal encima de su tabla tan a
    menudo como con estilo de titulo.
    """
    fuera: dict = {}
    for p in doc.paragraphs:
        k = ALIAS.get(clave(p.text))
        if not k or k in fuera:
            continue
        # Solo cuenta si es un **titulo**. El texto de ejemplo de una plantilla
        # dice "Validaciones", "Reglas" o "Acciones" en parrafos sueltos, y
        # tomarlos por apartados descuadra todo el reparto. La excepcion son los
        # dos controles, que las plantillas rotulan con un parrafo normal encima
        # de su tabla.
        if nivel_titulo(p) is None and k not in ("control_versiones", "control_aprobaciones"):
            continue
        fuera[k] = p
    return fuera


def limpiar_cuerpo(doc) -> None:
    """Vacia la plantilla conservando estilos, cabecera, pie y formato de pagina.

    Una plantilla suele traer texto de ejemplo; sin quitarlo el DF sale detras.
    Se conserva el `sectPr` final, que es donde viven margenes, tamano y
    orientacion: borrarlo devolveria el documento a los valores por defecto y se
    perderia justo lo que aporta la plantilla.
    """
    cuerpo = doc.element.body
    for hijo in list(cuerpo):
        if not hijo.tag.endswith("}sectPr"):
            cuerpo.remove(hijo)


def titulador(doc, est, numerar: bool = True):
    """Titulos numerados y con el estilo que exista.

    Word no numera los estilos `Heading` por si solo --hace falta una lista
    multinivel vinculada, que en python-docx es XML a mano--. El numero literal
    encaja aqui porque el documento se **regenera**, nunca se edita a mano: no
    hay renumeracion que mantener. Con una plantilla cuyos estilos ya numeren se
    desactiva desde el manifiesto, o saldria `1. 1. Introduccion`.
    """
    estado = {1: 0, 2: 0, 3: 0}

    def escribe(texto: str, nivel: int) -> None:
        if numerar and nivel in estado:
            estado[nivel] += 1
            for menor in range(nivel + 1, 4):
                estado[menor] = 0
            prefijo = ".".join(str(estado[n]) for n in range(1, nivel + 1))
            texto = f"{prefijo}. {texto}" if nivel == 1 else f"{prefijo} {texto}"
        doc.add_paragraph(texto, style=est(f"Heading {nivel}"))

    return escribe


def rango_seccion(doc, parrafo) -> list:
    """Lo que cuelga de un apartado: hasta el siguiente apartado o titulo par.

    Es el texto de ejemplo que trae la plantilla, que se machaca. Lo que **no**
    entra aqui es el titulo en si --con su estilo y su numeracion-- ni la tabla,
    que son de la plantilla y se quedan.
    """
    from docx.text.paragraph import Paragraph

    nivel = nivel_titulo(parrafo) or 9
    fuera = []
    el = parrafo._p.getnext()
    while el is not None:
        etiqueta = el.tag.rsplit("}", 1)[-1]
        if etiqueta == "sectPr":
            break
        if etiqueta == "sdt":
            # El indice es de la plantilla y no se toca: se salta sin cortar el
            # tramo, porque detras puede seguir habiendo ejemplo que si sobra.
            # Los demas controles de contenido llevan texto de ejemplo y caen
            # con el resto.
            from docx.oxml.ns import qn
            galeria = el.find(".//" + qn("w:docPartGallery"))
            if galeria is not None and galeria.get(qn("w:val")) == "Table of Contents":
                el = el.getnext()
                continue
        if etiqueta == "p":
            otro = Paragraph(el, parrafo._parent)
            n = nivel_titulo(otro)
            if n is not None and n <= nivel:
                break
            if nivel_titulo(otro) is not None and ALIAS.get(clave(otro.text)):
                break
            if ALIAS.get(clave(otro.text)) in ("control_versiones", "control_aprobaciones"):
                break
        fuera.append(el)
        el = el.getnext()
    return fuera


def tabla_de(doc, elementos):
    """La primera tabla del tramo, si la hay. Es la de la plantilla: se reusa."""
    from docx.table import Table

    for el in elementos:
        if el.tag.endswith("}tbl"):
            return Table(el, doc)
    return None


def rellenar_tabla(tabla, columnas: list[str], filas: list[list[str]]) -> None:
    """Reescribe los datos conservando la tabla de la plantilla.

    Se reusa en vez de crear una nueva porque el estilo, los anchos y la fila de
    cabecera son del cliente: una tabla nueva con `Table Grid` canta.
    """
    cabecera = tabla.rows[0]
    if not "".join(c.text for c in cabecera.cells).strip():
        for i, texto in enumerate(columnas[: len(cabecera.cells)]):
            cabecera.cells[i].text = str(texto)
    for fila in list(tabla.rows[1:]):
        fila._tr.getparent().remove(fila._tr)
    ancho = len(tabla.columns)
    for fila in filas or []:
        celdas = tabla.add_row().cells
        for i, v in enumerate(fila[:ancho]):
            escribir_marcado(celdas[i].paragraphs[0], "" if v is None else str(v))


def mover_tras(doc, ancla, escritor):
    """Ejecuta el escritor --que escribe al final-- y lleva lo escrito tras `ancla`.

    python-docx solo sabe anadir al final del cuerpo. Para escribir **dentro**
    del apartado que trae la plantilla se escribe al final y se traslada, que es
    mas simple que reimplementar cada `add_paragraph` con posicion.
    """
    cuerpo = doc.element.body
    # La lista se **conserva**: lxml crea los proxies al vuelo y los recolecta,
    # asi que guardar solo sus `id()` no vale --al volver a recorrer el cuerpo
    # los mismos nodos traen ids distintos y "lo nuevo" sale mal--. Manteniendo
    # las referencias vivas, comparar por identidad si es fiable.
    previos = list(cuerpo)
    escritor()
    for el in [x for x in cuerpo if not any(x is y for y in previos)]:
        ancla.addnext(el)
        ancla = el
    return ancla


def build(m: dict, salida: Path, plantilla: Path | None = None) -> dict:
    from docx import Document

    branding = marca.normalizar(m.get("branding"))
    accent = (branding.get("color_secundario") or branding.get("color_principal") or "D9D9D9")
    accent = accent.lstrip("#").upper()

    proyecto = m.get("proyecto", "")
    titulo = m.get("titulo") or m.get("hu_id") or "Documento de Diseno Funcional"
    version = str(m.get("version", "1.0"))
    hoy = m.get("fecha") or date.today().isoformat()

    avisos: list[str] = []
    numera_ella = False
    apartados_plantilla: list[str] = []
    modo = "generar"
    if plantilla:
        if not plantilla.is_file():
            raise SystemExit(f"No existe la plantilla '{plantilla}'.")
        doc = Document(str(plantilla))
        # Se interroga a la plantilla **antes** de vaciarla: despues no queda
        # nada que mirar. La numeracion vive en los parrafos de titulo y los
        # apartados en su texto, y los dos desaparecen con el cuerpo.
        numera_ella = plantilla_numera(doc)
        apartados_plantilla = sorted(localizar_apartados(doc))
        # Con los apartados reconocidos se escribe **dentro** de ellos y no se
        # toca nada mas: portada, logo, indice, tablas, cabecera y secciones se
        # quedan como el cliente las monto. Vaciar el cuerpo se lleva por delante
        # incluso la cabecera, porque una plantilla de varias secciones enlaza la
        # segunda a la primera y al desaparecer esta la cabecera se queda sin nada.
        if len(apartados_plantilla) >= 3:
            modo = "esqueleto"
        else:
            avisos.append(
                "la plantilla no trae los apartados del DF reconocibles"
                + (f" (solo {', '.join(apartados_plantilla)})" if apartados_plantilla else "")
                + ": se usa solo por sus estilos y el cuerpo se escribe entero")
            limpiar_cuerpo(doc)
    else:
        doc = Document()
    est = Estilos(doc)
    if est.faltan:
        avisos.append("estilos que la plantilla no trae (esas partes salen sin formato): "
                      + ", ".join(est.faltan))
    if est.vineta_propia and not est.sin_vineta:
        avisos.append("la plantilla no trae ningun estilo de vineta que numere; las "
                      "listas se cuelgan de una numeracion creada en el documento")
    if est.sin_vineta:
        avisos.append("el documento no admite numeracion: las listas salen con el "
                      "punto escrito en el texto y sangria colgante")
    # Si la plantilla ya numera sus titulos, numerar aqui saca `1. 1. Introduccion`.
    # Se deduce en vez de preguntarse, porque **Word engancha la numeracion al
    # parrafo tan a menudo como al estilo** y mirando solo el estilo se concluye
    # que no numera. El manifiesto sigue mandando si lo dice explicitamente.
    if numera_ella:
        avisos.append("la plantilla ya numera sus titulos: el generador no antepone "
                      "el suyo, o saldria '1. 1. Introduccion'")
    numerar = m.get("numerar_apartados")
    if numerar is None:
        numerar = not numera_ella
    h = titulador(doc, est, numerar=bool(numerar))
    if branding:
        marca.aplicar_estilos_word(doc, branding)
    # Con plantilla, la cabecera y el pie son suyos: escribir ahi borraria los
    # runs del parrafo y con ellos el logo del cliente. Solo se escriben cuando
    # la plantilla no trae nada, o cuando no hay plantilla.
    cabecera_pie = marca.cabecera_pie_word(
        doc, branding,
        cabecera=f"{proyecto} · {titulo}".strip(" ·"),
        pie=f"Versión {version}",
        respetar_existente=bool(plantilla)) or ["cabecera y pie generados por el skill"]

    # El contenido de cada apartado, separado de donde se escribe. Cada escritor
    # anade al final del documento; en modo esqueleto se traslada despues al
    # apartado que la plantilla ya trae.
    nar = m.get("narrativa") or {}
    campos = m.get("campos") or {}
    val = m.get("validaciones") or {}
    msg = m.get("mensajes") or {}
    ca = m.get("criterios_aceptacion") or {}
    pa = m.get("puntos_abiertos") or []

    cols_campos = campos.get("columnas") or ["Nombre", "Editable", "Oblig", "Tipo", "Comentario"]
    COLS_PA = ["ID", "Descripción", "Estado", "Responsable", "F. Estimada", "F. Resolución"]
    COLS_CV = ["Fecha", "Versión", "Autor", "Descripción del cambio"]
    COLS_CA = ["Responsable", "Cargo", "Departamento", "Fecha", "Versión del documento"]

    filas_cv = []
    for c in (m.get("control_versiones") or
              [{"fecha": hoy, "version": version, "autor": m.get("autor", ""),
                "cambio": "Versión inicial"}]):
        firma, nota = autor_persona(c.get("autor"))
        if nota and nota not in avisos:
            avisos.append(nota)
        filas_cv.append([c.get("fecha", ""), c.get("version", ""),
                         firma or CELDA_PENDIENTE, c.get("cambio", "")])
    filas_ca = [[a.get("responsable", ""), a.get("cargo", ""), a.get("departamento", ""),
                 a.get("fecha", ""), a.get("version", "")]
                for a in (m.get("control_aprobaciones") or [{}, {}, {}])]
    # En el control de versiones un hueco es un dato que falta, y se marca. En
    # el de aprobaciones **no**: esa tabla se entrega vacia a proposito --no se
    # inventan aprobadores-- y marcar sus quince celdas la deja en amarillo
    # entera, que es ruido y no informacion. Ahi la marca va una sola vez,
    # debajo de la tabla. En las demas tablas una celda vacia suele significar
    # "no aplica", asi que no se toca ninguna.
    for fila in filas_cv:
        for i, v in enumerate(fila):
            if not str(v or "").strip():
                fila[i] = CELDA_PENDIENTE
    aprobaciones_vacias = not any("".join(str(v or "") for v in fila).strip()
                                  for fila in filas_ca)
    if not aprobaciones_vacias:
        for fila in filas_ca:
            if "".join(str(v or "") for v in fila).strip():
                for i, v in enumerate(fila):
                    if not str(v or "").strip():
                        fila[i] = CELDA_PENDIENTE
    filas_pa = [[x.get("id", ""), x.get("descripcion", ""), x.get("estado", "Abierto"),
                 x.get("responsable", ""), x.get("estimada", ""), x.get("resolucion", "")]
                for x in pa]

    def narrativa():
        if any(nar.values()):
            for etiqueta, k in (("COMO", "como"), ("QUIERO", "quiero"), ("PARA", "para")):
                par = doc.add_paragraph()
                par.add_run(f"{etiqueta} ").bold = True
                par.add_run(nar.get(k, ""))
        else:
            parrafo_marcado(doc, PENDIENTE)

    def pantallas():
        write_blocks(doc, m.get("pantallas"), est=est)
        from docx.shared import Cm
        for img in m.get("imagenes") or []:
            if Path(img).is_file():
                try:
                    doc.add_picture(img, width=Cm(15))
                except Exception:  # noqa: BLE001
                    parrafo_marcado(doc, f"[No se pudo insertar la imagen: {img}]")
            else:
                parrafo_marcado(doc, f"[Imagen no encontrada: {img}]")

    def criterios():
        if ca.get("contexto"):
            write_blocks(doc, ca["contexto"], est=est)
        esc = ca.get("escenarios") or []
        for e in esc:
            # El manifiesto los trae como "- Escenario X: ...". El guion sobra
            # dentro de una vineta: saldria una vineta y un guion.
            est.vineta(doc, str(e).lstrip("-*\u2022 ").strip())
        if not esc and not ca.get("contexto"):
            parrafo_marcado(doc, PENDIENTE)

    def prosa(valor):
        return lambda: write_blocks(doc, valor, est=est)

    # (clave, titulo, nivel, escritor, tabla_o_None)
    APARTADOS_DF = [
        ("control_versiones", "Control de Versiones", 2, None, (COLS_CV, filas_cv)),
        ("control_aprobaciones", "Control de Aprobaciones", 2, None, (COLS_CA, filas_ca)),
        ("introduccion", "Introducción", 1, prosa(m.get("introduccion")), None),
        ("alcance", "Alcance", 2, prosa(m.get("alcance")), None),
        ("historia", titulo, 1, narrativa, None),
        ("campos", "Filtros/Campos", 2, None, (cols_campos, campos.get("filas"))),
        ("integraciones", "Integraciones otros aplicativos", 2,
         prosa(m.get("integraciones")), None),
        ("validaciones", "Validaciones / Reglas / Acciones", 2, None, None),
        ("validaciones_frontal", "Específicas del Frontal", 3, prosa(val.get("frontal")), None),
        ("validaciones_core", "Específicas del Core", 3, prosa(val.get("core")), None),
        ("mensajes", "Mensajes y avisos", 2, None, None),
        ("mensajes_frontal", "Específicos del Frontal", 3, prosa(msg.get("frontal")), None),
        ("mensajes_integracion", "Específicos de Integración no Core", 3,
         prosa(msg.get("integracion_no_core")), None),
        ("mensajes_core", "Específicos del Core", 3, prosa(msg.get("core")), None),
        ("pantallas", "Pantallas y Prototipo", 2, pantallas, None),
        ("criterios", "Criterios de aceptación", 1, criterios, None),
        ("especificaciones", "Especificaciones Técnicas", 1,
         prosa(m.get("especificaciones_tecnicas")), None),
        ("puntos_abiertos", "Puntos abiertos", 1, None, (COLS_PA, filas_pa)),
    ]

    anclas = localizar_apartados(doc) if modo == "esqueleto" else {}
    sin_apartado: list[str] = []

    if modo == "esqueleto":
        # La portada no es un apartado, asi que sin esto se queda con el titulo
        # de ejemplo que traiga la plantilla.
        if not poner_titulo(doc, est, titulo, proyecto):
            avisos.append("la plantilla no trae un parrafo con estilo de titulo en la "
                          "portada: el titulo del documento hay que ponerlo a mano")
        # El titulo de la historia es el unico que no se reconoce por su texto:
        # en la plantilla lleva el nombre del caso del cliente. Es el Titulo 1
        # que va entre Alcance y el primer apartado de la historia.
        entre = [p_ for p_ in doc.paragraphs if nivel_titulo(p_) == 1]
        for p_ in entre:
            if anclas.get("alcance") is not None and anclas.get("campos") is not None \
                    and anclas["alcance"]._p.getparent().index(anclas["alcance"]._p) \
                    < p_._p.getparent().index(p_._p) \
                    < anclas["campos"]._p.getparent().index(anclas["campos"]._p):
                for run in list(p_.runs)[1:]:
                    run._r.getparent().remove(run._r)
                if p_.runs:
                    p_.runs[0].text = titulo
                else:
                    p_.add_run(titulo)
                anclas["historia"] = p_
                break

        for k, _t, _n, escritor, tabla in APARTADOS_DF:
            ancla = anclas.get(k)
            if ancla is None:
                sin_apartado.append(k)
                continue
            tramo = rango_seccion(doc, ancla)
            propia = tabla_de(doc, tramo) if tabla else None
            for el in tramo:
                if propia is not None and el is propia._tbl:
                    continue          # la tabla es de la plantilla: se rellena
                el.getparent().remove(el)
            if tabla:
                cols, filas = tabla
                if propia is not None:
                    rellenar_tabla(propia, cols, filas)
                    fin = propia._tbl
                elif filas:
                    fin = mover_tras(doc, ancla._p,
                                     lambda c=cols, f=filas: add_table(doc, c, f, accent))
                else:
                    fin = mover_tras(doc, ancla._p, lambda: doc.add_paragraph("N/A"))
                # La nota va **detras** de la tabla, como en el modo sin
                # plantilla. Colgada del titulo caia entre el titulo y la tabla.
                if k == "control_aprobaciones" and aprobaciones_vacias:
                    mover_tras(doc, fin, lambda: parrafo_marcado(
                        doc, "[PENDIENTE: completar el control de aprobaciones con "
                             "los responsables que firman el documento]"))
            elif escritor:
                mover_tras(doc, ancla._p, escritor)
    else:
        # Portada y control, que con esqueleto ya trae la plantilla.
        if proyecto:
            doc.add_paragraph(proyecto, style=est("Title"))
        doc.add_paragraph(titulo, style=est("Title") if not proyecto else est("Subtitle"))
        doc.add_paragraph(f"Documento de Diseño Funcional · Versión {version} · {hoy}")
        doc.add_paragraph()
        doc.add_paragraph("Control de Versiones", style=est("Heading 2"))
        add_table(doc, COLS_CV, filas_cv, accent)
        doc.add_paragraph("Control de Aprobaciones", style=est("Heading 2"))
        add_table(doc, COLS_CA, filas_ca, accent)
        if aprobaciones_vacias:
            parrafo_marcado(doc, "[PENDIENTE: completar el control de aprobaciones "
                                 "con los responsables que firman el documento]")
        doc.add_paragraph("Índice", style=est("Heading 2"))
        add_toc(doc)
        doc.add_page_break()

        for k, t_, n_, escritor, tabla in APARTADOS_DF:
            if k in ("control_versiones", "control_aprobaciones"):
                continue
            h(t_, n_)
            if tabla:
                cols, filas = tabla
                if filas:
                    add_table(doc, cols, filas, accent)
                elif k == "campos":
                    doc.add_paragraph("N/A")
                else:
                    add_table(doc, cols, [], accent)
            elif escritor:
                escritor()

    for extra in m.get("secciones_adicionales") or []:
        if modo == "generar":
            h(extra.get("titulo", "Anexo"), 1)
        else:
            doc.add_paragraph(extra.get("titulo", "Anexo"), style=est("Heading 1"))
        write_blocks(doc, extra.get("contenido"), est=est)

    # El logo suele vivir solo en la cabecera de la portada; sin esto, el resto
    # de paginas sale sin el.
    propagadas = propagar_cabecera(doc)
    if propagadas:
        avisos.append("la cabecera de la portada se ha copiado al resto de paginas "
                      "(seccion " + ", ".join(propagadas) + "), que la tenian vacia: "
                      "asi el logo sale en todas")

    # Lo que la plantilla traia como relleno y nadie ha sustituido.
    relleno = marcar_relleno(doc)
    if relleno:
        avisos.append(f"queda texto de relleno de la plantilla sin sustituir "
                      f"({len(relleno)}): va resaltado en amarillo, pero revisalo")

    # El titulo del documento, el que ve Word en las propiedades del fichero.
    doc.core_properties.title = f"{proyecto} · {titulo}" if proyecto else titulo
    doc.core_properties.subject = "Documento de Diseño Funcional"

    salida.parent.mkdir(parents=True, exist_ok=True)
    doc.save(salida)
    return {"output": str(salida), "puntos_abiertos": len(pa),
            # Donde han quedado codigos internos (RF-, GAP-, ...). No bloquean la
            # generacion, pero el skill tiene que cantarlos: en el DF sobran.
            "codigos_internos": codigos_internos(m),
            "cabecera_pie": cabecera_pie,
            "modo": modo,
            # Los apartados que la plantilla traia y los del DF que no estaban en
            # ella. Los segundos no se pierden: van al final con su titulo.
            "apartados_plantilla": apartados_plantilla,
            "apartados_no_encontrados": sin_apartado,
            "plantilla_numera": numera_ella,
            # De donde sale la vineta: el estilo de la plantilla, una
            # numeracion creada aqui, o el punto escrito a mano.
            "vinetas": ("plantilla" if not est.vineta_propia
                        else "creada" if not est.sin_vineta else "literal"),
            # Texto de relleno de la plantilla que ha quedado en el documento,
            # con el apartado en el que esta. Resaltado, pero hay que resolverlo.
            "relleno_sin_sustituir": relleno,
            "secciones_adicionales": len(m.get("secciones_adicionales") or []),
            "plantilla": str(plantilla) if plantilla else None,
            # Los estilos que la plantilla no traia. Sin reportarlos, el
            # documento sale con partes sin formato y nadie se entera hasta
            # abrirlo.
            "avisos": avisos}


def extraer(ruta: Path) -> dict:
    """El texto y las tablas de un DF ya generado, para que otro skill los lea.

    Un `.docx` es un zip de XML: nadie lo lee de un vistazo. `aiba-test-plan`
    dice que el DF es su mejor fuente --sus validaciones y sus mensajes ya son
    casos de prueba casi literales-- y sin esto esa frase seria decorativa.
    """
    import docx

    d = docx.Document(ruta)
    parrafos = {p._p: p for p in d.paragraphs}
    tablas = {tb._tbl: tb for tb in d.tables}

    secciones: list[dict] = []
    actual = {"titulo": "(portada)", "nivel": 0, "parrafos": [], "tablas": []}
    for bloque in d.element.body.iterchildren():
        p = parrafos.get(bloque)
        if p is not None:
            if not p.text.strip():
                continue
            if p.style.name.startswith("Heading"):
                secciones.append(actual)
                sufijo = p.style.name.split()[-1]
                actual = {"titulo": p.text.strip(),
                          "nivel": int(sufijo) if sufijo.isdigit() else 1,
                          "parrafos": [], "tablas": []}
            else:
                actual["parrafos"].append(p.text.strip())
            continue
        tb = tablas.get(bloque)
        if tb is not None:
            actual["tablas"].append([[c.text.strip() for c in fila.cells]
                                     for fila in tb.rows])
    secciones.append(actual)
    return {"fichero": str(ruta),
            "secciones": [s for s in secciones if s["parrafos"] or s["tablas"]]}


def main() -> int:
    ap = argparse.ArgumentParser(description="Genera el DF en Word de una historia de usuario.")
    ap.add_argument("--manifest", help="JSON con el contenido del DF; sin el, stdin")
    ap.add_argument("--output", help="ruta del .docx de salida")
    ap.add_argument("--schema", action="store_true", help="imprime el esquema del manifiesto y sale")
    ap.add_argument("--extraer", metavar="RUTA",
                    help="vuelca a JSON el texto y las tablas de un DF ya generado, "
                         "para que otro skill pueda leerlo, y sale")
    ap.add_argument("--plantilla", default=None,
                    help="plantilla .docx/.dotx del cliente: el documento hereda sus "
                         "estilos, cabecera, pie y formato de pagina")
    ap.add_argument("--no-install", action="store_true", help="no instalar python-docx al vuelo")
    args = ap.parse_args()

    if args.schema:
        print(SCHEMA)
        return 0
    if args.extraer:
        _ensure_docx(not args.no_install)
        ruta = Path(args.extraer)
        if not ruta.is_file():
            sys.stderr.write(f"No existe el DF '{ruta}'.\n")
            return 2
        print(json.dumps(extraer(ruta), ensure_ascii=False, indent=2))
        return 0
    if not args.output:
        ap.error("--output es obligatorio (o usa --schema)")

    raw = Path(args.manifest).read_text(encoding="utf-8") if args.manifest else sys.stdin.read()
    try:
        m = json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"Manifiesto JSON invalido: {exc}\n")
        return 2

    _ensure_docx(allow_install=not args.no_install)
    print(json.dumps(build(m, Path(args.output),
                          Path(args.plantilla) if args.plantilla else None),
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
