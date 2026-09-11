#!/usr/bin/env python3
"""Lectura de los documentos del proyecto: secciones, parrafos y el brief.

Vive en los scripts compartidos del plugin porque lo leen dos skills:
`aiba-onboarding`, para contarle a quien llega que es el proyecto, y
`aiba-handover`, para contarselo a quien se queda con el. Dos copias del mismo
lector acabarian discrepando en el primer arreglo --paso con el titulo del brief
sin separador, que se tomaba como nombre del proyecto--, y el arreglo llegaria
solo a una.

Se importa como `sprints.py`: los scripts de los skills anaden
`parents[3] / "scripts"` al `sys.path`.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path


def clave(texto: str) -> str:
    """Titulo comparable: sin tildes, sin numeracion y en minusculas."""
    t = unicodedata.normalize("NFKD", texto or "")
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    t = re.sub(r"^[\d.\s]+", "", t.strip())
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def secciones(md: str) -> dict:
    """Cuerpo de cada seccion de segundo nivel, por su titulo normalizado."""
    fuera = {}
    for bloque in re.split(r"^##\s+", md, flags=re.M)[1:]:
        titulo, _, cuerpo = bloque.partition("\n")
        fuera[clave(titulo)] = cuerpo
    return fuera


def buscar(sec: dict, palabra: str) -> str:
    return next((v for k, v in sec.items() if palabra in k), "")


def parrafo(cuerpo: str, limite: int = 700) -> str:
    lineas = []
    for l in cuerpo.splitlines():
        l = l.strip()
        if not l:
            if lineas:
                break
            continue
        if l.startswith(("#", "|", ">")):
            continue
        lineas.append(l.lstrip("-* ").strip())
    return " ".join(lineas)[:limite]


def vinetas(cuerpo: str, n: int = 6) -> list[str]:
    return [l.strip()[2:].strip() for l in cuerpo.splitlines()
            if l.strip().startswith(("- ", "* "))][:n]


def leer_proyecto(root: Path) -> dict:
    """Nombre, contexto, usuarios y stack, del brief del cliente."""
    f = root / "docs" / "cliente-requisitos.md"
    if not f.is_file():
        return {"nombre": "", "contexto": "", "usuarios": [], "stack": []}
    md = f.read_text(encoding="utf-8", errors="replace")
    h1 = re.search(r"^#\s+(.+)$", md, re.M)
    partes = re.split(r"\s[—–-]\s", h1.group(1)) if h1 else []
    # Sin separador el titulo es el del documento --"Brief del cliente"--, no el
    # nombre del proyecto: mejor el respaldo que llamar asi al proyecto.
    nombre = partes[-1].strip() if len(partes) > 1 else ""
    sec = secciones(md)
    return {"nombre": nombre, "contexto": parrafo(buscar(sec, "contexto")),
            "usuarios": vinetas(buscar(sec, "usuario")),
            "stack": vinetas(buscar(sec, "stack"))}
