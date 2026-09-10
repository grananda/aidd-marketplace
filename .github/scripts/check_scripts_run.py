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

- 2026-09-03T10:00:00Z | user:dev | skill:aisdd-specs | ctx:HU-01 | run | note:-
- 2026-09-03T10:01:00Z | user:dev | skill:aisdd-specs | ctx:HU-01 | file:src/a.ts | note:-
- 2026-09-03T10:05:00Z | user:dev | skill:aisdd-specs | ctx:HU-01 | turn | note:dur=300s skills=1 files=1
"""

errors: list[str] = []


def proyecto(d: Path) -> None:
    (d / "docs").mkdir()
    (d / "openspec" / "audit" / "2026-09").mkdir(parents=True)
    (d / "openspec" / "changes" / "archive" / "viejo").mkdir(parents=True)
    (d / "docs" / "aidd-activity.md").write_text(ACTIVIDAD, encoding="utf-8")
    entradas = [
        {"command": "aisdd open change", "change_id": "nuevo", "id": "a",
         "timestamp": "2026-09-03T10:00:00Z", "corrects_archived": "viejo"},
        {"command": "aisdd close change", "change_id": "nuevo", "id": "b",
         "timestamp": "2026-09-03T12:00:00Z"},
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
                      "alcance": "x", "narrativa": {"como": "a", "quiero": "b", "para": "c"},
                      "integraciones": "N/A",
                      "validaciones": {"frontal": "N/A", "core": "N/A"},
                      "mensajes": {"frontal": "N/A", "integracion_no_core": "N/A",
                                   "core": "N/A"},
                      "pantallas": "[PENDIENTE: insertar la pantalla de Figma]",
                      # Lo que se enumera sale como vineta, no como parrafo corrido.
                      "especificaciones_tecnicas": ["- Node 20", "- PostgreSQL 15"]}
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
        cab_e = esq.sections[0].header.paragraphs[0]
        cab_e.add_run().add_picture(str(d / "logo.png"), height=Cm(1))
        cab_e.add_run("CABECERA DEL CLIENTE")
        esq.sections[0].footer.paragraphs[0].text = "PIE DEL CLIENTE"
        esq.add_paragraph().add_run().add_picture(str(d / "logo.png"), height=Cm(2))
        esq.add_paragraph("Control de Versiones")
        esq.add_table(rows=1, cols=4).style = "Table Grid"
        for t_, n_ in (("Introducción", 1), ("Alcance", 2), ("Filtros/Campos", 2),
                       ("Criterios de aceptación", 1), ("Puntos abiertos", 1)):
            esq.add_paragraph(t_, style=f"Heading {n_}")
            esq.add_paragraph("TEXTO DE EJEMPLO DE LA PLANTILLA")
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

if errors:
    print("Scripts que compilan pero no funcionan:", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
# Decir que se ejercito y que no. Un "correcto" que oculta una parte sin
# ejecutar es el mismo fallo que esta comprobacion existe para cazar.
print("Humo de scripts correcto: compute_kpis (json y md) y audit.py se ejecutan "
      "de punta a punta sobre un proyecto minimo"
      + (", y gen_df_docx con plantilla y sin ella." if df_ejercitado
         else ". AVISO: gen_df_docx **no** se ha ejercitado (falta python-docx)."))
