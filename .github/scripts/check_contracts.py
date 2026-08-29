#!/usr/bin/env python3
"""Lo que un skill documenta coincide con lo que el script hace.

Un skill y el script que invoca son productor y consumidor de un formato, y el
formato vive en dos sitios a la vez: la prosa del skill y el codigo del script.
Nada los ata. Cuando divergen no falla la CI, falla el usuario, en su proyecto,
a mitad de un comando -- que es donde menos se puede diagnosticar.

Dos contratos, los dos comprobables sin ejecutar nada:

1. **La invocacion documentada y el argparse del script.** Cada flag que se
   escribe existe, cada flag `required=True` esta puesta y cada argumento
   posicional obligatorio tambien. Los tres sentidos importan: una flag
   inventada aborta el comando, y una obligatoria nueva deja obsoletas todas
   las invocaciones ya escritas sin tocar ninguna.

   Se comprueba **por invocacion**, no sobre la union de todas: que entre dos
   ejemplos esten todas las obligatorias no salva a ninguno de los dos.

   Cubre las dos fuentes de invocaciones. Las de los skills, ancladas a
   `${CLAUDE_PLUGIN_ROOT}` (o a `$env:` en PowerShell), que ejecuta el agente
   en casa del usuario; y las del README, relativas al repo, que ejecuta quien
   mantiene esto -- de una de ellas depende que los `.html` de metodologia se
   regeneren, asi que un flag renombrado ahi rompe otra comprobacion de la CI.

2. **El tipo de documento y su vista HTML.** `booster-docs` deduce el tipo por
   el nombre del fichero contra `DOC_TYPES`. Un documento sin entrada no falla:
   sale con la etiqueta y el dashboard genericos, que es una vista peor sin que
   nadie lo note. Paso justo eso con `kpis-ia`.
"""
from __future__ import annotations

import ast
import re
import shlex
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Invocacion anclada al plugin, la que ejecuta el agente. Las lineas continuadas
# con `\` van **antes** del resto en el patron: al reves, `[^\n]*` se come la
# barra final, la continuacion casa cero veces, el patron ya encaja y nada le
# obliga a retroceder -- se pierden todas las flags, que es justo donde estan.
# Las dos formas de la variable, como en check_plugin_assets.py: la de PowerShell
# escribe la ruta con barras invertidas y por ahi ya se colo una ruta obsoleta.
INV_PLUGIN = re.compile(
    r"(?:\$\{CLAUDE_PLUGIN_ROOT\}|\$env:CLAUDE_PLUGIN_ROOT)"
    r"[/\\]([A-Za-z0-9_./\\-]+\.py)\"?((?:[^\n]*\\\n)*[^\n]*)")
# Invocacion relativa al repo, la del README: la ejecuta quien mantiene esto.
INV_REPO = re.compile(
    r"\bpython3?\s+\"?(plugins/[A-Za-z0-9_./-]+\.py)\"?((?:[^\n]*\\\n)*[^\n]*)")

# Acciones de argparse que no consumen el token siguiente.
SIN_VALOR = {"store_true", "store_false", "store_const", "count", "help", "version"}
# nargs que hace opcional un posicional.
NARGS_OPCIONAL = {"?", "*"}

RENDER = ROOT / "plugins/boosters/skills/booster-docs/scripts/render_docs_html.py"
HTML_DECLARADO = re.compile(r"docs/html/([A-Za-z0-9._-]+)\.html")

# Vistas HTML que no las genera booster-docs, asi que no les toca DOC_TYPES.
SIN_DOC_TYPE = {
    "faseado-comparativa": "la genera optimize_phasing.py, no booster-docs",
}


class Firma:
    """Lo que el script acepta y lo que exige, leido del arbol sin ejecutarlo."""

    def __init__(self, script: Path):
        self.acepta: set[str] = set()
        self.exige: set[str] = set()
        self.con_valor: set[str] = set()
        self.posicionales: list[tuple[str, bool]] = []  # (nombre, obligatorio)
        self.valida = False
        try:
            arbol = ast.parse(script.read_text(encoding="utf-8"))
        except SyntaxError:
            return
        for n in ast.walk(arbol):
            if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr == "add_argument"):
                continue
            nombres = [a.value for a in n.args
                       if isinstance(a, ast.Constant) and isinstance(a.value, str)]
            if not nombres:
                continue
            kw = {k.arg: k.value for k in n.keywords}
            def const(clave):
                v = kw.get(clave)
                return v.value if isinstance(v, ast.Constant) else None
            if nombres[0].startswith("-"):
                self.acepta.update(nombres)
                largo = nombres[-1]
                if const("required") is True:
                    self.exige.add(largo)
                if const("action") not in SIN_VALOR:
                    self.con_valor.update(nombres)
            else:
                self.posicionales.append(
                    (nombres[0], const("nargs") not in NARGS_OPCIONAL))
        self.valida = bool(self.acepta or self.posicionales)

    @property
    def posicionales_obligatorios(self) -> int:
        return sum(1 for _, obligatorio in self.posicionales if obligatorio)


def tokens(cola: str) -> list[str] | None:
    """Los argumentos de una invocacion, sin continuaciones ni cola de shell."""
    linea = cola.replace("\\\n", " ")
    # Los marcadores `<algo>` van primero. Toda la documentacion escribe asi los
    # huecos (`<change-slug>`, `<marker>`, `<focus>`), y su `>` es indistinguible
    # de una redireccion: cortar por el se lleva por delante media invocacion y
    # deja el comando pareciendo que le faltan las flags que venian detras.
    linea = re.sub(r"<[^<>\s]*>", "_", linea)
    # Un comentario o un operador de shell terminan la invocacion; lo que venga
    # detras es otro comando, y contarlo inventaria argumentos que no existen.
    linea = re.split(r"\s+#|\||>|&&|;", linea)[0]
    try:
        return shlex.split(linea, posix=False)
    except ValueError:
        return None  # comillas sin cerrar: mejor callar que inventar un fallo


errores: list[str] = []
flags_vistas = 0
scripts_vistos: set[Path] = set()

fuentes: list[tuple[Path, re.Pattern, Path]] = []
for plugin_dir in sorted(ROOT.glob("plugins/*/")):
    for md in sorted(plugin_dir.rglob("*.md")):
        if "methodology" not in md.parts:
            fuentes.append((md, INV_PLUGIN, plugin_dir))
for md in sorted(ROOT.glob("*.md")):
    fuentes.append((md, INV_REPO, ROOT))

for md, patron, base in fuentes:
    for m in patron.finditer(md.read_text(encoding="utf-8", errors="replace")):
        script = base / m.group(1).replace("\\", "/")
        if not script.is_file():
            continue  # ruta rota: la reportan check_plugin_assets.py / check_skill_refs.py
        firma = Firma(script)
        if not firma.valida:
            continue  # el script no usa argparse; no hay contrato que comprobar
        args = tokens(m.group(2))
        if args is None:
            continue
        scripts_vistos.add(script)

        usadas: set[str] = set()
        posicionales = 0
        saltar = False
        for tok in args:
            if saltar:
                saltar = False
                continue
            if tok.startswith("-") and len(tok) > 1:
                nombre = tok.split("=", 1)[0]
                usadas.add(nombre)
                flags_vistas += 1
                if nombre not in firma.acepta:
                    errores.append(
                        f"{md.relative_to(ROOT)}: documenta `{nombre}` para {script.name}, "
                        f"que no la acepta (acepta: {', '.join(sorted(firma.acepta))})")
                elif "=" not in tok and nombre in firma.con_valor:
                    saltar = True
            else:
                posicionales += 1

        for f in sorted(firma.exige - usadas):
            errores.append(
                f"{md.relative_to(ROOT)}: invoca {script.name} sin `{f}`, que el script "
                f"exige (required=True): ese comando fallaria al ejecutarse")
        faltan = firma.posicionales_obligatorios - posicionales
        if faltan > 0:
            nombres = [n for n, ob in firma.posicionales if ob]
            errores.append(
                f"{md.relative_to(ROOT)}: invoca {script.name} con {posicionales} "
                f"argumento(s) posicional(es) y el script exige {len(nombres)} "
                f"({', '.join(nombres)}): ese comando fallaria al ejecutarse")


def literal_de(ruta: Path, nombre: str):
    for nodo in ast.parse(ruta.read_text(encoding="utf-8")).body:
        if isinstance(nodo, ast.Assign) and any(
                isinstance(d, ast.Name) and d.id == nombre for d in nodo.targets):
            return ast.literal_eval(nodo.value)
    return None


doc_types = literal_de(RENDER, "DOC_TYPES") if RENDER.is_file() else None
if doc_types is None:
    errores.append(f"{RENDER.relative_to(ROOT)}: no declara DOC_TYPES como literal de modulo")
else:
    claves = sorted(doc_types, key=len, reverse=True)  # el orden de detect_doc_type
    vistos: set[str] = set()
    for md in sorted(ROOT.glob("plugins/*/skills/*/**/*.md")):
        for m in HTML_DECLARADO.finditer(md.read_text(encoding="utf-8", errors="replace")):
            stem = m.group(1).lower()
            if stem in vistos or stem in SIN_DOC_TYPE:
                continue
            vistos.add(stem)
            if not any(k in stem for k in claves):
                errores.append(
                    f"{md.relative_to(ROOT)}: genera docs/html/{m.group(1)}.html, y "
                    f"DOC_TYPES no tiene entrada que case con '{stem}': saldria con la "
                    f"etiqueta y el dashboard genericos")

if errores:
    print("Contratos rotos entre lo documentado y lo implementado:", file=sys.stderr)
    for e in errores:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)
print(f"Contratos coherentes: {flags_vistas} flags documentadas existen en su script, "
      f"{len(scripts_vistos)} scripts con sus obligatorias --flags y posicionales-- "
      f"en cada invocacion, {len(doc_types or {})} tipos de documento con vista propia.")
