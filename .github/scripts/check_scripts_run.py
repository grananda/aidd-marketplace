#!/usr/bin/env python3
"""Los scripts que producen un entregable **se ejecutan**, no solo compilan.

`py_compile` no ve un `NameError`: el fichero compila y revienta al usarlo. Paso
exactamente por eso --una variable mal escrita en `compute_kpis.py` llego a una
release y dejaba `aiba metrics` sin poder ejecutarse--, y ninguna de las nueve
comprobaciones lo detecto porque ninguna **llamaba** al script.

Esta lo hace: monta un proyecto minimo y lo ejecuta de punta a punta. No valida
las cifras --eso es de cada script-- sino que termine con exito y devuelva algo
parseable. Es un humo, y es el que faltaba.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

def _campos(elemento) -> list[str]:
    """Los hijos de un run que forman parte de un campo de Word."""
    return [q.tag.rsplit("}", 1)[-1] for q in elemento
            if q.tag.rsplit("}", 1)[-1] in ("fldChar", "instrText", "t")]


def _numera_de_verdad(doc, parrafo) -> bool:
    """Si el parrafo saldra con vineta al abrirlo, venga de donde venga.

    Puede venir de un `numPr` colgado del propio parrafo o del estilo --o de
    alguno del que este herede--. Mirar solo el nombre del estilo no sirve.
    """
    from docx.oxml.ns import qn

    ppr = parrafo._p.find(qn("w:pPr"))
    if ppr is not None and ppr.find(qn("w:numPr")) is not None:
        return True
    estilos = {e.name: e for e in doc.styles}
    est = estilos.get(parrafo.style.name) if parrafo.style is not None else None
    visto = set()
    while est is not None and id(est._element) not in visto:
        visto.add(id(est._element))
        spr = est._element.find(qn("w:pPr"))
        if spr is not None and spr.find(qn("w:numPr")) is not None:
            return True
        est = est.base_style
    return False


def _revisar_df(doc, salida_json: dict, etiqueta: str) -> list[str]:
    """Las cuatro reglas del generador, sobre el .docx ya escrito.

    Ninguna estaba cubierta, y dos de ellas son averias que llegaron a los
    analistas: el indice se comia el texto y la plantilla se pisaba.
    """
    fallos = []

    # El campo TOC, montado como lo monta Word: envuelto en un `sdt` de galeria
    # "Table of Contents" y **repartido entre varios parrafos**, con el `begin`
    # en el primero y el `end` en el ultimo. Meterlos en el mismo parrafo obliga
    # a Word, al actualizar, a convertir un campo de un parrafo en uno de
    # treinta, y al reconstruir el rango se lleva las marcas de parrafo
    # siguientes: desaparecia el principio de Introduccion y Alcance. Los
    # parrafos de un `sdt` no salen en `doc.paragraphs`, asi que se mira el XML.
    from docx.oxml.ns import qn                                # noqa: PLC0415

    if etiqueta == "con esqueleto":
        # Tres averias que llegaron a los analistas con la plantilla del
        # cliente: el logo solo en la portada, el titulo de ejemplo sin
        # sustituir y el texto de relleno entregado tal cual.
        from docx.oxml.ns import qn as _q                       # noqa: PLC0415

        cab = doc.sections[0].header
        if next(cab._element.iter(_q("w:drawing")), None) is None:
            fallos.append(f"gen_df_docx.py {etiqueta}: el logo solo queda en la "
                          "cabecera de la portada; el resto de paginas sale sin el")
        else:
            for blip in cab._element.iter(_q("a:blip")):
                rid = blip.get(_q("r:embed"))
                if cab.part.related_parts.get(rid) is None:
                    fallos.append(f"gen_df_docx.py {etiqueta}: la imagen copiada a "
                                  f"la cabecera apunta a una relacion que no existe "
                                  f"({rid}): sale como recuadro roto")

        # La portada es una tabla: hay que mirar dentro, no solo los parrafos.
        portada = " ".join(c_.text for t_ in doc.tables for f_ in t_.rows
                           for c_ in f_.cells)
        portada += " " + " ".join(p_.text for p_ in doc.paragraphs[:6])
        if "Diseño Funcional de Ejemplo" in portada:
            fallos.append(f"gen_df_docx.py {etiqueta}: la portada conserva el titulo "
                          "de ejemplo de la plantilla; en las plantillas reales va en "
                          "una celda de tabla, no en un parrafo con estilo Title")
        if "01/01/2020" in portada or " 0.1 " in f" {portada} ":
            fallos.append(f"gen_df_docx.py {etiqueta}: la portada conserva la version "
                          "o la fecha de la plantilla")
        if not (doc.core_properties.title or "").strip():
            fallos.append(f"gen_df_docx.py {etiqueta}: el titulo del documento (el de "
                          "las propiedades del fichero) se queda vacio")

        cabecera = " ".join(p_.text for p_ in cab.paragraphs)
        if "Diseño Funcional de Ejemplo" in cabecera:
            fallos.append(f"gen_df_docx.py {etiqueta}: la cabecera sigue nombrando al "
                          "documento de la plantilla")
        if "CABECERA DEL CLIENTE" not in cabecera:
            fallos.append(f"gen_df_docx.py {etiqueta}: al poner al dia el nombre del "
                          "documento se ha perdido el texto del cliente")
        if next(cab._element.iter(_q("w:drawing")), None) is None:
            fallos.append(f"gen_df_docx.py {etiqueta}: al reescribir la cabecera se ha "
                          "perdido el logo")

        for _t in ("w:commentRangeStart", "w:commentRangeEnd", "w:commentReference"):
            if doc.element.body.findall(".//" + _q(_t)):
                fallos.append(f"gen_df_docx.py {etiqueta}: quedan marcas de comentario "
                              f"({_t}) de la plantilla en el documento entregado")
        if salida_json.get("comentarios_quitados"):
            import zipfile as _zip                                # noqa: PLC0415
            with _zip.ZipFile(str(salida)) as _z:
                sobran = [n_ for n_ in _z.namelist()
                          if "comment" in n_ or "people" in n_]
            if sobran:
                fallos.append(f"gen_df_docx.py {etiqueta}: se quitaron las marcas pero "
                              f"el paquete conserva {sobran}: Word abre el panel de "
                              "revision con los comentarios huerfanos")
        else:
            fallos.append(f"gen_df_docx.py {etiqueta}: no se ha quitado el comentario "
                          "de Word que traia la plantilla")

        relleno = salida_json.get("relleno_sin_sustituir")
        if relleno is None:
            fallos.append(f"gen_df_docx.py {etiqueta}: la salida no trae "
                          "relleno_sin_sustituir")
        elif not any("RELLENAR" in x for x in relleno):
            fallos.append(f"gen_df_docx.py {etiqueta}: no caza el relleno "
                          f"'<RELLENAR ...>' que trae la plantilla ({relleno})")
        else:
            from docx.enum.text import WD_COLOR_INDEX            # noqa: PLC0415
            marcado = [p_ for p_ in doc.paragraphs if "RELLENAR" in p_.text
                       and any(r_.font.highlight_color == WD_COLOR_INDEX.YELLOW
                               for r_ in p_.runs)]
            if not marcado:
                fallos.append(f"gen_df_docx.py {etiqueta}: el relleno que queda no "
                              "va resaltado, asi que nadie lo ve al revisar")
        return fallos          # el indice y las tablas los pone la plantilla

    cuerpo = doc.element.body
    sdt = next((x for x in cuerpo.findall(qn("w:sdt"))
                if (g := x.find(".//" + qn("w:docPartGallery"))) is not None
                and g.get(qn("w:val")) == "Table of Contents"), None)
    if sdt is None:
        fallos.append(f"gen_df_docx.py {etiqueta}: el indice no va en un sdt de "
                      "galeria 'Table of Contents'; escrito a mano se desfasa y "
                      "montado a medias Word se come el texto al actualizarlo")
    else:
        for parr in sdt.findall(".//" + qn("w:p")):
            marcas = [f.get(qn("w:fldCharType")) for f in parr.iter(qn("w:fldChar"))]
            if "begin" in marcas and "end" in marcas:
                fallos.append(
                    f"gen_df_docx.py {etiqueta}: el campo TOC abre y cierra en el "
                    "mismo parrafo. Word lo reparte; junto, al actualizar el "
                    "indice se come el contenido de despues")
                break
            for r in parr.findall(qn("w:r")):
                if len(_campos(r)) > 1:
                    fallos.append(f"gen_df_docx.py {etiqueta}: el campo TOC mete "
                                  f"{_campos(r)} en un solo run")
                    break

    # Lo que tiene que completar una persona, resaltado. Sin esto un hueco pasa
    # desapercibido en un documento de veinte paginas y acaba firmado.
    from docx.enum.text import WD_COLOR_INDEX                  # noqa: PLC0415
    resaltados = [r.text for p in doc.paragraphs for r in p.runs
                  if r.font.highlight_color == WD_COLOR_INDEX.YELLOW]
    if not any("PENDIENTE" in t for t in resaltados):
        fallos.append(f"gen_df_docx.py {etiqueta}: los [PENDIENTE] no salen "
                      "resaltados en amarillo")
    # Y lo mismo escrito en prosa. Que el hueco se vea no puede depender de que
    # modelo redacto el manifiesto: unos ponen el marcador y otros lo parafrasean.
    if not any("pendiente de definir" in t.lower() for t in resaltados):
        fallos.append(f"gen_df_docx.py {etiqueta}: un hueco escrito en prosa "
                      "('pendiente de definir') no se resalta, asi que el DF sale "
                      "distinto segun que modelo lo redacte")
    # La firma que se vacia por ser la herramienta deja marca, no un hueco mudo.
    celdas = [p_.text for t_ in doc.tables for f_ in t_.rows for c_ in f_.cells
              for p_ in c_.paragraphs
              if any(r_.font.highlight_color == WD_COLOR_INDEX.YELLOW for r_ in p_.runs)]
    if not celdas:
        fallos.append(f"gen_df_docx.py {etiqueta}: el control de versiones deja la "
                      "firma vacia sin marcarla; nadie ve que falta")

    # El autor es una persona, nunca la herramienta.
    autores = [f.cells[2].text for t in doc.tables for f in t.rows[1:]
               if len(f.cells) == 4]
    if any("aiba" in a.lower() for a in autores):
        fallos.append(f"gen_df_docx.py {etiqueta}: el control de versiones firma "
                      f"con el nombre del skill ({autores})")

    # Lo enumerado sale como vineta de Word. Un parrafo con cinco reglas
    # separadas por comas no se lee, no se revisa y no da casos de prueba.
    #
    # Se mira si el parrafo **numera de verdad**, no como se llama su estilo: la
    # averia que motivo esta comprobacion era justo esa. `Parrafo de lista`
    # estaba en la lista de alias de vineta y sangra, pero no pone punto, asi
    # que con una plantilla que no trajera `List Bullet` el DF salia corrido y
    # el nombre del estilo decia que todo estaba bien.
    vinetas = [p.text for p in doc.paragraphs if _numera_de_verdad(doc, p)]
    if not any("Node 20" in v for v in vinetas):
        fallos.append(f"gen_df_docx.py {etiqueta}: las lineas que empiezan por '- ' "
                      f"no salen como vineta ({vinetas[:3]})")

    # Una forma de manifiesto distinta no puede dejar el apartado mudo. `campos`
    # como lista de diccionarios reventaba con `'list' object has no attribute
    # 'get'`, y el analista se quedaba sin ningun DF del lote.
    celdas = [c_.text for t_ in doc.tables for f_ in t_.rows for c_ in f_.cells]
    if "Ramo" not in celdas or "NIF" not in celdas:
        fallos.append(f"gen_df_docx.py {etiqueta}: Filtros y Campos no se rellena "
                      "cuando `campos` viene como lista de diccionarios")

    # Los codigos internos se cazan y se dicen, con su seccion.
    codigos = salida_json.get("codigos_internos")
    if codigos is None:
        fallos.append(f"gen_df_docx.py {etiqueta}: la salida no trae codigos_internos")
    elif not any("RF-014" in c for c in codigos):
        fallos.append(f"gen_df_docx.py {etiqueta}: no caza el RF-014 sembrado en "
                      f"la introduccion ({codigos})")
    return fallos


def _revisar_plantilla(doc, etiqueta: str = "con plantilla") -> list[str]:
    """La cabecera y el pie del cliente sobreviven, con su logo."""
    from docx.oxml.ns import qn                                # noqa: PLC0415

    fallos = []
    cab = doc.sections[0].header
    if next(cab._element.iter(qn("w:drawing")), None) is None:
        fallos.append(f"gen_df_docx.py {etiqueta}: el logo de la cabecera "
                      "desaparece. Escribir con `p.text = ...` borra los runs del "
                      "parrafo, y con ellos el w:drawing")
    if "CABECERA DEL CLIENTE" not in "".join(p.text for p in cab.paragraphs):
        fallos.append(f"gen_df_docx.py {etiqueta}: el texto de cabecera del "
                      "cliente se sustituye por el del skill")
    if "PIE DEL CLIENTE" not in "".join(p.text for p in doc.sections[0].footer.paragraphs):
        fallos.append(f"gen_df_docx.py {etiqueta}: el pie del cliente se pisa")
    return fallos


ROOT = Path(__file__).resolve().parents[2]
KPIS = ROOT / "plugins/aiba/skills/aiba-metrics/scripts/compute_kpis.py"
AUDIT = ROOT / "plugins/aisdd/skills/aisdd-specs/scripts/audit.py"
DF = ROOT / "plugins/aiba/skills/aiba-functional-design/scripts/gen_df_docx.py"

ACTIVIDAD = """# Registro de actividad AIDD

- 2026-09-01T09:00:00Z | user:dev | skill:aisdd-specs | ctx:HU-02 | run | note:-
- 2026-09-03T10:00:00Z | user:dev | skill:aisdd-specs | ctx:HU-01 | run | note:-
- 2026-09-03T10:01:00Z | user:dev | skill:aisdd-specs | ctx:HU-01 | file:src/a.ts | note:-
- 2026-09-03T10:05:00Z | user:dev | skill:aisdd-specs | ctx:HU-01 | turn | note:dur=300s skills=1 files=1
- 2026-09-10T18:00:00Z | user:dev | skill:aisdd-specs | ctx:HU-02 | turn | note:dur=600s skills=1 files=2
"""
# La ventana la fija el registro de actividad, y **filtra la auditoria**: una
# entrada fuera de esas fechas no se cuenta. Con la ventana de cinco minutos que
# habia, cinco de las seis entradas de prueba caian fuera y las comprobaciones
# pasaban en vacio. La primera y la ultima marca tienen que cubrir el periodo
# entero, aperturas incluidas: un `close` cuyo `open` cayo fuera no da lead time.

errors: list[str] = []


def proyecto(d: Path) -> None:
    (d / "docs").mkdir()
    (d / "openspec" / "audit" / "2026-09").mkdir(parents=True)
    (d / "openspec" / "changes" / "archive" / "viejo").mkdir(parents=True)
    (d / "docs" / "aidd-activity.md").write_text(ACTIVIDAD, encoding="utf-8")
    # Tres changes cerrados, no uno. Con uno solo el percentil de lead time no
    # se ejercitaba: `percentile(lead_times, 50)` --50 donde espera una
    # fraccion-- solo revienta a partir del segundo valor, asi que el fallo
    # llego a main con el humo en verde.
    (d / "openspec" / "config.yaml").write_text(
        "roadmap:\n  phases:\n"
        "    - id: F-01\n      change_hint: nuevo\n      effort_ai: 2\n"
        "    - id: F-02\n      change_hint: lento\n      effort_ai: 1\n"
        "    - id: F-03\n      change_hint: mudo\n      effort_ai: 1\n",
        encoding="utf-8")
    entradas = [
        {"command": "aisdd open change", "change_id": "nuevo", "id": "a",
         "timestamp": "2026-09-03T10:00:00Z", "corrects_archived": "viejo"},
        {"command": "aisdd close change", "change_id": "nuevo", "id": "b",
         "timestamp": "2026-09-03T12:00:00Z"},
        # Uno retrasado con una senal que lo explica...
        {"command": "aisdd open change", "change_id": "lento", "id": "c",
         "timestamp": "2026-09-01T09:00:00Z",
         "decisions": [{"type": "bloqueante", "decision": "pendiente", "slug": "d1"}]},
        {"command": "aisdd close change", "change_id": "lento", "id": "d",
         "timestamp": "2026-09-10T18:00:00Z"},
        # ...y otro igual de retrasado sin ninguna, que es el hueco.
        {"command": "aisdd open change", "change_id": "mudo", "id": "e",
         "timestamp": "2026-09-01T09:00:00Z"},
        {"command": "aisdd close change", "change_id": "mudo", "id": "f",
         "timestamp": "2026-09-09T18:00:00Z"},
    ]
    (d / "openspec" / "audit" / "2026-09" / "dev.jsonl").write_text(
        "\n".join(json.dumps(e) for e in entradas) + "\n", encoding="utf-8")


with tempfile.TemporaryDirectory() as tmp:
    d = Path(tmp)
    proyecto(d)

    # 1. `aiba metrics`: el informe completo, que es donde estaba el fallo.
    r = subprocess.run([sys.executable, str(KPIS), "--audit", "openspec/audit",
                        "--no-git", "--format", "json"],
                       cwd=d, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        errors.append(f"compute_kpis.py falla al ejecutarse: {r.stderr.strip()[-400:]}")
    else:
        try:
            datos = json.loads(r.stdout)
        except json.JSONDecodeError as exc:
            errors.append(f"compute_kpis.py no devuelve JSON valido: {exc}")
        else:
            for clave in ("attended", "audit"):
                if clave not in datos:
                    errors.append(f"compute_kpis.py: falta la seccion '{clave}' en la salida")
            if datos.get("audit", {}).get("rework_total") != 1:
                errors.append("compute_kpis.py: no cuenta el retrabajo "
                              "(`corrects_archived`) que trae la auditoria de prueba")
            # La desviacion tiene que venir explicada, no desnuda. Sin PyYAML no
            # hay roadmap que leer y la seccion se declara no disponible: eso no
            # es un fallo, pero tiene que decir por que.
            at = datos.get("attribution")
            if at is None:
                errors.append("compute_kpis.py: falta la seccion 'attribution': la "
                              "desviacion vuelve a salir como una cifra sin explicar")
            elif at.get("available"):
                ag = at.get("agregado", {})
                causas = [c["senal"] for c in ag.get("retraso", {}).get("por_causa", [])]
                if "decisiones bloqueantes sin resolver" not in causas:
                    errors.append("compute_kpis.py: la atribucion agregada no recoge la "
                                  f"causa del change retrasado ({causas})")
                if not ag.get("retraso", {}).get("changes_sin_senal"):
                    errors.append("compute_kpis.py: el change retrasado sin senal no "
                                  "sale como hueco; un hueco callado se lee como "
                                  "explicado")
            elif not at.get("reason"):
                errors.append("compute_kpis.py: la atribucion no esta disponible y "
                              "tampoco dice por que")

    # 2. Y el formato humano, que recorre otro camino del codigo.
    r = subprocess.run([sys.executable, str(KPIS), "--audit", "openspec/audit",
                        "--no-git", "--format", "md"],
                       cwd=d, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        errors.append(f"compute_kpis.py --format md falla: {r.stderr.strip()[-400:]}")

    # 3. `audit.py`: escribir una entrada de punta a punta.
    r = subprocess.run([sys.executable, str(AUDIT), "--root", str(d)],
                       input=json.dumps({"command": "aisdd init",
                                         "started_at": "2026-09-03T10:00:00Z"}),
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        errors.append(f"audit.py falla al ejecutarse: {r.stderr.strip()[-400:]}")

    # 4. `aiba functional-design`: genera el .docx, con plantilla y sin ella.
    #    Necesita python-docx; si no esta, se **dice** y no se finge cobertura.
    df_ejercitado = False
    try:
        import docx                                            # noqa: F401,PLC0415
    except ImportError:
        pass
    else:
        df_ejercitado = True
        # El manifiesto lleva sembrado lo que las cuatro reglas del generador
        # tienen que cazar: un codigo interno, un autor que es la herramienta y
        # un pendiente que debe salir resaltado.
        manifiesto = {"proyecto": "P", "titulo": "T",
                      "introduccion": "Cubre el RF-014 del catalogo.",
                      "autor": "aiba-functional-design",
                      # Un hueco escrito en prosa, como lo redacta un modelo que no
                      # usa el marcador literal. Tiene que resaltarse igual.
                      "alcance": "El plazo maximo esta pendiente de definir.",
                      "narrativa": {"como": "a", "quiero": "b", "para": "c"},
                      "integraciones": "N/A",
                      "validaciones": {"frontal": "N/A", "core": "N/A"},
                      "mensajes": ["- Aviso de NIF incorrecto"],
                      "pantallas": "[PENDIENTE: insertar la pantalla de Figma]",
                      # Lo que se enumera sale como vineta, no como parrafo corrido.
                      "especificaciones_tecnicas": ["- Node 20", "- PostgreSQL 15"],
                      # `campos` como lista de diccionarios y `mensajes` como
                      # lista: dos formas que salen de un modelo mas flojo y que
                      # antes reventaban la generacion entera.
                      "campos": [{"nombre": "Ramo", "tipo": "Lista"},
                                 {"nombre": "NIF", "tipo": "Texto"}]}
        (d / "m.json").write_text(json.dumps(manifiesto), encoding="utf-8")

        # Plantilla como la de un cliente: estilo en espanol, relleno, y una
        # cabecera con logo y un pie propios. El logo es lo que se perdia: el
        # generador escribia con `p.text = ...`, que borra los runs del parrafo
        # y con ellos el `w:drawing`, y el DF salia sin la marca del cliente.
        import struct, zlib, binascii                          # noqa: PLC0415
        def _chunk(t, data):
            c = t + data
            return struct.pack(">I", len(data)) + c + struct.pack(">I", binascii.crc32(c))
        crudo = b"".join(b"\x00" + b"\xff\x00\x00" * 4 for _ in range(4))
        (d / "logo.png").write_bytes(
            b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", struct.pack(">IIBBBBB", 4, 4, 8, 2, 0, 0, 0))
            + _chunk(b"IDAT", zlib.compress(crudo)) + _chunk(b"IEND", b""))

        import docx as _docx                                   # noqa: PLC0415
        from docx.oxml.ns import qn as _qn                     # noqa: PLC0415
        from docx.shared import Cm                             # noqa: PLC0415
        tpl = _docx.Document()
        tpl.add_paragraph("RELLENO DE LA PLANTILLA")
        tpl.styles["Heading 1"].name = "Título 1"
        cab = tpl.sections[0].header.paragraphs[0]
        cab.add_run().add_picture(str(d / "logo.png"), height=Cm(1))
        cab.add_run("CABECERA DEL CLIENTE")
        tpl.sections[0].footer.paragraphs[0].text = "PIE DEL CLIENTE"
        tpl.save(str(d / "tpl.docx"))

        # Plantilla-esqueleto: el DF entero ya montado, que es lo que trae un
        # cliente de verdad. Portada con logo en el cuerpo, tablas propias y
        # texto de ejemplo. El generador tiene que escribir DENTRO y no arrasar.
        esq = _docx.Document()
        # Portada distinta y el logo **solo** ahi, que es como vienen: sin
        # propagarla, el logo sale en la primera pagina y en ninguna mas.
        esq.sections[0].different_first_page_header_footer = True
        cab_e = esq.sections[0].first_page_header.paragraphs[0]
        cab_e.add_run().add_picture(str(d / "logo.png"), height=Cm(1))
        cab_e.add_run("CABECERA DEL CLIENTE")
        # El nombre del documento, partido en dos runs como lo parte Word al
        # editarlo: sustituirlo run a run no vale, hay que mirar el parrafo.
        cab_e.add_run("  |  Diseño Funcional ")
        cab_e.add_run("de Ejemplo")
        esq.sections[0].footer.paragraphs[0].text = "PIE DEL CLIENTE"
        esq.add_paragraph().add_run().add_picture(str(d / "logo.png"), height=Cm(2))
        # La portada de una plantilla corporativa suele ser **una tabla**, no un
        # parrafo con estilo `Title`: buscando solo por estilo no se encuentra
        # nada y el titulo de ejemplo se entrega tal cual.
        port = esq.add_table(rows=3, cols=2)
        port.style = "Table Grid"
        port.rows[0].cells[0].text = "Título del documento:"
        port.rows[0].cells[1].text = "Diseño Funcional de Ejemplo"
        port.rows[1].cells[0].text = "Versión:"
        port.rows[1].cells[1].text = "0.1"
        port.rows[2].cells[0].text = "Fecha:"
        port.rows[2].cells[1].text = "01/01/2020"
        esq.add_paragraph("Control de Versiones")
        esq.add_table(rows=1, cols=4).style = "Table Grid"
        for t_, n_ in (("Introducción", 1), ("Alcance", 2), ("Filtros/Campos", 2),
                       ("Criterios de aceptación", 1), ("Puntos abiertos", 1)):
            esq.add_paragraph(t_, style=f"Heading {n_}")
            esq.add_paragraph("TEXTO DE EJEMPLO DE LA PLANTILLA")
        # Un apartado del cliente que el DF no conoce, con relleno sin sustituir.
        esq.add_paragraph("Anexo del cliente", style="Heading 1")
        _relleno = esq.add_paragraph("<RELLENAR CON LO QUE PROCEDA>")
        # Comentarios de Word como los que trae una plantilla que alguien estuvo
        # editando. Son notas de aquel momento y no contenido del DF.
        esq.add_comment(_relleno.runs, "Revisar con negocio antes de entregar",
                        author="Plantilla", initials="PL")
        esq.save(str(d / "esq.docx"))

        # Plantilla sin ningun estilo de vineta, que es lo normal en cliente:
        # Word solo deja en el documento los estilos que alguien ha usado, y
        # `Parrafo de lista` sobrevive --lo aplica cualquier lista-- mientras
        # que `Lista con viñetas` no. El DF tiene que salir con vinetas igual.
        sinv = _docx.Document()
        for _n in ("List Bullet", "List Bullet 2", "List Bullet 3"):
            _e = sinv.styles[_n]._element
            _e.getparent().remove(_e)
        sinv.styles["List Paragraph"]._element.find(
            _qn("w:name")).set(_qn("w:val"), "Párrafo de lista")
        sinv.add_paragraph("PLANTILLA SIN ESTILO DE VIÑETA")
        sinv.save(str(d / "sinvin.docx"))

        # El indice de la plantilla, que es lo que el pre-flight ensena para
        # poder preguntar que dejar en blanco. Sin numeros no se puede preguntar.
        r_idx = subprocess.run([sys.executable, str(DF), "--indice", str(d / "esq.docx"),
                                "--no-install"], capture_output=True, text=True,
                               timeout=120)
        if r_idx.returncode != 0:
            errors.append(f"gen_df_docx.py --indice falla: {r_idx.stderr.strip()[:160]}")
        else:
            idx = json.loads(r_idx.stdout)
            numeros = [a["numero"] for a in idx["apartados"]]
            if not numeros or not any("." in n_ for n_ in numeros):
                errors.append("gen_df_docx.py --indice no numera los apartados de "
                              f"segundo nivel ({numeros}): el pre-flight pregunta por "
                              "numero, asi que sin ellos no se puede preguntar")
            if not any(a["apartado"] == "campos" for a in idx["apartados"]):
                errors.append("gen_df_docx.py --indice no reconoce Filtros/Campos "
                              "entre los apartados de la plantilla")

            # Y dejarlo en blanco por numero tiene que dejarlo en blanco.
            n_campos = next(a["numero"] for a in idx["apartados"]
                            if a["apartado"] == "campos")
            m_blanco = json.loads((d / "m.json").read_text(encoding="utf-8"))
            m_blanco["secciones_en_blanco"] = [n_campos]
            (d / "m-blanco.json").write_text(json.dumps(m_blanco, ensure_ascii=False),
                                             encoding="utf-8")
            r_b = subprocess.run([sys.executable, str(DF), "--manifest",
                                  str(d / "m-blanco.json"), "--output",
                                  str(d / "df-blanco.docx"), "--plantilla",
                                  str(d / "esq.docx"), "--no-install"],
                                 capture_output=True, text=True, timeout=120)
            if r_b.returncode != 0:
                errors.append(f"gen_df_docx.py con secciones_en_blanco falla: "
                              f"{r_b.stderr.strip()[:160]}")
            else:
                if "campos" not in json.loads(r_b.stdout).get("secciones_en_blanco", []):
                    errors.append("gen_df_docx.py: pedir en blanco el apartado "
                                  f"{n_campos} no lo deja en blanco")
                d_b = _docx.Document(str(d / "df-blanco.docx"))
                if any("Ramo" in c_.text for t_ in d_b.tables for f_ in t_.rows
                       for c_ in f_.cells):
                    errors.append("gen_df_docx.py: el apartado pedido en blanco se "
                                  "rellena igual")

            # Y un apartado **propio del cliente**, que el DF no reconoce, tiene
            # que poder dejarse en blanco igual: se identifica por su numero.
            propio = next((a for a in idx["apartados"] if not a["apartado"]
                           and a["nivel"] == 1), None)
            if propio is None:
                errors.append("el esqueleto de prueba ya no trae ningun apartado "
                              "propio del cliente: la comprobacion de dejarlo en "
                              "blanco no prueba nada")
            else:
                m_p = json.loads((d / "m.json").read_text(encoding="utf-8"))
                m_p["secciones_en_blanco"] = [propio["numero"]]
                (d / "m-propio.json").write_text(json.dumps(m_p, ensure_ascii=False),
                                                 encoding="utf-8")
                r_p = subprocess.run([sys.executable, str(DF), "--manifest",
                                      str(d / "m-propio.json"), "--output",
                                      str(d / "df-propio.docx"), "--plantilla",
                                      str(d / "esq.docx"), "--no-install"],
                                     capture_output=True, text=True, timeout=120)
                if r_p.returncode != 0:
                    errors.append(f"gen_df_docx.py en blanco un apartado propio falla: "
                                  f"{r_p.stderr.strip()[:160]}")
                elif not json.loads(r_p.stdout).get("secciones_en_blanco"):
                    errors.append("gen_df_docx.py: pedir en blanco un apartado propio "
                                  f"del cliente ({propio['numero']} "
                                  f"{propio['titulo']}) no hace nada y no avisa")

        for etiqueta, extra in (("sin plantilla", []),
                                ("con plantilla", ["--plantilla", str(d / "tpl.docx")]),
                                ("con esqueleto", ["--plantilla", str(d / "esq.docx")]),
                                ("sin estilo de vineta",
                                 ["--plantilla", str(d / "sinvin.docx")])):
            salida = d / f"df-{etiqueta.split()[0]}.docx"
            r = subprocess.run([sys.executable, str(DF), "--manifest", str(d / "m.json"),
                                "--output", str(salida), "--no-install"] + extra,
                               capture_output=True, text=True, timeout=120)
            if r.returncode != 0:
                errors.append(f"gen_df_docx.py falla {etiqueta}: {r.stderr.strip()[-300:]}")
                continue
            try:
                salida_json = json.loads(r.stdout)
            except json.JSONDecodeError:
                errors.append(f"gen_df_docx.py {etiqueta}: la salida no es JSON")
                salida_json = {}
            doc = _docx.Document(str(salida))
            titulos = [p.text for p in doc.paragraphs
                       if p.style.name in ("Heading 1", "Título 1")]
            # En modo esqueleto los titulos --y su numeracion-- son de la
            # plantilla: el generador no los escribe y no le toca numerarlos.
            if etiqueta != "con esqueleto" and not any(x.startswith("1. ") for x in titulos):
                errors.append(f"gen_df_docx.py {etiqueta}: los apartados no salen "
                              f"numerados ({titulos[:3]})")
            errors.extend(_revisar_df(doc, salida_json, etiqueta))

            if "con esqueleto" in etiqueta:
                from docx.oxml.ns import qn                     # noqa: PLC0415
                if salida_json.get("modo") != "esqueleto":
                    errors.append("gen_df_docx.py: con una plantilla que trae los "
                                  "apartados del DF no entra en modo esqueleto y "
                                  "rehace el cuerpo, perdiendo portada y logo")
                if any("TEXTO DE EJEMPLO" in p.text for p in doc.paragraphs):
                    errors.append("gen_df_docx.py esqueleto: queda texto de ejemplo "
                                  "de la plantilla dentro de los apartados")
                if not doc.element.body.findall(".//" + qn("w:drawing")):
                    errors.append("gen_df_docx.py esqueleto: se pierde el logo de la "
                                  "portada; el cuerpo de la plantilla no se toca")
                errors.extend(_revisar_plantilla(doc, etiqueta))

            if etiqueta == "con plantilla":
                if any("RELLENO DE LA PLANTILLA" in p.text for p in doc.paragraphs):
                    errors.append("gen_df_docx.py: el contenido de ejemplo de la "
                                  "plantilla acaba dentro del DF")
                errors.extend(_revisar_plantilla(doc, etiqueta))

# 5. `aiba onboarding`: los hechos y el documento, sin OpenSpec, con el y en un
#    proyecto vacio. Lo cuantitativo sale del script para que el onboarding no
#    dependa del modelo que lo redacte: si el script falla, falla todo lo demas.
ONB = ROOT / "plugins/aiba/skills/aiba-onboarding/scripts/compute_onboarding.py"
with tempfile.TemporaryDirectory() as tmp_onb:
    o = Path(tmp_onb)
    (o / "docs").mkdir()
    (o / "docs" / "sprint-plan.md").write_text(
        "# Plan de sprints\n\n## 4. Distribucion en sprints\n\n"
        "### Sprint 1 — (25/08/2026 a 05/09/2026)\n\nObjetivo: alta. Unidades: HU-01.\n\n"
        # Una mencion de pasada: no puede llevarse HU-02 al Sprint 1.
        "Deja preparada la base que necesitara HU-02.\n\n"
        "### Sprint 2 — (08/09/2026 a 19/09/2026)\n\n"
        "Objetivo: suplementos. Unidades: HU-02.\n\n"
        # Una historia nombrada fuera de los sprints: no puede colarse en el ultimo.
        "## 5. Hitos\n\n- El MVP necesita HU-03 cerrada\n", encoding="utf-8")
    (o / "docs" / "mapa-historias-usuario.md").write_text(
        "# Mapa\n\n## 3. Historias por fase\n\n### F1 — Alta\n\n"
        "| ID | Historia | RF | MoSCoW |\n|---|---|---|---|\n"
        "| HU-01 | Como gestor, quiero dar de alta una poliza para cubrir | RF-01 | Must |\n"
        "| HU-02 | Como gestor, quiero anadir un suplemento para ampliar | RF-02 | Must |\n"
        "| HU-03 | Como gestor, quiero dar de baja para cerrar | RF-03 | Should |\n",
        encoding="utf-8")
    (o / "docs" / "plan-revision-hu.json").write_text(json.dumps({"hus": [
        {"id": "HU-01", "estado": "Cerrada"}, {"id": "HU-02", "estado": "Cerrada"},
        {"id": "HU-03", "estado": "En revision", "bloqueada": True}]}), encoding="utf-8")

    def onb(*extra, dest="h.json"):
        return subprocess.run([sys.executable, str(ONB), "--root", str(o), "--out",
                               str(o / dest), "--hoy", "2026-09-11", *extra],
                              capture_output=True, text=True, timeout=120)

    r = onb()
    if r.returncode != 0:
        errors.append(f"compute_onboarding.py falla al calcular: {r.stderr.strip()[-300:]}")
    else:
        h = json.loads((o / "h.json").read_text(encoding="utf-8"))
        s1 = next((x for x in h["sprints"]["lista"] if x["nombre"] == "Sprint 1"), {})
        s2 = next((x for x in h["sprints"]["lista"] if x["nombre"] == "Sprint 2"), {})
        if s1.get("hus") != ["HU-01"]:
            errors.append("compute_onboarding.py asigna a un sprint una historia que solo "
                          f"nombra de pasada ({s1.get('hus')}); iba al Sprint 2")
        if h["sprints"]["actual"] != "Sprint 2":
            errors.append("compute_onboarding.py no reconoce el sprint en curso "
                          f"({h['sprints']['actual']})")
        if s2.get("hus") != ["HU-02"]:
            # Puede fallar por los dos lados --que se le cuele la seccion siguiente
            # del plan o que otro sprint se lleve la suya--, y el mensaje no puede
            # afirmar uno de los dos sin saber cual ha sido.
            errors.append("compute_onboarding.py: el Sprint 2 no se queda exactamente con "
                          f"las historias que declara ({s2.get('hus')}, esperaba ['HU-02'])")
        if "Unidades" in s2.get("objetivo", ""):
            errors.append("compute_onboarding.py: el objetivo del sprint arrastra el resto "
                          f"de la linea ({s2.get('objetivo')!r})")
        if h["resumen"]["total"] != 3 or h["resumen"]["bloqueadas"] != ["HU-03"]:
            errors.append("compute_onboarding.py: cuenta mal las historias o las "
                          f"bloqueadas ({h['resumen']})")
        if h["resumen"]["construidas"] is not None:
            errors.append("compute_onboarding.py: sin OpenSpec afirma cuantas historias "
                          "estan construidas; eso no lo sabe")
        if "docs/cliente-requisitos.md" not in {f["ruta"] for f in h["fuentes"]
                                                if not f["existe"]}:
            errors.append("compute_onboarding.py: no declara el brief como fuente que falta")

        r = subprocess.run([sys.executable, str(ONB), "--render", str(o / "h.json"),
                            "--output", str(o / "docs" / "onboarding.md")],
                           capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            errors.append(f"compute_onboarding.py falla al escribir: {r.stderr.strip()[-300:]}")
        else:
            md = (o / "docs" / "onboarding.md").read_text(encoding="utf-8")
            for esperado, motivo in (
                    ("## 7. Lo que falta", "no escribe la seccion de huecos"),
                    ("[PENDIENTE", "no marca como pendiente la narrativa que falta"),
                    ("(bloqueada)", "no senala las historias bloqueadas"),
                    ("2 cerradas", "no concuerda en plural el estado de revision"),
                    ("en revisión", "pinta el estado de revision sin tilde")):
                if esperado not in md:
                    errors.append(f"compute_onboarding.py: el documento {motivo}")

    # Con OpenSpec: lo construido sale del estado que da compute_status.py.
    (o / "estado.json").write_text(json.dumps({
        "topology": "externalizado", "modo_faseado": "atomic",
        "avance": {"hus": {"ids_ok": ["HU-02"], "ids_en_curso": [],
                           "ids_todas": ["HU-01", "HU-02", "HU-03"]}}}), encoding="utf-8")
    r = onb("--estado", str(o / "estado.json"), dest="h2.json")
    if r.returncode != 0:
        errors.append(f"compute_onboarding.py con --estado falla: {r.stderr.strip()[-300:]}")
    else:
        h2 = json.loads((o / "h2.json").read_text(encoding="utf-8"))
        if h2["resumen"]["construidas"] != 1:
            errors.append("compute_onboarding.py no cuenta lo construido desde OpenSpec "
                          f"({h2['resumen']['construidas']})")
        if not h2["openspec"].get("donde_se_ejecuta"):
            errors.append("compute_onboarding.py: en topologia externalizado no dice desde "
                          "donde se ejecuta cada comando, que es lo primero que se pregunta")
        # HU-01 estaba en un sprint cerrado y no esta construida: la unica senal de
        # desfase que cabe en una vision global.
        if h2["resumen"]["planificadas_sin_construir"] != ["HU-01"]:
            errors.append("compute_onboarding.py no senala lo planificado en sprints "
                          "cerrados y sin construir "
                          f"({h2['resumen']['planificadas_sin_construir']})")
        r = subprocess.run([sys.executable, str(ONB), "--render", str(o / "h2.json"),
                            "--output", str(o / "o2.md")],
                           capture_output=True, text=True, timeout=120)
        md2 = (o / "o2.md").read_text(encoding="utf-8") if r.returncode == 0 else ""
        queda = md2.split("## 5.")[1].split("## 6.")[0] if "## 5." in md2 else ""
        if "HU-01" not in queda:
            errors.append("compute_onboarding.py: 'Que queda' pierde las historias de "
                          "sprints cerrados que no estan construidas, justo lo mas urgente")

    # Un --estado que no existe --el modelo lo pasa aunque se salte el paso 1-- no
    # puede tumbar el comando: se sigue sin OpenSpec y se dice.
    r = onb("--estado", str(o / "no-existe.json"), dest="h3.json")
    if r.returncode != 0 or "no existe" not in r.stderr:
        errors.append("compute_onboarding.py con un --estado inexistente revienta o calla "
                      f"(salida {r.returncode})")

# Y un proyecto sin ningun documento: el onboarding sale y dice que falta todo.
with tempfile.TemporaryDirectory() as tmp_vacio:
    v = Path(tmp_vacio)
    r = subprocess.run([sys.executable, str(ONB), "--root", str(v), "--out",
                        str(v / "h.json"), "--hoy", "2026-09-11"],
                       capture_output=True, text=True, timeout=120)
    r2 = subprocess.run([sys.executable, str(ONB), "--render", str(v / "h.json"),
                         "--output", str(v / "onboarding.md")],
                        capture_output=True, text=True, timeout=120) if r.returncode == 0 else r
    if r.returncode != 0 or r2.returncode != 0:
        errors.append("compute_onboarding.py revienta en un proyecto sin documentos")
    else:
        md = (v / "onboarding.md").read_text(encoding="utf-8")
        if "| # | Documento |" in md:
            errors.append("compute_onboarding.py: sin documentos escribe una tabla de "
                          "lectura vacia, que se lee como un fallo")
        if "No queda ninguna historia pendiente" in md:
            errors.append("compute_onboarding.py: sin historias dice que no queda nada, "
                          "cuando lo que pasa es que no hay nada definido")

# 6. `aiba handover`: el cuestionario, los hechos, el documento y la regla de los
#    secretos. Lo operativo sale del cuestionario y lo que falta, como hueco; y si
#    algo tiene pinta de secreto el script se niega, dice donde y no lo repite.
HAN = ROOT / "plugins/aiba/skills/aiba-handover/scripts/compute_handover.py"


def han(*extra):
    return subprocess.run([sys.executable, str(HAN), *extra],
                          capture_output=True, text=True, timeout=120)


with tempfile.TemporaryDirectory() as tmp_han:
    t = Path(tmp_han)

    def w(rel: str, texto: str) -> None:
        f = t / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(texto, encoding="utf-8")

    w("docs/arquitectura-base.md",
      "# Arquitectura\n\n## 3. Estructura\n\n### Repositorios\n\n| id | Contiene |\n"
      "|---|---|\n| `front` | SPA |\n| `api` | Servicios |\n\n"
      "## 10. Integracion con APIs y servicios externos\n\n| Servicio | Uso |\n"
      "|---|---|\n| Redsys | Cobro |\n")
    w("docs/planificacion-proyecto.md",
      "# Plan\n\n## 2. Perfiles y equipo recomendado\n\n| Perfil | Dedicacion |\n"
      "|---|---|\n| Backend | 100 % |\n\n## 4. Infraestructura y entornos\n\n"
      "Dev, pre y pro en Azure.\n")
    w("openspec/specs/polizas/spec.md", "## Purpose\n\nAlta y baja de polizas.\n\n"
      "## Requirements\n\n### Requirement: Alta\n\n### Requirement: Baja\n")
    w("openspec/changes/archive/2026-09-01-alta/specs/polizas/spec.md", "x")
    w("openspec/changes/archive/2026-09-01-alta/decisions.md",
      "## baja-logica\n\n- **Tipo**: correccion\n- **Decision**: la baja es logica\n"
      "- **Justificacion**: lo exige el regulador\n")
    w("openspec/changes/archive/2026-09-05-cobro/specs/pagos/spec.md", "x")

    def aud(i: str, cmd: str, cid: str) -> str:
        return json.dumps({"id": i, "command": cmd, "change_id": cid,
                           "timestamp": "2026-09-05T10:00:00Z"})

    # `polizas` la conoce solo ana; `pagos`, ana y luis.
    w("openspec/audit/2026-09/ana.jsonl", aud("1", "aisdd close change", "alta") + "\n"
      + aud("2", "aisdd implement change", "cobro") + "\n")
    w("openspec/audit/2026-09/luis.jsonl", aud("3", "aisdd close change", "cobro") + "\n")
    cuest = t / "docs" / "traspaso-cuestionario.md"

    r = han("--root", str(t), "--preparar")
    if r.returncode != 0 or not cuest.is_file():
        errors.append(f"compute_handover.py --preparar falla: {r.stderr.strip()[-300:]}")
    else:
        base = cuest.read_text(encoding="utf-8")
        # Lo que ya se sabe no se pregunta: los repositorios y las integraciones
        # de la arquitectura, y quien aparece en la auditoria.
        for fila in ("| front |", "| api |", "| Redsys |", "| ana |", "| luis |"):
            if fila not in base:
                errors.append(f"compute_handover.py --preparar no precarga «{fila}»")
        han("--root", str(t), "--preparar")
        if cuest.read_text(encoding="utf-8") != base:
            errors.append("compute_handover.py --preparar reescribe un cuestionario que ya "
                          "existe; tiene que respetar lo contestado")
        # Contestado como lo haria un equipo, con cosas que parecen secretos y no lo
        # son: el tamano de una VM, la ruta de un secreto en su gestor, una URL.
        relleno = (base
                   .replace("| front |  |  |  |  |", "| front | App Service | P1v3 | api | Sistemas |")
                   .replace("| api |  |  |  |  |", "| api | AKS Standard_D2s_v3 | 3 nodos | BD, Redsys |  |")
                   .replace("| Producción |  |  |  |",
                            "| Producción | https://polizas.cliente.es | real | Sistemas |"))
        relleno = re.sub(r"(<!-- id: almacenes -->.*?\|---\|---\|---\|---\|\n)\|  \|  \|  \|  \|",
                         r"\1| BD | Azure SQL | diaria | nunca |", relleno, flags=re.S)
        relleno = re.sub(r"(<!-- id: secretos -->.*?\|---\|---\|---\|\n)\|  \|  \|  \|",
                         r"\1| Contraseña de la BD | Key Vault, kv-prod/db-password | Sistemas |",
                         relleno, flags=re.S)
        cuest.write_text(relleno, encoding="utf-8")
        r = han("--root", str(t), "--out", str(t / "h.json"), "--hoy", "2026-09-11")
        if r.returncode != 0:
            errors.append("compute_handover.py se niega con contenido que parece un secreto "
                          f"y no lo es: {r.stderr.strip()[-300:]}")
        else:
            h = json.loads((t / "h.json").read_text(encoding="utf-8"))
            riesgos = " ".join(h["riesgos"])
            for trozo, motivo in (
                    ("restaurar «BD»", "la restauracion que nunca se ha probado"),
                    ("administra «api»", "el componente que no administra nadie"),
                    ("«polizas» la ha construido solo ana",
                     "la capacidad que solo conoce una persona")):
                if trozo not in riesgos:
                    errors.append(f"compute_handover.py no senala como riesgo {motivo} "
                                  f"({h['riesgos']})")
            if "«pagos»" in riesgos:
                errors.append("compute_handover.py marca como de una sola persona una "
                              "capacidad que conocen dos")
            mer = h["despliegue"].get("mermaid") or ""
            if "-->" not in mer or "Redsys" not in mer:
                errors.append("compute_handover.py no dibuja el despliegue con las "
                              "conexiones de la tabla de componentes")
            if h["cuestionario"]["contestadas"] != 4:
                errors.append("compute_handover.py cuenta mal las preguntas contestadas "
                              f"({h['cuestionario']['contestadas']}, esperaba 4)")

            # Lo que anade el skill: un diagrama de datos que no lo es y un perfil
            # sin dedicacion. Ninguno de los dos puede pasar como si nada.
            h["narrativa"] = {"que_es": "Gestiona polizas.", "como_esta_construido": "Dos repos."}
            h["diagramas"] = {"contexto": "flowchart LR\n  A --> B", "datos": "graph TD\n  A --> B"}
            h["equipo"] = {"perfiles": [{"perfil": "Backend", "dedicacion": "30 %"},
                                        {"perfil": "Soporte", "dedicacion": "a demanda"}],
                           "diferencias": ["Sobra UX."]}
            (t / "h.json").write_text(json.dumps(h, ensure_ascii=False), encoding="utf-8")
            r = han("--render", str(t / "h.json"), "--output", str(t / "docs" / "traspaso.md"))
            if r.returncode != 0:
                errors.append(f"compute_handover.py falla al escribir: {r.stderr.strip()[-300:]}")
            else:
                md = (t / "docs" / "traspaso.md").read_text(encoding="utf-8")
                if not md.split("\n## ")[1].startswith("1. Lo que hay que resolver"):
                    errors.append("compute_handover.py: el documento no empieza por lo que "
                                  "hay que resolver antes de cerrar el traspaso")
                for esperado, motivo in (
                        ("(14 de 18", "no cuenta lo que queda sin contestar"),
                        ("> **Hueco:** «Cómo se vuelve atrás»",
                         "no declara como hueco la vuelta atras sin contestar"),
                        ("```mermaid\nflowchart LR\n  subgraph",
                         "no incluye el diagrama de despliegue"),
                        ("[PENDIENTE: dedicación en %]",
                         "no marca el perfil sin dedicacion, que no se puede presupuestar"),
                        ("falta el diagrama del modelo de datos",
                         "no declara el hueco del diagrama que ha descartado"),
                        ("| polizas | Alta y baja de polizas. | 2 |",
                         "no cuenta las capacidades de las specs y sus requisitos"),
                        ("| alta | correccion | la baja es logica |",
                         "pierde las decisiones del archivo de changes")):
                    if esperado not in md:
                        errors.append(f"compute_handover.py: el documento {motivo}")
                if "graph TD" in md:
                    errors.append("compute_handover.py incluye como modelo de datos un "
                                  "diagrama que no lo es")

            # Un secreto en lo que escribe el skill: el documento no se escribe, y
            # el aviso dice en que clave del JSON esta sin repetirlo.
            h["narrativa"]["que_es"] = "Conecta con postgres://app:Sup3rS3creta@db:5432/polizas"
            (t / "h3.json").write_text(json.dumps(h, ensure_ascii=False), encoding="utf-8")
            r = han("--render", str(t / "h3.json"), "--output", str(t / "otro.md"))
            if r.returncode != 2 or (t / "otro.md").exists():
                errors.append("compute_handover.py escribe un documento con una cadena de "
                              "conexion que lleva la contrasena")
            if "Sup3rS3creta" in r.stdout + r.stderr:
                errors.append("compute_handover.py repite el secreto que ha encontrado: lo "
                              "acaba de copiar a la terminal y al log")
            elif "narrativa.que_es" not in r.stderr:
                errors.append("compute_handover.py no dice en que clave del JSON esta el secreto")

        # Y un secreto en el cuestionario: no se lee, y el aviso dice la linea.
        cuest.write_text(relleno.replace("| Contraseña de la BD | Key Vault, kv-prod/db-password |",
                                         "| Contraseña de la BD | Pa55w0rd!Prod |"),
                         encoding="utf-8")
        r = han("--root", str(t), "--out", str(t / "h2.json"))
        if r.returncode != 2 or (t / "h2.json").exists():
            errors.append("compute_handover.py lee un cuestionario con una contrasena y sigue")
        if "Pa55w0rd" in r.stdout + r.stderr:
            errors.append("compute_handover.py repite la contrasena que ha encontrado en el "
                          "cuestionario")
        elif "traspaso-cuestionario.md:" not in r.stderr:
            errors.append("compute_handover.py no dice en que linea del cuestionario esta el "
                          "secreto")

# Y un proyecto sin nada: el traspaso sale, y dice que falta todo.
with tempfile.TemporaryDirectory() as tmp_hv:
    v = Path(tmp_hv)
    r = han("--root", str(v), "--preparar")
    if r.returncode == 0:
        r = han("--root", str(v), "--out", str(v / "h.json"))
    if r.returncode == 0:
        r = han("--render", str(v / "h.json"), "--output", str(v / "t.md"))
    if r.returncode != 0:
        errors.append(f"compute_handover.py revienta en un proyecto sin documentos: "
                      f"{r.stderr.strip()[-300:]}")
    else:
        md = (v / "t.md").read_text(encoding="utf-8")
        if "(18 de 18" not in md or "Nada pendiente" in md:
            errors.append("compute_handover.py: en un proyecto sin nada no declara que "
                          "falta todo")

if errors:
    print("Scripts que compilan pero no funcionan:", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
# Decir que se ejercito y que no. Un "correcto" que oculta una parte sin
# ejecutar es el mismo fallo que esta comprobacion existe para cazar.
print("Humo de scripts correcto: compute_kpis (json y md), compute_onboarding "
      "(con y sin OpenSpec), compute_handover (cuestionario, documento y secretos) "
      "y audit.py se ejecutan "
      "de punta a punta sobre un proyecto minimo"
      + (", y gen_df_docx con plantilla y sin ella." if df_ejercitado
         else ". AVISO: gen_df_docx **no** se ha ejercitado (falta python-docx)."))
