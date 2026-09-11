#!/usr/bin/env python3
"""Lo que tiene pinta de secreto no sale en un documento.

Un documento de traspaso los atrae: contrasenas, tokens, cadenas de conexion,
claves de API. Se nombra **donde viven** --que gestor, que ruta, quien da
acceso-- y nunca el valor, porque el documento circula por correo, se sube a un
SharePoint y acaba en el portatil de gente que ya no esta en el proyecto.

Este modulo solo encuentra: devuelve la linea, el tipo y lo que hay **delante**
del valor, y el script que lo llama decide negarse a escribir. Nunca el valor,
ni un trozo: un detector que imprime el secreto que ha encontrado lo acaba de
copiar a la terminal, al log de la CI y a la conversacion con el modelo.

**Precision antes que exhaustividad.** Un detector que salta con
`Standard_D2s_v3` o con `kv-prod/db-password` se aprende a ignorar, y entonces
no sirve ni para lo que si caza. Por eso los formatos conocidos van por su forma
exacta, y lo generico --una etiqueta de contrasena seguida de un valor-- solo
salta si el valor parece una contrasena y no una referencia a donde vive.

Se importa como `sprints.py`: los scripts de los skills anaden
`parents[3] / "scripts"` al `sys.path`.
"""

from __future__ import annotations

import math
import re

# Formatos con forma propia: si aparece, es lo que parece.
FORMATOS = [
    ("clave privada", re.compile(r"-----BEGIN (?:[A-Z]+ )*PRIVATE KEY-----")),
    ("clave de acceso de AWS", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("token de GitHub",
     re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,})")),
    ("token de Atlassian", re.compile(r"\bATATT3[A-Za-z0-9_\-=]{20,}")),
    ("token de Slack", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("clave de API de Google", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}")),
    ("clave de API", re.compile(r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_\-]{20,}")),
    ("clave de Stripe", re.compile(r"\b[rs]k_(?:live|test)_[0-9A-Za-z]{16,}")),
    ("token JWT", re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}")),
]

# La palabra que anuncia un secreto. `secreto` antes que `secret`, y sin letras
# a los lados: `secretos:` o `tokens,` son titulos, no asignaciones.
ETIQUETA = (r"(?<![A-Za-z])(?:password|passwd|pwd|contrase(?:ñ|n)a|secreto|secret|token"
            r"|api[ _-]?key|client[ _-]?secret|access[ _-]?key)(?![A-Za-z])")

# Formatos que traen el valor en el grupo 1. `cualquiera`: todo valor que no
# sea una plantilla es un secreto --en una cadena de conexion no hay otra cosa
# que pueda ir detras de `Password=`--. `parece`: el valor tiene que parecer una
# contrasena, porque detras de `token:` tambien puede ir donde vive.
CON_VALOR = [
    ("cadena de conexión con contraseña",
     re.compile(r"\b[a-z][a-z0-9+.\-]{1,20}://[^\s/:@]+:([^\s/@]+)@", re.I), "cualquiera"),
    ("cadena de conexión con contraseña",
     re.compile(r"(?i)\b(?:server|data source|host|address)\s*=[^\n]*?;\s*(?:password|pwd)"
                r"\s*=\s*([^;\s\"']+)"), "cualquiera"),
    ("clave de cuenta de Azure",
     re.compile(r"(?i)\b(?:AccountKey|SharedAccessKey)\s*=\s*([A-Za-z0-9+/=%]{16,})"),
     "cualquiera"),
    ("token Bearer", re.compile(r"(?i)\bBearer\s+([A-Za-z0-9._~+/\-]{20,}=*)"), "cualquiera"),
    ("contraseña escrita tal cual",
     re.compile(ETIQUETA + r"[*_`]*[^\S\n]*[:=][^\S\n]*[\"'`]?([^\s\"'`;,|<>]{6,})", re.I),
     "parece"),
]

_PLANTILLA = re.compile(r"^(?:<.*>|\$\{.*\}|\$[A-Z_][A-Z0-9_]*|\{\{.*\}\}|%[^%]+%"
                        r"|[x*•·.\-_]{3,})$", re.I)
# Lo que se escribe en los ejemplos en lugar del valor: `https://user:password@host`.
_DE_EJEMPLO = {"password", "pass", "contraseña", "contrasena", "secret", "secreto",
               "token", "usuario", "user", "clave"}

_CANDIDATA = re.compile(r"(?<![A-Za-z0-9+/=_\-])[A-Za-z0-9+/=_\-]{32,}(?![A-Za-z0-9+/=_\-])")

CONSEJO = ("Un documento no lleva secretos: sustituye el valor por dónde vive —el gestor de "
           "secretos, la ruta y quién da acceso— y vuelve a lanzar el comando. Si el fichero "
           "ya estaba en git, borrarlo no basta: el valor sigue en el historial y hay que "
           "rotarlo. Si es un falso positivo —el nombre de algo, no su valor—, escríbelo con "
           "su ruta (gestor/ruta) y no saltará.")


def _es_plantilla(v: str) -> bool:
    v = v.strip().strip("\"'`")
    return not v or bool(_PLANTILLA.match(v)) or v.lower() in _DE_EJEMPLO


def _parece_contrasena(v: str) -> bool:
    if _es_plantilla(v):
        return False
    # Una ruta o una URL dicen donde vive, que es justo lo que se pide.
    if "/" in v or "\\" in v or ":" in v:
        return False
    letras = any(c.isalpha() for c in v)
    return letras and (any(c.isdigit() for c in v) or any(c in "!@#$%^&*+=?~" for c in v))


def _entropia(s: str) -> float:
    n = len(s)
    return -sum(k / n * math.log2(k / n) for k in (s.count(c) for c in set(s)))


def _parece_clave_larga(s: str) -> bool:
    # Hashes, commits y UUID son hexadecimales y no son secretos.
    if re.fullmatch(r"[0-9a-fA-F\-]+", s):
        return False
    if not (re.search(r"[a-z]", s) and re.search(r"[A-Z]", s) and re.search(r"\d", s)):
        return False
    # Un identificador son palabras unidas por `_` o `-`; una clave es un tramo
    # largo sin separadores. Sin esto saltaba con nombres de fichero y de test.
    if max(len(t) for t in re.split(r"[_\-]", s)) < 20:
        return False
    return _entropia(s) >= 4.3


def buscar(texto: str) -> list[dict]:
    """Cada cosa con pinta de secreto: linea, tipo y lo que la precede."""
    hallazgos: list[dict] = []
    for n, linea in enumerate(texto.splitlines(), 1):
        tramos: list[tuple[int, int]] = []

        def anota(tipo: str, ini: int, fin: int) -> None:
            # Un token de GitHub tambien es una cadena larga con entropia: se
            # cuenta una vez, con el tipo mas preciso, que es el que llega antes.
            if any(ini < b and a < fin for a, b in tramos):
                return
            tramos.append((ini, fin))
            delante = linea[max(0, ini - 30):ini].strip()
            donde = f"detrás de «{delante}»" if delante else "al principio de la línea"
            hallazgos.append({"linea": n, "tipo": tipo,
                              "muestra": f"{donde}, {fin - ini} caracteres"})

        for tipo, rx in FORMATOS:
            for m in rx.finditer(linea):
                anota(tipo, *m.span(0))
        for tipo, rx, criterio in CON_VALOR:
            for m in rx.finditer(linea):
                v = m.group(1)
                if _parece_contrasena(v) if criterio == "parece" else not _es_plantilla(v):
                    anota(tipo, *m.span(1))
        # En una tabla la etiqueta y el valor van en celdas contiguas:
        # `| Contrasena de la BD | P4ssw0rd! |`. Sin los dos puntos la regla
        # anterior no lo ve, y el cuestionario del traspaso es casi todo tablas.
        if linea.lstrip().startswith("|"):
            pos, celdas = 0, []
            for c in linea.split("|"):
                celdas.append((c, pos))
                pos += len(c) + 1
            for (a, _), (b, ib) in zip(celdas, celdas[1:]):
                v = b.strip()
                if (v and re.search(ETIQUETA, a, re.I) and " " not in v
                        and _parece_contrasena(v)):
                    ini = ib + b.index(v)
                    anota("contraseña en una tabla", ini, ini + len(v))
        for m in _CANDIDATA.finditer(linea):
            if _parece_clave_larga(m.group(0)):
                anota("cadena con pinta de clave", *m.span(0))
    return hallazgos


def informe(hallazgos: list[dict], origen: str) -> list[str]:
    return [f"{origen}:{h['linea']}: parece {h['tipo']} ({h['muestra']})" for h in hallazgos]
