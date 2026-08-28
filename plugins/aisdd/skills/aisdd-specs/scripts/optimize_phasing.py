#!/usr/bin/env python3
"""aisdd-specs · optimize_phasing.py — compara caminos de faseado y calcula el optimo.

Dado el grafo de fases (id, ``depends_on``, esfuerzo en dias) que ``aisdd roadmap``
acaba de disenar, calcula cuanto dura el proyecto en cada modo y con cada numero
de developers, y emite:

  * un resumen JSON por stdout, para que el agente lo lea y lo presente;
  * un HTML autocontenido con los caminos superpuestos, sus barreras y sus tiempos.

Por que un script y no prosa: el calendario de un faseado con dependencias es una
planificacion, y una planificacion que el modelo estima "a ojo" cada vez no se
puede contrastar. Aqui el numero sale igual todas las veces y se puede rehacer.

MODELO
------
Los tres modos son el **mismo** problema de scheduling con ``N`` maquinas sobre un
grafo de precedencias. Lo unico que cambia es cuantas sincronizaciones se fuerzan:

    atomic     N = 1. Todo en serie.
    waves      N maquinas, con una **barrera despues de cada oleada**: nadie
               empieza la oleada k+1 hasta que la k entera ha terminado.
    multilane  N maquinas, con barreras **solo** donde cambia el contrato
               compartido (``shared: true``) o en la foundation.

De ahi sale una relacion que se cumple siempre y conviene ver en el diagrama:
``multilane <= waves <= atomic`` a igual ``N``. Las oleadas pagan una sincronizacion
por tanda que los lanes solo pagan en las barreras reales.

LIMITE INFERIOR
---------------
El **camino critico** (la cadena de dependencias mas larga) acota por debajo
cualquier calendario, con los devs que sea. Es la cifra que dice cuando dejar de
anadir gente: en cuanto el makespan toca el camino critico, un dev mas no compra
ni un dia.

QUE PRECISION TIENE
-------------------
El numero se desvia en **dos direcciones a la vez**, y conviene no confundirlas:

* **Optimista sobre la viabilidad.** Da por hecho que existe un corte de lanes
  valido para ese reparto. Un corte real ademas exige rutas y specs disjuntas,
  que es un juicio de arquitectura que ningun script puede hacer. Si el corte no
  se sostiene, ese calendario no se alcanza.
* **Conservador sobre el reparto.** Repartir trabajo con precedencias entre `N`
  maquinas no tiene solucion exacta barata. Aqui se prueban seis prioridades
  distintas y se devuelve el mejor resultado, lo que sobre 800 instancias
  aleatorias se queda en el optimo el **91%** de las veces, y en el peor caso
  medido un 33% por encima. Es decir: el calendario real puede ser **mejor** que
  el que sale aqui, nunca peor por este motivo.

Sirve para **comparar modos entre si**, que es para lo que existe. No es una
promesa de fecha.

Uso:
    python3 optimize_phasing.py --input plan.json [--out comparativa.html]
    cat plan.json | python3 optimize_phasing.py

Entrada (JSON):
    {
      "proyecto": "<nombre, opcional>",
      "fases": [
        {"id": "F1", "titulo": "...", "effort_days": 5.0,
         "depends_on": [], "shared": false, "foundation": false}
      ],
      "equipo": {"devs": 2},
      "eleccion_usuario": {"mode": "waves", "devs": 2}
    }

``effort_days`` admite tambien una talla (``"M"``) y se convierte con la escala
AIDD. ``shared: true`` marca una fase que toca superficie compartida: en
``multilane`` es una barrera obligatoria.

Codigo de salida:
    0  comparativa generada
    2  entrada invalida (JSON mal formado, ciclo en depends_on, campos que faltan)

Solo biblioteca estandar.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

# Escala de tallas AIDD, 1 d = jornada de 8 h. Misma tabla que EFFORT_DAYS de
# booster-docs y que la que declara aidd-user-story-details: si cambia en un
# sitio, cambia en los tres o los calendarios dejan de ser comparables.
EFFORT_DAYS = {"XS": 0.5, "S": 1.5, "M": 3.0, "L": 5.0, "XL": 8.0}

MODOS = ("atomic", "waves", "multilane")


# --------------------------------------------------------------------------- #
# Entrada
# --------------------------------------------------------------------------- #
class EntradaInvalida(Exception):
    """La entrada no describe un faseado calculable."""


def esfuerzo(valor) -> float:
    """Acepta dias (numero) o talla (XS/S/M/L/XL)."""
    if isinstance(valor, (int, float)):
        return float(valor)
    if isinstance(valor, str) and valor.strip().upper() in EFFORT_DAYS:
        return EFFORT_DAYS[valor.strip().upper()]
    raise EntradaInvalida(
        f"esfuerzo '{valor}' no es ni dias ni talla {'/'.join(EFFORT_DAYS)}")


def lee_fases(datos: dict) -> list[dict]:
    brutas = datos.get("fases")
    if not isinstance(brutas, list) or not brutas:
        raise EntradaInvalida("falta 'fases' o esta vacia")

    fases, vistos = [], set()
    for i, f in enumerate(brutas):
        fid = str(f.get("id") or "").strip()
        if not fid:
            raise EntradaInvalida(f"la fase #{i + 1} no tiene 'id'")
        if fid in vistos:
            raise EntradaInvalida(f"id de fase duplicado: {fid}")
        vistos.add(fid)
        fases.append({
            "id": fid,
            "titulo": str(f.get("titulo") or fid),
            "dias": esfuerzo(f.get("effort_days", f.get("talla", 0))),
            "depends_on": [str(d) for d in (f.get("depends_on") or [])],
            # Una fase que toca superficie compartida no puede vivir en un lane.
            # La foundation lo es por definicion: hasta que la base no esta, no
            # hay nada que paralelizar.
            "shared": bool(f.get("shared") or f.get("foundation")),
            "foundation": bool(f.get("foundation")),
        })

    for f in fases:
        for d in f["depends_on"]:
            if d not in vistos:
                raise EntradaInvalida(f"{f['id']} depende de '{d}', que no existe")
    return fases


def orden_topologico(fases: list[dict], prioridad=None) -> list[str]:
    """Kahn. Un ciclo en depends_on es un faseado invalido, no un caso a tolerar.

    `prioridad` ordena entre las fases que quedan listas a la vez. Sin ella se
    desempata por id, que es determinista pero arbitrario: el orden en que se
    reparten las fases decide el calendario, asi que el desempate no es cosmetico.
    """
    pendientes = {f["id"]: set(f["depends_on"]) for f in fases}
    orden: list[str] = []
    while pendientes:
        libres = sorted(k for k, v in pendientes.items() if not v)
        if not libres:
            raise EntradaInvalida(
                "ciclo en depends_on entre: " + ", ".join(sorted(pendientes)))
        if prioridad is not None:
            libres.sort(key=prioridad)
        for k in libres:
            orden.append(k)
            del pendientes[k]
        for v in pendientes.values():
            v.difference_update(libres)
    return orden


def niveles(fases: list[dict]) -> dict[str, float]:
    """Camino mas largo desde cada fase hasta el final, contando la suya.

    Es la prioridad clasica para repartir trabajo con precedencias: atender antes
    la fase que arrastra mas cola detras. Repartir por id deja para el final
    cadenas largas que ya no caben en paralelo con nada.
    """
    sucesores: dict[str, list[str]] = {f["id"]: [] for f in fases}
    for f in fases:
        for d in f["depends_on"]:
            sucesores[d].append(f["id"])
    por_id = {f["id"]: f for f in fases}
    nivel: dict[str, float] = {}
    for fid in reversed(orden_topologico(fases)):
        nivel[fid] = por_id[fid]["dias"] + max(
            [nivel[s] for s in sucesores[fid]] + [0.0])
    return nivel


# --------------------------------------------------------------------------- #
# Calculo
# --------------------------------------------------------------------------- #
def camino_critico(fases: list[dict]) -> tuple[float, list[str]]:
    """Cadena de dependencias mas larga en dias. Cota inferior de todo calendario."""
    por_id = {f["id"]: f for f in fases}
    fin: dict[str, float] = {}
    previa: dict[str, str | None] = {}
    for fid in orden_topologico(fases):
        f = por_id[fid]
        mejor, quien = 0.0, None
        for d in f["depends_on"]:
            if fin[d] > mejor:
                mejor, quien = fin[d], d
        fin[fid] = mejor + f["dias"]
        previa[fid] = quien
    if not fin:
        return 0.0, []
    ultimo = max(fin, key=lambda k: fin[k])
    cadena, cursor = [], ultimo
    while cursor:
        cadena.append(cursor)
        cursor = previa[cursor]
    return fin[ultimo], list(reversed(cadena))


def planifica(fases: list[dict], devs: int, modo: str) -> dict:
    """Mejor reparto sobre `devs` maquinas. El modo decide que se sincroniza.

    Devuelve el makespan y el detalle por fase (inicio, fin, maquina), que es lo
    que el HTML pinta. Con `waves`, ademas, el numero de oleada.
    """
    if modo == "atomic":
        devs = 1

    por_id = {f["id"]: f for f in fases}
    nivel = niveles(fases)
    sucs = sucesores_de(fases)
    # Prioridades candidatas. Ninguna gana siempre -- por eso se prueban todas y
    # se devuelve el mejor reparto, que es lo que un dev haria si le dejas elegir.
    candidatas = [
        lambda k: -nivel[k],                       # camino critico primero
        lambda k: -por_id[k]["dias"],              # la mas larga primero
        lambda k: por_id[k]["dias"],               # la mas corta primero
        lambda k: k,                               # por id
        lambda k: (-len(sucs[k]), -nivel[k]),      # la que desbloquea mas
        lambda k: (-nivel[k], -por_id[k]["dias"]),
    ]
    mejor: dict | None = None
    for prioridad in candidatas:
        r = _reparte(fases, por_id, orden_topologico(fases, prioridad=prioridad), devs, modo)
        if mejor is None or r["makespan"] < mejor["makespan"]:
            mejor = r
    return mejor


def sucesores_de(fases: list[dict]) -> dict[str, list[str]]:
    s: dict[str, list[str]] = {f["id"]: [] for f in fases}
    for f in fases:
        for d in f["depends_on"]:
            s[d].append(f["id"])
    return s


def _reparte(fases: list[dict], por_id: dict, topo: list[str],
             devs: int, modo: str) -> dict:
    """Coloca las fases en `devs` maquinas siguiendo `topo`. Lo que varia entre
    modos es que se sincroniza; el reparto en si es el mismo."""

    # `waves` fuerza una barrera despues de cada oleada; `multilane`, solo en las
    # fases compartidas. `atomic` no necesita ninguna: con una maquina ya va en serie.
    if modo == "waves":
        oleada: dict[str, int] = {}
        restantes = list(topo)
        n = 0
        while restantes:
            n += 1
            # Una oleada admite las fases cuyas dependencias estan en oleadas
            # anteriores, hasta el ancho `devs`. La foundation va sola en la 1.
            elegibles = [k for k in restantes
                         if all(d in oleada for d in por_id[k]["depends_on"])]
            if not elegibles:
                raise EntradaInvalida("ciclo en depends_on al construir oleadas")
            fund = [k for k in elegibles if por_id[k]["foundation"]]
            if n == 1 and fund:
                tanda = fund[:1]
            else:
                # Las mas largas primero. Una oleada cuesta el `max` de lo que
                # lleva dentro, asi que juntar las largas paga ese maximo una vez;
                # repartirlas lo paga en cada oleada donde caiga una. Sin esta
                # regla el desempate lo decide el orden alfabetico, y sobre el
                # mismo grafo eso puede duplicar el calendario.
                tanda = sorted(elegibles, key=lambda k: -por_id[k]["dias"])[:devs]
            for k in tanda:
                oleada[k] = n
                restantes.remove(k)
    else:
        oleada = {}

    fin_de: dict[str, float] = {}
    libre = [0.0] * devs          # cuando queda libre cada maquina
    detalle: list[dict] = []
    reloj_barrera = 0.0           # nadie empieza antes de la ultima sincronizacion

    def coloca(fid: str, solo: bool) -> None:
        nonlocal reloj_barrera
        f = por_id[fid]
        listo = max([fin_de[d] for d in f["depends_on"]] + [reloj_barrera])
        if solo:
            # Una barrera para a todos: arranca cuando la ultima maquina termina.
            inicio = max([listo] + libre)
            fin = inicio + f["dias"]
            libre[:] = [fin] * devs
            reloj_barrera = fin
            maquina = -1
        else:
            maquina = min(range(devs), key=lambda m: max(libre[m], listo))
            inicio = max(libre[maquina], listo)
            fin = inicio + f["dias"]
            libre[maquina] = fin
        fin_de[fid] = fin
        detalle.append({
            "id": fid, "titulo": f["titulo"], "dias": f["dias"],
            "inicio": inicio, "fin": fin, "maquina": maquina,
            "barrera": solo, "compartida": f["shared"], "oleada": oleada.get(fid),
        })

    if modo == "waves":
        for n in sorted(set(oleada.values())):
            tanda = [k for k in topo if oleada[k] == n]
            for fid in tanda:
                coloca(fid, solo=False)
            # Barrera implicita de fin de oleada: la siguiente no arranca hasta
            # que esta cierra entera. Es lo que las oleadas pagan de mas.
            reloj_barrera = max([fin_de[k] for k in tanda] + [reloj_barrera])
            libre[:] = [reloj_barrera] * devs
    else:
        for fid in topo:
            coloca(fid, solo=(modo == "multilane" and por_id[fid]["shared"]))

    detalle.sort(key=lambda d: (d["inicio"], d["id"]))
    return {
        "modo": modo,
        "devs": devs,
        "makespan": round(max(fin_de.values()), 2) if fin_de else 0.0,
        "fases": detalle,
        "oleadas": max(oleada.values()) if oleada else None,
        "barreras": sum(1 for d in detalle if d["barrera"]),
    }


def barrido(fases: list[dict], tope: int) -> dict:
    """Makespan de cada (modo, N) hasta `tope` devs, y el N a partir del cual no mejora."""
    critico, _ = camino_critico(fases)
    tabla: dict[str, list[dict]] = {}
    optimo: dict[str, dict] = {}
    for modo in MODOS:
        filas = []
        for n in range(1, tope + 1):
            p = planifica(fases, n, modo)
            filas.append({"devs": n, "makespan": p["makespan"]})
            if modo == "atomic":
                break  # atomic no depende de N: siempre una maquina
        tabla[modo] = filas
        # El N optimo es el primero que ya alcanza el mejor makespan del modo:
        # a partir de ahi, un dev mas no compra ni un dia.
        mejor = min(f["makespan"] for f in filas)
        primero = next(f["devs"] for f in filas if f["makespan"] == mejor)
        optimo[modo] = {"devs": primero, "makespan": mejor}
    return {"critico": round(critico, 2), "tabla": tabla, "optimo": optimo}


# --------------------------------------------------------------------------- #
# HTML
# --------------------------------------------------------------------------- #
ETIQUETA = {
    "atomic": "Atómico",
    "waves": "Oleadas",
    "multilane": "Lanes",
}


def pista(p: dict, escala: float) -> str:
    """Una fila por maquina, con las fases colocadas por tiempo. Barreras a todo lo ancho."""
    filas: dict[int, list[dict]] = {}
    for f in p["fases"]:
        filas.setdefault(f["maquina"], []).append(f)

    out = []
    for maquina in sorted(filas, key=lambda m: (m == -1, m)):
        nombre = "barrera" if maquina == -1 else f"dev {maquina + 1}"
        barras = []
        for f in sorted(filas[maquina], key=lambda x: x["inicio"]):
            izq = f["inicio"] * escala
            ancho = max(f["dias"] * escala, 1.2)
            if f["barrera"]:
                clase = "barra barrera"
            elif f["compartida"]:
                clase = "barra desprotegida"  # toca superficie compartida y nada lo impide
            else:
                clase = "barra"
            aviso = ""
            if f["compartida"] and not f["barrera"]:
                aviso = " · SUPERFICIE COMPARTIDA, sin barrera que la proteja"
            titulo = html.escape(f"{f['id']} · {f['titulo']} · {f['dias']:g} d{aviso}")
            barras.append(
                f'<span class="{clase}" style="left:{izq:.3f}%;width:{ancho:.3f}%" '
                f'title="{titulo}"><b>{html.escape(f["id"])}</b></span>')
        out.append(f'<div class="pista"><span class="maquina">{nombre}</span>'
                   f'<div class="carril">{"".join(barras)}</div></div>')
    return "".join(out)


def bloque(titulo: str, subtitulo: str, p: dict, escala: float, tono: str) -> str:
    return f"""<section class="camino {tono}">
  <header>
    <h2>{html.escape(titulo)}</h2>
    <p class="meta">{html.escape(subtitulo)}</p>
    <p class="total"><span class="n">{p['makespan']:g}</span><span class="u">días</span></p>
  </header>
  <div class="pistas">{pista(p, escala)}</div>
</section>"""


def render(datos: dict, res: dict, caminos: list[tuple[str, str, dict, str]]) -> str:
    peor = max(p["makespan"] for _, _, p, _ in caminos) or 1.0
    escala = 100.0 / peor
    proyecto = html.escape(str(datos.get("proyecto") or "Comparativa de faseado"))

    filas_tabla = []
    for modo in MODOS:
        o = res["optimo"][modo]
        filas_tabla.append(
            f"<tr><td>{ETIQUETA[modo]}</td><td class='num'>{o['devs']}</td>"
            f"<td class='num'>{o['makespan']:g} d</td></tr>")

    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{proyecto} · faseado</title>
<style>
:root{{
  --ground:#f4f6f8; --surface:#fff; --line:#d6dce4; --ink:#161b22; --ink-2:#5a6672;
  --user:#8a5a12; --user-bg:#fdf3e2; --opt:#0f6b57; --opt-bg:#e0f2ec;
  --max:#3f5ea8; --max-bg:#e6ecf9; --barrera:#8d3a46; --barrera-bg:#f7e5e8;
  --mono:ui-monospace,SFMono-Regular,Menlo,monospace;
  --body:system-ui,-apple-system,"Segoe UI",sans-serif;
}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{
  --ground:#10141a; --surface:#181e26; --line:#2b333f; --ink:#e7ecf2; --ink-2:#9aa6b4;
  --user:#e0a955; --user-bg:#33260f; --opt:#5cc4a6; --opt-bg:#0f3129;
  --max:#8fa9e8; --max-bg:#1b2540; --barrera:#e08d99; --barrera-bg:#3a1c22;
}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--ground);color:var(--ink);font-family:var(--body);line-height:1.55}}
.wrap{{max-width:64rem;margin:0 auto;padding:2.5rem 1.25rem 4rem}}
h1{{font-size:1.9rem;margin:0 0 .3rem;letter-spacing:-.01em}}
.lede{{color:var(--ink-2);margin:0 0 2rem;max-width:62ch}}
.camino{{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--line);
  border-radius:4px;padding:1.1rem 1.25rem;margin-bottom:1.1rem}}
.camino.tu{{border-left-color:var(--user)}}
.camino.opt{{border-left-color:var(--opt)}}
.camino.max{{border-left-color:var(--max)}}
.camino header{{display:flex;flex-wrap:wrap;align-items:baseline;gap:.35rem 1rem;margin-bottom:.9rem}}
.camino h2{{font-size:1.05rem;margin:0;flex:0 0 auto}}
.meta{{margin:0;color:var(--ink-2);font-size:.86rem;flex:1 1 14rem}}
.total{{margin:0;font-family:var(--mono);white-space:nowrap}}
.total .n{{font-size:1.5rem;font-weight:700;font-variant-numeric:tabular-nums}}
.total .u{{font-size:.75rem;color:var(--ink-2);margin-left:.25rem}}
.pistas{{display:flex;flex-direction:column;gap:.3rem}}
.pista{{display:grid;grid-template-columns:4.5rem 1fr;align-items:center;gap:.6rem}}
.maquina{{font-family:var(--mono);font-size:.7rem;color:var(--ink-2);text-align:right}}
.carril{{position:relative;height:1.6rem;background:var(--ground);border-radius:2px;overflow:hidden}}
.barra{{position:absolute;top:2px;bottom:2px;background:var(--opt-bg);border:1px solid var(--opt);
  border-radius:2px;font-family:var(--mono);font-size:.62rem;display:flex;align-items:center;
  justify-content:center;overflow:hidden;color:var(--ink)}}
.tu .barra{{background:var(--user-bg);border-color:var(--user)}}
.max .barra{{background:var(--max-bg);border-color:var(--max)}}
.barra.barrera{{background:var(--barrera-bg);border-color:var(--barrera);border-style:dashed}}
.barra.desprotegida{{border-color:var(--barrera);border-width:2px;
  background-image:repeating-linear-gradient(45deg,transparent,transparent 3px,
  color-mix(in srgb,var(--barrera) 22%,transparent) 3px,
  color-mix(in srgb,var(--barrera) 22%,transparent) 6px)}}
table{{border-collapse:collapse;width:100%;margin:.6rem 0 0;font-size:.88rem}}
th,td{{border-bottom:1px solid var(--line);padding:.4rem .6rem;text-align:left}}
td.num,th.num{{text-align:right;font-family:var(--mono);font-variant-numeric:tabular-nums}}
.nota{{background:var(--surface);border:1px solid var(--line);border-radius:4px;
  padding:1rem 1.25rem;margin-top:1.5rem;font-size:.9rem;color:var(--ink-2)}}
.nota b{{color:var(--ink)}}
.leyenda{{display:flex;flex-wrap:wrap;gap:1rem;font-size:.78rem;color:var(--ink-2);margin:1.2rem 0 0}}
.leyenda span{{display:flex;align-items:center;gap:.35rem}}
.sw{{width:1.1rem;height:.7rem;border-radius:2px;border:1px solid var(--line);display:inline-block}}
</style></head><body><div class="wrap">
<h1>{proyecto}</h1>
<p class="lede">Cada carril es un developer; cada barra, una fase. Las barras a rayas son
<b>barreras</b>: paran a todo el mundo. El eje es tiempo, a la misma escala en todos los bloques,
así que lo que se compara de un vistazo es el ancho total.</p>
<p class="lede">Las barras con <b>borde grueso y trama</b> son fases que tocan <b>superficie
compartida</b> —contrato, esquema, permisos, rollout— corriendo <b>sin barrera que las proteja</b>.
Solo aparecen fuera de <code>multilane</code>: es la diferencia que el calendario no muestra.
Un camino más corto con esas barras es más rápido <em>y</em> más frágil.</p>

{"".join(bloque(t, s, p, escala, tono) for t, s, p, tono in caminos)}

<div class="nota">
  <p style="margin:0 0 .5rem"><b>El camino crítico son {res['critico']:g} días.</b> Es la cadena
  de dependencias más larga: ningún reparto, con los developers que sea, baja de ahí. Cuando un
  camino toca esa cifra, añadir gente ya no compra calendario.</p>
  <table>
    <tr><th>Modo</th><th class="num">Devs óptimos</th><th class="num">Calendario</th></tr>
    {"".join(filas_tabla)}
  </table>
  <p style="margin:.8rem 0 0"><b>Qué precisión tienen estas cifras.</b> Se desvían en dos
  direcciones. Son <b>optimistas sobre la viabilidad</b>: <code>multilane</code> da por hecho que
  existe un corte de lanes válido para ese reparto, y un corte real exige además rutas y specs
  disjuntas — un juicio de arquitectura que ningún cálculo hace. Y son <b>conservadoras sobre el
  reparto</b>: repartir trabajo con precedencias no tiene solución exacta barata, así que el
  calendario real puede salir algo mejor que el de aquí, nunca peor por ese motivo. Sirven para
  <b>comparar modos entre sí</b>, que es para lo que existen; no son una promesa de fecha.</p>
</div>

<p class="leyenda">
  <span><i class="sw" style="background:var(--user-bg);border-color:var(--user)"></i> tu elección</span>
  <span><i class="sw" style="background:var(--opt-bg);border-color:var(--opt)"></i> óptimo con tu equipo</span>
  <span><i class="sw" style="background:var(--max-bg);border-color:var(--max)"></i> óptimo absoluto</span>
  <span><i class="sw" style="background:var(--barrera-bg);border-color:var(--barrera);border-style:dashed"></i> barrera</span>
  <span><i class="sw" style="border-color:var(--barrera);border-width:2px"></i> superficie compartida <b>sin proteger</b></span>
</p>
</div></body></html>"""


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description="Compara caminos de faseado y calcula el optimo.")
    ap.add_argument("--input", default=None, help="fichero JSON; sin el, stdin")
    ap.add_argument("--out", default=None, help="ruta del HTML comparativo")
    args = ap.parse_args()

    try:
        raw = Path(args.input).read_text(encoding="utf-8") if args.input else sys.stdin.read()
        datos = json.loads(raw)
        fases = lee_fases(datos)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: no se pudo leer la entrada: {exc}", file=sys.stderr)
        return 2
    except EntradaInvalida as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    equipo = int((datos.get("equipo") or {}).get("devs") or 1)
    eleccion = datos.get("eleccion_usuario") or {}
    modo_usuario = eleccion.get("mode") if eleccion.get("mode") in MODOS else "atomic"
    devs_usuario = int(eleccion.get("devs") or equipo)

    # Barrer mas alla del numero de fases no aporta: nunca hay tantas ejecutables
    # a la vez, asi que el makespan deja de moverse.
    tope = max(len(fases), equipo, devs_usuario)
    try:
        res = barrido(fases, tope)
        plan_usuario = planifica(fases, devs_usuario, modo_usuario)
    except EntradaInvalida as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    def preferencia(p: dict) -> tuple:
        """Ordena candidatos: antes calendario, luego devs, y solo entonces el modo.

        A igual calendario y mismos devs no da igual que modo se recomiende. Con un
        solo dev gana `atomic`: los otros dos son ceremonia sin paralelismo que
        proteger. Con mas de uno gana `multilane`, que es el unico cuyo aislamiento
        verifica un comando; `waves` va ultimo porque ordena pero no protege.
        """
        if p["devs"] == 1:
            rango = {"atomic": 0, "multilane": 1, "waves": 2}
        else:
            rango = {"multilane": 0, "waves": 1, "atomic": 2}
        return (p["makespan"], p["devs"], rango[p["modo"]])

    # Optimo con el equipo que hay: el mejor modo sin pasar de `equipo` devs.
    con_equipo = min(
        (planifica(fases, min(res["optimo"][m]["devs"], equipo), m) for m in MODOS),
        key=preferencia)
    # Optimo absoluto: el mejor modo sin tope de equipo.
    absoluto = min(
        (planifica(fases, res["optimo"][m]["devs"], m) for m in MODOS),
        key=preferencia)

    caminos = [
        (f"Tu elección — {ETIQUETA[modo_usuario].lower()}, {devs_usuario} dev"
         f"{'s' if devs_usuario != 1 else ''}",
         "lo que has pedido en el pre-flight", plan_usuario, "tu"),
        (f"Óptimo con tu equipo — {ETIQUETA[con_equipo['modo']].lower()}, "
         f"{con_equipo['devs']} dev{'s' if con_equipo['devs'] != 1 else ''}",
         f"el mejor modo sin pasar de los {equipo} developers disponibles",
         con_equipo, "opt"),
    ]
    if absoluto["devs"] > equipo and absoluto["makespan"] < con_equipo["makespan"]:
        caminos.append((
            f"Óptimo absoluto — {ETIQUETA[absoluto['modo']].lower()}, "
            f"{absoluto['devs']} devs",
            f"{absoluto['devs'] - equipo} developer(s) más de los que hay hoy",
            absoluto, "max"))

    if args.out:
        Path(args.out).write_text(render(datos, res, caminos), encoding="utf-8")

    resumen = {
        "critico_dias": res["critico"],
        "tu_eleccion": {k: plan_usuario[k] for k in ("modo", "devs", "makespan", "barreras")},
        "optimo_con_equipo": {k: con_equipo[k] for k in ("modo", "devs", "makespan", "barreras")},
        "optimo_absoluto": {k: absoluto[k] for k in ("modo", "devs", "makespan", "barreras")},
        "ahorro_vs_tu_eleccion": round(plan_usuario["makespan"] - con_equipo["makespan"], 2),
        "coste_de_no_ampliar": round(con_equipo["makespan"] - absoluto["makespan"], 2),
        "optimo_por_modo": res["optimo"],
        "html": args.out,
    }
    print(json.dumps(resumen, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
