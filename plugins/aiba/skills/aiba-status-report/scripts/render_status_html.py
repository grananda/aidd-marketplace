#!/usr/bin/env python3
"""aiba-status-report · render_status_html.py — el informe de situacion en HTML.

Toma el JSON de `compute_status.py`, enriquecido por el skill con la narrativa
--riesgos, GAPs, desviaciones, resumen y recomendaciones-- y produce un HTML
autocontenido: sin CDN, sin fuentes externas, sin peticiones. Un informe de
estado se reenvia por correo y se abre sin red.

**Las cifras vienen del calculo y la narrativa del skill.** El renderizador no
inventa ninguna de las dos: si un bloque no esta en el JSON, la seccion sale
diciendo que falta y de que documento vendria.

Uso:
    python3 render_status_html.py --input estado.json --output docs/html/estado-proyecto.html
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

# Semantica del color, no decoracion: cada uno significa una sola cosa en todo
# el informe. Se declara aqui para que el HTML no invente tonos por su cuenta.
SEM = {"ok": "verde", "curso": "azul", "riesgo": "ambar", "malo": "rojo", "neutro": "gris"}

CSS = """
:root{
  --bg:#fbfbfd; --panel:#ffffff; --linea:#e4e4e9; --texto:#16161d; --suave:#5f5f6d;
  --verde:#15803d; --verde-b:#dcfce7; --azul:#1d4ed8; --azul-b:#dbeafe;
  --ambar:#a16207; --ambar-b:#fef3c7; --rojo:#b91c1c; --rojo-b:#fee2e2;
  --gris:#52525b; --gris-b:#f1f1f4; --acento:#1d4ed8;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --bg:#0e0e12; --panel:#17171d; --linea:#2b2b34; --texto:#ececf2; --suave:#a1a1b0;
  --verde:#4ade80; --verde-b:#14321f; --azul:#7dabff; --azul-b:#13233f;
  --ambar:#fbbf24; --ambar-b:#3a2c07; --rojo:#f87171; --rojo-b:#3b1414;
  --gris:#a1a1aa; --gris-b:#23232b; --acento:#7dabff;
}}
:root[data-theme="dark"]{
  --bg:#0e0e12; --panel:#17171d; --linea:#2b2b34; --texto:#ececf2; --suave:#a1a1b0;
  --verde:#4ade80; --verde-b:#14321f; --azul:#7dabff; --azul-b:#13233f;
  --ambar:#fbbf24; --ambar-b:#3a2c07; --rojo:#f87171; --rojo-b:#3b1414;
  --gris:#a1a1aa; --gris-b:#23232b; --acento:#7dabff;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--texto);
  font:15px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:1120px;margin:0 auto;padding:32px 20px 72px}
h1{font-size:26px;letter-spacing:-.02em;margin:0 0 4px;text-wrap:balance}
h2{font-size:17px;letter-spacing:-.01em;margin:40px 0 12px;padding-bottom:8px;
   border-bottom:1px solid var(--linea)}
h3{font-size:14px;margin:0 0 10px;color:var(--suave);font-weight:600;
   text-transform:uppercase;letter-spacing:.06em}
.sub{color:var(--suave);font-size:14px;margin:0}
.hero{display:flex;flex-wrap:wrap;gap:24px;align-items:flex-end;justify-content:space-between;
      padding-bottom:20px;border-bottom:2px solid var(--linea)}
.hero-dato{text-align:right}
.hero-dato b{display:block;font-size:19px;font-variant-numeric:tabular-nums}
.hero-dato span{font-size:12px;color:var(--suave);text-transform:uppercase;letter-spacing:.06em}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(178px,1fr));gap:12px;margin:22px 0 8px}
.kpi{background:var(--panel);border:1px solid var(--linea);border-radius:10px;padding:14px 16px}
.kpi .v{font-size:27px;font-weight:650;font-variant-numeric:tabular-nums;line-height:1.1}
.kpi .l{font-size:13px;font-weight:600;margin-top:4px}
.kpi .s{font-size:12px;color:var(--suave);margin-top:3px}
.card{background:var(--panel);border:1px solid var(--linea);border-radius:10px;
      padding:16px 18px;margin-bottom:14px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}
.barra{margin:10px 0}
.barra .cab{display:flex;justify-content:space-between;font-size:13px;margin-bottom:5px}
.barra .cab b{font-variant-numeric:tabular-nums}
.pista{height:9px;border-radius:5px;background:var(--gris-b);overflow:hidden;display:flex}
.pista i{display:block;height:100%}
.leyenda{display:flex;flex-wrap:wrap;gap:14px;font-size:12px;color:var(--suave);margin-top:9px}
.leyenda i{width:9px;height:9px;border-radius:3px;display:inline-block;margin-right:5px}
table{width:100%;border-collapse:collapse;font-size:13.5px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--linea);vertical-align:top}
th{font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--suave);font-weight:600}
td.num{text-align:right;font-variant-numeric:tabular-nums}
.scroll{overflow-x:auto}
.pill{display:inline-block;padding:2px 9px;border-radius:99px;font-size:11.5px;font-weight:600;
      white-space:nowrap}
.p-verde{background:var(--verde-b);color:var(--verde)} .p-azul{background:var(--azul-b);color:var(--azul)}
.p-ambar{background:var(--ambar-b);color:var(--ambar)} .p-rojo{background:var(--rojo-b);color:var(--rojo)}
.p-gris{background:var(--gris-b);color:var(--gris)}
.nota{border-left:3px solid var(--acento);background:var(--gris-b);padding:11px 14px;
      border-radius:0 8px 8px 0;font-size:13.5px;margin:12px 0}
.nota.mal{border-left-color:var(--rojo)} .nota.ojo{border-left-color:var(--ambar)}
.nota.bien{border-left-color:var(--verde)}
.hueco{color:var(--ambar);font-size:13.5px;font-style:italic}
.pie-dato{color:var(--suave);font-size:12.5px;margin:6px 0 0}
a{color:var(--acento)}
.pie{margin-top:44px;padding-top:16px;border-top:1px solid var(--linea);
     font-size:12.5px;color:var(--suave)}
ul.lim{margin:8px 0;padding-left:20px} ul.lim li{margin:4px 0}
"""


def e(v) -> str:
    return html.escape("" if v is None else str(v))


def pill(texto, tono="gris") -> str:
    return f'<span class="pill p-{tono}">{e(texto)}</span>'


def barra(segmentos: list[tuple[float, str]]) -> str:
    """Una pista con varios tramos. Los porcentajes ya vienen calculados."""
    tramos = "".join(
        f'<i style="width:{max(0.0, min(100.0, p)):.4g}%;background:var(--{c})"></i>'
        for p, c in segmentos if p and p > 0)
    return f'<div class="pista">{tramos}</div>'


def tabla(cabeceras: list[str], filas: list[list[str]], numericas: set[int] | None = None) -> str:
    if not filas:
        return '<p class="hueco">Sin datos.</p>'
    num = numericas or set()
    th = "".join(f"<th>{e(c)}</th>" for c in cabeceras)
    tr = "".join(
        "<tr>" + "".join(
            f'<td class="num">{c}</td>' if i in num else f"<td>{c}</td>"
            for i, c in enumerate(f)) + "</tr>"
        for f in filas)
    return f'<div class="scroll"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


# --- Secciones ---------------------------------------------------------------

def sec_avance(d: dict) -> str:
    a = d.get("avance", {})
    ch, es, hu = a.get("changes", {}), a.get("esfuerzo", {}), a.get("hus", {})
    prev, desv = d.get("previsto", {}), d.get("desviacion", {})
    p = []

    p.append('<h2>Avance real frente a avance previsto</h2>')
    p.append('<div class="nota">El avance real se mide por <b>trabajo ejecutado</b>, no por '
             'fechas: cada fase pesa sus dias de esfuerzo y solo cuenta cuando su change esta '
             'archivado. Cerrar una fase L vale mas que cerrar una XS.</div>')

    p.append('<div class="grid2">')
    total = ch.get("total") or 0
    # La barra va **por esfuerzo**, igual que el titular. Pintarla por numero de
    # fases daba dos cifras distintas del mismo avance en la misma pantalla --
    # 35,2% arriba y 42,9% justo debajo--, que es como se pierde la confianza en
    # un informe. El recuento sigue estando, en la etiqueta y en su propia linea.
    td = es.get("total_dias") or 0
    pc = es.get("pct_cerrado") or 0 if td else (ch.get("pct_cerrado") or 0)
    pa = round((es.get("activo_dias") or 0) / td * 100, 1) if td else (ch.get("pct_activo") or 0)
    unidad = "esfuerzo" if td else "numero de fases"
    p.append('<div class="card"><h3>Por changes · metrica principal</h3>')
    p.append(f'<div class="barra"><div class="cab"><span>Cerrados / activos / pendientes '
             f'<b>por {unidad}</b></span>'
             f'<b>{ch.get("cerrados",0)} · {ch.get("activos",0)} · '
             f'{ch.get("pendientes",0)} de {total} fases</b></div>')
    p.append(barra([(pc, "verde"), (pa, "azul")]))
    p.append('<div class="leyenda">'
             f'<span><i style="background:var(--verde)"></i>Cerrados {pc:.4g}%</span>'
             f'<span><i style="background:var(--azul)"></i>Activos {pa:.4g}%</span>'
             f'<span><i style="background:var(--gris-b)"></i>Pendientes '
             f'{max(0, 100 - pc - pa):.4g}%</span></div></div>')
    pn = ch.get("pct_cerrado") or 0
    if td and abs(pn - pc) >= 3:
        mas = "grandes" if pn < pc else "pequenas"
        p.append(f'<p class="pie-dato">Por numero de fases seria {pn:.4g}%, '
                 f'{abs(pn - pc):.4g} puntos de diferencia: las fases cerradas son '
                 f'mas {mas} que la media. La cifra buena es la de esfuerzo.</p>')
    if ch.get("ids_cerrados"):
        p.append(f'<p class="pie-dato">Cerrados: {e(", ".join(ch["ids_cerrados"]))}</p>')
    if ch.get("ids_activos"):
        p.append(f'<p class="pie-dato">Activos: {e(", ".join(ch["ids_activos"]))}</p>')
    p.append("</div>")

    p.append('<div class="card"><h3>Por historias de usuario · metrica secundaria</h3>')
    tot_hu = hu.get("total") or 0
    if tot_hu:
        pok = hu.get("pct_ok") or 0
        pcur = round((hu.get("en_curso") or 0) / tot_hu * 100, 1)
        p.append('<div class="barra"><div class="cab"><span>Entregadas / en curso / sin iniciar</span>'
                 f'<b>{hu.get("ok",0)} · {hu.get("en_curso",0)} · '
                 f'{hu.get("sin_iniciar",0)} de {tot_hu}</b></div>')
        p.append(barra([(pok, "verde"), (pcur, "azul")]))
        p.append('<div class="leyenda">'
                 f'<span><i style="background:var(--verde)"></i>Entregadas {pok:.4g}%</span>'
                 f'<span><i style="background:var(--azul)"></i>En curso {pcur:.4g}%</span>'
                 '</div></div>')
        p.append('<p class="pie-dato">Una HU cuenta como entregada cuando el change que la '
                 'implementa esta archivado, no cuando se escribio su codigo.</p>')
    else:
        p.append('<p class="hueco">Las fases del roadmap no declaran que HUs cubren '
                 '(campo <code>hus</code> de <code>openspec/config.yaml</code>).</p>')
    p.append("</div></div>")

    p.append('<div class="card"><h3>Esfuerzo</h3>')
    if es.get("total_dias"):
        p.append(tabla(
            ["Concepto", "Dias", "% del total"],
            [["Entregado", f'{es.get("cerrado_dias",0):.4g}',
              f'{es.get("pct_cerrado") or 0:.4g}%'],
             ["En curso", f'{es.get("activo_dias",0):.4g}',
              f'{round((es.get("activo_dias") or 0)/es["total_dias"]*100,1):.4g}%'],
             ["Previsto a dia de hoy",
              f'{prev.get("dias") if prev.get("dias") is not None else "—"}',
              f'{prev["pct"]:.4g}%' if prev.get("pct") is not None else "—"],
             ["<b>Total del proyecto</b>", f'<b>{es["total_dias"]:.4g}</b>', "<b>100%</b>"]],
            numericas={1, 2}))
    else:
        p.append('<p class="hueco">No hay esfuerzo por fase: ni <code>effort_ai</code> en '
                 '<code>openspec/config.yaml</code> ni tallas en el detalle de historias.</p>')
    p.append("</div>")

    if desv.get("puntos") is not None:
        tono = {"adelantado": "bien", "retrasado": "mal"}.get(desv.get("sentido"), "")
        signo = "+" if desv["puntos"] > 0 else ""
        p.append(f'<div class="nota {tono}"><b>Desviacion: {signo}{desv["puntos"]:.4g} puntos'
                 f'</b> ({signo}{desv.get("dias",0):.4g} dias de esfuerzo) — '
                 f'el proyecto va <b>{e(desv.get("sentido"))}</b> respecto al plan de sprints. '
                 f'Previsto {prev.get("pct"):.4g}% · real {es.get("pct_cerrado") or 0:.4g}%.</div>')
    else:
        p.append(f'<div class="nota ojo"><b>No hay avance previsto con el que comparar.</b> '
                 f'{e(desv.get("motivo") or prev.get("motivo_si_falta") or "")}</div>')
    return "\n".join(p)


def sec_comparativa(d: dict) -> str:
    """Que ha cambiado desde el informe anterior. Va arriba porque es lo primero
    que pregunta quien ya vio el de la semana pasada."""
    c = d.get("comparativa")
    if not c:
        return ""
    p = ['<h2>Desde el informe anterior</h2>', '<div class="card">']
    p.append(f'<p class="pie-dato">Comparado con el informe del {e(c.get("desde"))}.</p>')
    filas = []
    av = c.get("avance_puntos")
    if av is not None:
        filas.append(["Avance real",
                      pill(f'{"+" if av > 0 else ""}{av:.4g} puntos',
                           "verde" if av > 0 else "gris" if av == 0 else "rojo")])
    dv = c.get("desviacion_puntos")
    if dv is not None:
        filas.append(["Desviacion frente al plan",
                      pill(f'{"+" if dv > 0 else ""}{dv:.4g} puntos',
                           "verde" if dv > 0 else "rojo" if dv < 0 else "gris")])
    for etiqueta, clave, tono in (
            ("Changes cerrados desde entonces", "changes_cerrados_desde", "verde"),
            ("Bloqueos resueltos", "bloqueos_resueltos", "verde"),
            ("Bloqueos nuevos", "bloqueos_nuevos", "rojo")):
        v = c.get(clave) or []
        filas.append([etiqueta, ", ".join(e(x) for x in v) if v else pill("ninguno", "gris")])
    p.append(tabla(["Concepto", "Cambio"], filas))
    rep = c.get("bloqueos_que_repiten") or []
    if rep:
        p.append('<div class="nota mal"><b>Bloqueos que repiten: '
                 + ", ".join(e(x) for x in rep) + '.</b> Un bloqueo que aparece en dos '
                 'informes seguidos ya no es un bloqueo: es un problema de gobierno, y se '
                 'resuelve escalandolo, no esperando.</div>')
    p.append("</div>")
    return "\n".join(p)


def sec_riesgos(d: dict) -> str:
    n = d.get("narrativa") or {}
    p = ['<h2>Riesgos, bloqueos y dependencias</h2>']

    bl = d.get("bloqueos") or []
    p.append('<div class="card"><h3>Bloqueos activos</h3>')
    if bl:
        p.append('<div class="nota mal">Son <b>bloqueos medidos</b>, no declarados: decisiones '
                 'marcadas como bloqueantes en el pre-flight de un change y todavia sin '
                 'resolver en <code>openspec/audit/</code>.</div>')
        p.append(tabla(["Change", "Decision pendiente", "Bloqueado desde"],
                       [[e(b.get("change")), e(b.get("decision")),
                         e((b.get("desde") or "")[:10])] for b in bl]))
    else:
        p.append('<div class="nota bien">Ninguna decision bloqueante pendiente en la '
                 'auditoria.</div>')
    p.append("</div>")

    dep = d.get("dependencias") or {}
    p.append('<div class="grid2">')
    p.append('<div class="card"><h3>Fases listas para abrir</h3>')
    listas = dep.get("listas") or []
    p.append(tabla(["Fase", "Nombre", "change_hint"],
                   [[e(x["fase"]), e(x["nombre"]), f'<code>{e(x["change_hint"])}</code>']
                    for x in listas]) if listas else
             '<p class="pie-dato">Ninguna fase pendiente tiene todas sus dependencias '
             'cerradas.</p>')
    p.append("</div>")
    p.append('<div class="card"><h3>Fases bloqueadas por dependencia</h3>')
    blq = dep.get("bloqueadas") or []
    p.append(tabla(["Fase", "Nombre", "Espera a"],
                   [[e(x["fase"]), e(x["nombre"]),
                     ", ".join(f'{e(f)}{" (en curso)" if f in x.get("alguna_en_curso",[]) else ""}'
                               for f in x["espera_a"])] for x in blq]) if blq else
             '<p class="pie-dato">Ninguna.</p>')
    p.append("</div></div>")

    conf = dep.get("conflictos") or []
    if conf:
        p.append('<div class="nota mal"><b>Conflicto de faseado.</b> Estas dependencias cruzan '
                 'de un lane a otro sin pasar por una barrera, asi que los lanes dejan de ser '
                 'independientes sin que nada lo declare: ' +
                 "; ".join(f'{e(c["fase"])} ({e(c["lane"])}) depende de {e(c["depende_de"])} '
                           f'({e(c["lane_origen"])})' for c in conf) +
                 '. Lo resuelve <code>aisdd roadmap</code>.</div>')

    for clave, titulo, cabs, campos in (
        ("riesgos", "Riesgos", ["ID", "Descripcion", "Probabilidad", "Impacto", "Estado",
                                "Mitigacion", "Origen"],
         ["id", "descripcion", "probabilidad", "impacto", "estado", "mitigacion", "origen"]),
        ("gaps", "GAPs y dependencias externas",
         ["GAP", "Descripcion", "Probabilidad", "Sprint impactado", "Estado", "Accion requerida"],
         ["id", "descripcion", "probabilidad", "sprint", "estado", "accion"]),
    ):
        filas = n.get(clave) or []
        p.append(f'<div class="card"><h3>{titulo}</h3>')
        p.append(tabla(cabs, [[e(r.get(c)) for c in campos] for r in filas]) if filas else
                 f'<p class="hueco">El informe no recoge {titulo.lower()}. Se consolidan de '
                 f'<code>docs/planificacion-proyecto.md</code>, <code>docs/sprint-plan.md</code> '
                 f'y <code>docs/arquitectura-base.md</code>.</p>')
        p.append("</div>")
    return "\n".join(p)


def sec_calendario(d: dict) -> str:
    p = ['<h2>Calendario, camino critico y ritmo</h2>']

    sp = d.get("sprints") or []
    p.append('<div class="card"><h3>Sprints</h3>')
    if sp:
        actual = (d.get("previsto") or {}).get("sprint_actual")
        cerrados = set((d.get("previsto") or {}).get("sprints_cerrados") or [])
        filas = []
        for s in sp:
            if s["nombre"] in cerrados:
                est = pill("cerrado", "verde")
            elif s["nombre"] == actual:
                est = pill("en curso", "azul")
            else:
                est = pill("pendiente", "gris")
            filas.append([e(s["nombre"]), e(s.get("desde") or "—"),
                          e(s.get("hasta") or "—"), est])
        p.append(tabla(["Sprint", "Desde", "Hasta", "Estado"], filas))
    else:
        p.append('<p class="hueco">No se reconocieron sprints en '
                 '<code>docs/sprint-plan.md</code>.</p>')
    p.append("</div>")

    cc = d.get("camino_critico") or {}
    p.append('<div class="grid2"><div class="card"><h3>Camino critico</h3>')
    if cc.get("dias"):
        p.append(f'<p><b style="font-size:22px">{cc["dias"]:.4g} dias</b> de cadena de '
                 f'dependencias mas larga.</p>')
        p.append(f'<p class="pie-dato">{e(" → ".join(cc.get("cadena") or []))}</p>')
        p.append('<div class="nota">Ningun reparto del trabajo baja de esa cifra, con los '
                 'developers que sea. Cuando el calendario la toca, anadir gente ya no compra '
                 'tiempo.</div>')
    else:
        p.append('<p class="hueco">Sin <code>depends_on</code> en las fases no hay grafo del '
                 'que derivar el camino critico.</p>')
    p.append("</div>")

    r = d.get("ritmo") or {}
    p.append('<div class="card"><h3>Ritmo de entrega</h3>')
    if r.get("changes_medidos"):
        tono = {"acelerando": "verde", "frenando": "rojo"}.get(r.get("tendencia"), "gris")
        p.append(f'<p><b style="font-size:22px">{r["lead_time_medio_dias"]:.4g} dias</b> '
                 f'de media entre abrir y cerrar un change '
                 f'({r["changes_medidos"]} medidos) {pill(r.get("tendencia",""), tono)}</p>')
        if r.get("ratio_atencion_medio") is not None:
            ra = r["ratio_atencion_medio"]
            tono_r = "rojo" if ra < 15 else "ambar" if ra < 35 else "verde"
            p.append(f'<p><b style="font-size:22px">{ra:.4g}%</b> de atencion sobre '
                     f'calendario {pill("atencion / calendario", tono_r)}</p>')
            p.append(f'<div class="nota {"mal" if ra < 15 else ""}">De todo el tiempo que '
                     f'un change estuvo abierto, se trabajo en el un {ra:.4g}% '
                     f'({r.get("atendido_horas",0):.4g} h atendidas en '
                     f'{r.get("changes_con_atencion",0)} changes). Un ratio bajo significa '
                     f'que el change estuvo <b>esperando</b>, no avanzando — y casi siempre '
                     f'esperando a algo que esta en la lista de bloqueos.</div>')
        elif r.get("ratio_atencion_motivo"):
            p.append(f'<p class="hueco">{e(r["ratio_atencion_motivo"])}</p>')
        cabs = ["Change", "Abierto", "Cerrado", "Dias"]
        num = {3}
        con_at = any("atendido_h" in x for x in (r.get("por_change") or []))
        if con_at:
            cabs += ["Atendido (h)", "Atencion"]
            num |= {4, 5}
        filas = []
        for x in (r.get("por_change") or []):
            fila = [e(x["change"]), e(x["abierto"][:10]), e(x["cerrado"][:10]),
                    f'{x["dias"]:.4g}']
            if con_at:
                fila += [f'{x["atendido_h"]:.4g}' if "atendido_h" in x else "—",
                         f'{x["ratio_atencion"]:.4g}%' if "ratio_atencion" in x else "—"]
            filas.append(fila)
        p.append(tabla(cabs, filas, numericas=num))
    else:
        p.append(f'<p class="hueco">{e(r.get("motivo") or "Sin auditoria no hay fechas de "
                 "apertura y cierre, asi que no hay ritmo que medir.")}</p>')
    p.append("</div></div>")
    return "\n".join(p)


def sec_narrativa(d: dict) -> str:
    n = d.get("narrativa") or {}
    p = ['<h2>Analisis de desviaciones y acciones</h2>']

    desvs = n.get("desviaciones") or []
    p.append('<div class="card"><h3>Desviaciones detectadas</h3>')
    p.append(tabla(["ID", "Desviacion", "Causa raiz", "Prioridad", "Accion propuesta",
                    "Responsable", "Plazo"],
                   [[e(x.get("id")), e(x.get("desviacion")), e(x.get("causa")),
                     pill(x.get("prioridad", "—"),
                          {"alta": "rojo", "media": "ambar"}.get(
                              str(x.get("prioridad", "")).lower(), "gris")),
                     e(x.get("accion")), e(x.get("responsable")), e(x.get("plazo"))]
                    for x in desvs]) if desvs else
             '<p class="hueco">El informe no recoge desviaciones. Si las cifras de arriba '
             'muestran retraso y esta tabla esta vacia, falta el analisis.</p>')
    p.append("</div>")

    p.append('<h2>Resumen de situacion y recomendaciones</h2>')
    resumen = n.get("resumen") or []
    p.append('<div class="card"><h3>Valoracion cualitativa</h3>')
    if resumen:
        for parrafo in (resumen if isinstance(resumen, list) else [resumen]):
            p.append(f"<p>{e(parrafo)}</p>")
    else:
        p.append('<p class="hueco">Sin valoracion cualitativa. Las cifras dicen donde esta el '
                 'proyecto; esta seccion dice si eso es bueno o malo y por que.</p>')
    p.append("</div>")

    recs = n.get("recomendaciones") or []
    p.append('<div class="card"><h3>Acciones a corto plazo</h3>')
    p.append(tabla(["Prioridad", "Accion", "Por que", "Responsable", "Plazo"],
                   [[pill(x.get("prioridad", "—"),
                          {"alta": "rojo", "media": "ambar"}.get(
                              str(x.get("prioridad", "")).lower(), "gris")),
                     e(x.get("accion")), e(x.get("porque")),
                     e(x.get("responsable")), e(x.get("plazo"))]
                    for x in recs]) if recs else
             '<p class="hueco">Sin recomendaciones. Una recomendacion sin responsable y sin '
             'plazo es una opinion, asi que las dos columnas son parte de la accion.</p>')
    p.append("</div>")
    return "\n".join(p)


def sec_fuentes(d: dict) -> str:
    p = ['<h2>Documentos de referencia</h2>',
         '<div class="nota bien">Todas las cifras de este informe salen de los documentos de '
         'abajo. Lo que no se puede derivar de ellos aparece como hueco declarado, nunca como '
         'una cifra plausible.</div>', '<div class="card">']
    filas = []
    for f in d.get("fuentes") or []:
        doc = f.get("documento", "")
        est = pill("usado", "verde") if f.get("existe") else pill("no existe", "gris")
        enlace = f'<a href="../../{e(doc)}">{e(doc)}</a>' if f.get("existe") else f"<code>{e(doc)}</code>"
        filas.append([enlace, est, e(f.get("usado_para"))])
    p.append(tabla(["Documento", "Estado", "De donde sale que"], filas))
    p.append("</div>")

    avisos = d.get("avisos") or []
    if avisos:
        p.append('<div class="card"><h3>Limites de este informe</h3><ul class="lim">')
        p += [f"<li>{e(a)}</li>" for a in avisos]
        p.append("</ul></div>")
    return "\n".join(p)


def construir(d: dict) -> str:
    a = d.get("avance", {})
    ch, es, hu = a.get("changes", {}), a.get("esfuerzo", {}), a.get("hus", {})
    prev, desv = d.get("previsto", {}), d.get("desviacion", {})
    proyecto = d.get("proyecto") or "Proyecto"
    fin = ""
    if d.get("sprints"):
        fin = (d["sprints"][-1].get("hasta") or "")

    kpis = [
        (f'{es.get("pct_cerrado") or 0:.4g}%', "Avance real", "verde",
         f'{ch.get("cerrados",0)} cerrados + {ch.get("activos",0)} activos de {ch.get("total",0)}'),
        (f'{prev["pct"]:.4g}%' if prev.get("pct") is not None else "—", "Avance previsto hoy",
         "azul", e(prev.get("sprint_actual") or prev.get("motivo_si_falta") or "")),
        (f'{hu.get("pct_ok"):.4g}%' if hu.get("pct_ok") is not None else "—",
         "HU entregadas", "ambar", f'{hu.get("ok",0)} de {hu.get("total",0)}'),
        (str(len(d.get("bloqueos") or [])), "Bloqueos activos", "rojo",
         e(", ".join(b.get("decision", "") for b in (d.get("bloqueos") or [])[:3])) or "ninguno"),
        (("+" if (desv.get("puntos") or 0) > 0 else "") +
         (f'{desv["puntos"]:.4g} pts' if desv.get("puntos") is not None else "—"),
         "Desviacion", {"adelantado": "verde", "retrasado": "rojo"}.get(desv.get("sentido"), "gris"),
         e(desv.get("sentido", ""))),
    ]
    tarjetas = "".join(
        f'<div class="kpi"><div class="v" style="color:var(--{c})">{e(v)}</div>'
        f'<div class="l">{e(l)}</div><div class="s">{s}</div></div>'
        for v, l, c, s in kpis)

    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Situacion del proyecto · {e(proyecto)}</title>
<style>{CSS}</style>
<div class="wrap">
<header class="hero">
  <div><h1>Informe de situacion</h1>
  <p class="sub">{e(proyecto)} · faseado <b>{e(d.get("modo_faseado","atomic"))}</b></p></div>
  <div style="display:flex;gap:26px">
    <div class="hero-dato"><b>{e(d.get("generado",""))}</b><span>Fecha del informe</span></div>
    {f'<div class="hero-dato"><b>{e(fin)}</b><span>Fin del ultimo sprint</span></div>' if fin else ''}
  </div>
</header>
<div class="kpis">{tarjetas}</div>
{sec_comparativa(d)}
{sec_avance(d)}
{sec_riesgos(d)}
{sec_calendario(d)}
{sec_narrativa(d)}
{sec_fuentes(d)}
<p class="pie">Generado por <code>aiba status-report</code> el {e(d.get("generado",""))}.
Las cifras las calcula <code>compute_status.py</code> sobre los documentos del repositorio;
la valoracion y las acciones las escribe el analista.</p>
</div>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Renderiza el informe de situacion en HTML.")
    ap.add_argument("--input", help="JSON de compute_status.py con la narrativa; sin el, stdin")
    ap.add_argument("--output", required=True, help="ruta del .html de salida")
    args = ap.parse_args()

    crudo = (Path(args.input).read_text(encoding="utf-8") if args.input else sys.stdin.read())
    try:
        d = json.loads(crudo)
    except json.JSONDecodeError as ex:
        sys.stderr.write(f"La entrada no es JSON valido: {ex}\n")
        return 2

    salida = Path(args.output)
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(construir(d), encoding="utf-8")
    print(json.dumps({"salida": str(salida),
                      "secciones": 5,
                      "narrativa": sorted((d.get("narrativa") or {}).keys()),
                      "avisos": len(d.get("avisos") or [])}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
