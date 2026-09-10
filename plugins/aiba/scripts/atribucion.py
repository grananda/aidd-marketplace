#!/usr/bin/env python3
"""Por que un change tardo lo que tardo, y que parte de la desviacion explica.

Vive aqui, en los scripts compartidos del plugin, y no dentro de un skill,
porque lo usan dos: `aiba-status-report` lo aplica change a change, y
`aiba-metrics` agrega el resultado para justificar la desviacion del proyecto
entero. Tenerlo dos veces significaria dos definiciones de la misma causa, y una
causa es una afirmacion sobre por que paso algo: no puede depender de que
comando la calcule.

Las dos reglas que sostienen todo lo de aqui:

- **Nada se inventa.** Cada causa nombra el dato de la auditoria del que sale.
  Un change desviado sin ninguna senal se declara **hueco**, no se le asigna la
  causa mas plausible. Una causa inventada es peor que un hueco, porque se actua
  sobre ella.
- **Los adelantos se explican igual que los retrasos.** Si solo se mira lo que
  sale mal, solo se aprende de lo que sale mal.

Se importa como `branding.py`: los scripts de los skills anaden
`parents[3] / "scripts"` al `sys.path`.
"""

from __future__ import annotations

from datetime import datetime, timedelta


LABORABLE_DEFECTO = {"workweek": [1, 2, 3, 4, 5], "holidays": [], "por_defecto": True}


def dias_laborables(a: datetime, b: datetime, cal: dict) -> float:
    """Dias laborables entre dos instantes, con la fraccion del primero y el ultimo.

    Se cuenta por dias y no por horas de jornada a proposito: la jornada no esta
    declarada en ningun sitio y suponerla seria inventar la mitad del numero.
    """
    if b <= a:
        return 0.0
    festivos = set(cal.get("holidays") or [])
    semana = set(cal.get("workweek") or LABORABLE_DEFECTO["workweek"])

    def laborable(d: date) -> bool:
        return d.isoweekday() in semana and d.isoformat() not in festivos

    total, dia = 0.0, a.date()
    while dia <= b.date():
        if laborable(dia):
            ini = max(a, datetime.combine(dia, datetime.min.time(), tzinfo=a.tzinfo))
            fin = min(b, datetime.combine(dia, datetime.max.time(), tzinfo=a.tzinfo))
            total += max(0.0, (fin - ini).total_seconds() / 86400)
        dia += timedelta(days=1)
    return round(total, 2)


def _duracion(inicio, fin) -> float | None:
    """Horas entre dos marcas ISO. None si falta alguna o el orden no cuadra."""
    if not inicio or not fin:
        return None
    try:
        a = datetime.fromisoformat(str(inicio).replace("Z", "+00:00"))
        b = datetime.fromisoformat(str(fin).replace("Z", "+00:00"))
    except ValueError:
        return None
    h = (b - a).total_seconds() / 3600
    # Un comando que sale negativo o que dura mas de un dia es un reloj mal
    # puesto o una marca copiada, no un comando largo. Descartarlo es mejor que
    # dejar que arrastre la media de todo el proyecto.
    return h if 0 <= h <= 24 else None


def atribuir(rit: dict, fases: list, pesos: dict, eventos: dict, cal: dict) -> dict:
    """Por que cada change tardo lo que tardo, con la senal que lo dice.

    El informe ya sabe **cuanto** duro cada change. Lo que faltaba es **por que**,
    y sin eso una desviacion no es accionable: "vamos tres dias tarde" no dice si
    hay que contratar, desbloquear o rehacer specs.

    Dos reglas que sostienen esta seccion, y son las mismas del resto del informe:

    - **Nada se inventa.** Cada causa nombra el dato de la auditoria del que sale.
      Un change lento sin ninguna senal se declara como **hueco**, no se le asigna
      la causa mas plausible. Una causa inventada es peor que un hueco porque se
      actua sobre ella.
    - **Los adelantos se explican igual que los retrasos.** Un change que costo la
      mitad de lo estimado es informacion para la proxima estimacion, y si nadie
      lo mira solo se aprende de lo que sale mal.

    El esfuerzo estimado esta en jornadas de trabajo y el lead time en dias de
    calendario, asi que la comparacion va contra **dias laborables**. Compararlo
    con dias naturales haria que todo change que cruza un fin de semana pareciera
    ir tarde.
    """
    por_fase = {str(f.get("change_hint") or ""): f for f in fases if f.get("change_hint")}
    filas = []
    for m in rit.get("por_change") or []:
        cid = m["change"]
        fase = por_fase.get(cid)
        est = pesos.get(str(fase.get("id"))) if fase else None
        real = m.get("dias_laborables")
        if not est or real is None:
            filas.append({"change": cid, "estimado_dias": est, "real_laborable": real,
                          "sentido": "no comparable",
                          "motivo": ("la fase no declara esfuerzo" if fase and not est
                                     else "el change no esta en el roadmap" if not fase
                                     else "sin dias laborables medidos")})
            continue

        desv = round(real - est, 2)
        # +-25 % es ruido: un change de 3 dias que tarda 3,5 no es un hallazgo, y
        # marcarlo como desviacion llenaria el informe de falsos positivos.
        rel = desv / est
        sentido = ("retrasado" if rel > 0.25 else
                   "adelantado" if rel < -0.25 else "en linea")

        reg = eventos.get(cid) or {}
        causas = []
        if sentido == "retrasado":
            ratio = m.get("ratio_atencion")
            if ratio is not None and ratio < 15:
                causas.append({
                    "senal": "ratio de atencion",
                    "valor": f"{ratio:.1f} %",
                    "dice": ("el change estuvo esperando, no avanzando: de todo el tiempo "
                             "que estuvo abierto solo se trabajo en el esa fraccion. "
                             "Mas gente no acorta una espera")})
            if reg.get("bloqueos_pendientes"):
                causas.append({
                    "senal": "decisiones bloqueantes sin resolver",
                    "valor": str(reg["bloqueos_pendientes"]),
                    "dice": "hubo decisiones que nadie cerro mientras el change estaba vivo"})
            if (reg.get("intentos") or 1) > 1:
                causas.append({
                    "senal": "reintentos del comando",
                    "valor": str(reg["intentos"]),
                    "dice": ("el comando se relanzo sobre el mismo change: las specs no "
                             "estaban listas para ejecutarse a la primera")})
            if reg.get("verde_primera") is False:
                causas.append({
                    "senal": "build o tests en rojo en la primera pasada",
                    "valor": "first_run_green = false",
                    "dice": "hubo que corregir despues de implementar, no antes"})
            if reg.get("correcciones"):
                causas.append({
                    "senal": "correcciones durante la implementacion",
                    "valor": str(reg["correcciones"]),
                    "dice": "el trabajo se desvio de lo especificado y hubo que rectificar"})
            if reg.get("intervenciones"):
                causas.append({
                    "senal": "intervenciones del humano",
                    "valor": str(reg["intervenciones"]),
                    "dice": ("el humano tuvo que redirigir a mitad. Es auto-declarado y no "
                             "se puede contrastar: tomalo como contexto, no como prueba")})
        else:
            if m.get("ratio_atencion") is not None and m["ratio_atencion"] > 40:
                causas.append({
                    "senal": "ratio de atencion",
                    "valor": f"{m['ratio_atencion']:.1f} %",
                    "dice": "el change se trabajo de forma continua, casi sin esperas"})
            if reg.get("verde_primera") is True and (reg.get("intentos") or 1) == 1:
                causas.append({
                    "senal": "verde a la primera",
                    "valor": "sin reintentos",
                    "dice": ("las specs bastaron para implementar sin rectificar. Es lo que "
                             "hay que repetir, y solo se ve mirando los adelantos")})
            if not reg.get("correcciones") and reg.get("pf_dudas"):
                causas.append({
                    "senal": "pre-flight resuelto y sin correcciones despues",
                    "valor": f"{reg['pf_dudas']} dudas antes, 0 correcciones despues",
                    "dice": "preguntar antes evito rectificar durante"})

        filas.append({
            "change": cid, "fase": (fase or {}).get("id"),
            "estimado_dias": est, "real_laborable": real,
            "desviacion_dias": desv,
            "desviacion_pct": round(rel * 100, 1),
            "sentido": sentido,
            "causas": causas,
            "sin_causa": bool(sentido != "en linea" and not causas),
        })

    con_desv = [x for x in filas if x.get("sentido") in ("retrasado", "adelantado")]
    sin_causa = [x["change"] for x in con_desv if x.get("sin_causa")]
    return {
        "changes": filas,
        "retrasados": sum(1 for x in filas if x.get("sentido") == "retrasado"),
        "adelantados": sum(1 for x in filas if x.get("sentido") == "adelantado"),
        "en_linea": sum(1 for x in filas if x.get("sentido") == "en linea"),
        "no_comparables": sum(1 for x in filas if x.get("sentido") == "no comparable"),
        "dias_perdidos": round(sum(x["desviacion_dias"] for x in filas
                                   if x.get("sentido") == "retrasado"), 2),
        "dias_ganados": round(-sum(x["desviacion_dias"] for x in filas
                                   if x.get("sentido") == "adelantado"), 2),
        "sin_causa": sin_causa,
        "umbral": "una desviacion cuenta a partir del 25 % sobre el esfuerzo estimado",
        "base": "dias laborables frente a esfuerzo estimado de la fase",
    }


def acumular_senales(reg: dict, e: dict) -> dict:
    """Pliega en `reg` las senales que trae una entrada de auditoria.

    Existe para que los dos comandos lean **los mismos campos**. Que
    `status-report` mirase `attempt` y `metrics` mirase otra cosa daria dos
    explicaciones distintas del mismo change, y la discusion no seria sobre el
    proyecto sino sobre cual de los dos informes miente.

    Por si solas estas senales no dicen nada; junto a la duracion, si.
    """
    try:
        reg["intentos"] = max(int(reg.get("intentos") or 1), int(e.get("attempt") or 1))
    except (TypeError, ValueError):
        pass
    pf = e.get("preflight") or {}
    for k_src, k_dst in (("bloqueantes", "pf_bloqueantes"), ("total", "pf_dudas"),
                         ("rounds", "pf_rondas")):
        try:
            v = pf.get(k_src)
            if v is not None:
                reg[k_dst] = reg.get(k_dst, 0) + int(v)
        except (TypeError, ValueError):
            pass
    ver = e.get("verification")
    if isinstance(ver, dict):
        # Un solo rojo manda: que una pasada posterior saliera verde no borra
        # que hubo que corregir despues de implementar.
        if ver.get("first_run_green") is False:
            reg["verde_primera"] = False
        elif ver.get("first_run_green") is True:
            reg.setdefault("verde_primera", True)
    try:
        iv = (e.get("self_reported") or {}).get("interventions")
        if iv is not None:
            reg["intervenciones"] = reg.get("intervenciones", 0) + int(iv)
    except (TypeError, ValueError):
        pass
    for dec in e.get("decisions") or []:
        if not isinstance(dec, dict):
            continue
        if dec.get("type") == "correccion":
            reg["correcciones"] = reg.get("correcciones", 0) + 1
        if (dec.get("type") == "bloqueante"
                and str(dec.get("decision", "")).strip().lower() == "pendiente"):
            reg["bloqueos_pendientes"] = reg.get("bloqueos_pendientes", 0) + 1
    return reg


def agregar_desviacion(atr: dict) -> dict:
    """Sube la atribucion por change al nivel del proyecto.

    Es lo que faltaba: `metrics` daba la desviacion global como una cifra
    desnuda, y un `+30 %` no es accionable. Lo accionable es «el 60 % viene de
    tres changes; de esos, dos por decisiones bloqueantes sin resolver».

    No se inventa una explicacion nueva a nivel de proyecto: se **agrega** la
    que ya existe change a change. Y el hueco se agrega igual, porque a esta
    escala **la suma de huecos es en si un dato**: si la mayor parte de la
    desviacion no tiene senal, el problema no es el proyecto, es que la
    auditoria no esta capturando lo que pasa.
    """
    filas = [x for x in (atr.get("changes") or [])
             if x.get("sentido") in ("retrasado", "adelantado")]
    perdidos = round(sum(x["desviacion_dias"] for x in filas
                         if x["sentido"] == "retrasado"), 2)
    ganados = round(-sum(x["desviacion_dias"] for x in filas
                         if x["sentido"] == "adelantado"), 2)

    def reparto(sentido: str, total: float) -> dict:
        de_ese = sorted((x for x in filas if x["sentido"] == sentido),
                        key=lambda x: abs(x["desviacion_dias"]), reverse=True)
        por_causa: dict[str, dict] = {}
        sin_senal = 0.0
        for x in de_ese:
            dias = abs(x["desviacion_dias"])
            if not x.get("causas"):
                sin_senal += dias
                continue
            # Un change con dos causas no cuenta dos veces: los dias se reparten
            # entre ellas. Sumar el change entero a cada causa daria porcentajes
            # que pasan del cien y un informe que no se sostiene.
            parte = dias / len(x["causas"])
            for c in x["causas"]:
                acc = por_causa.setdefault(c["senal"], {"senal": c["senal"], "dias": 0.0,
                                                        "changes": []})
                acc["dias"] += parte
                if x["change"] not in acc["changes"]:
                    acc["changes"].append(x["change"])
        for acc in por_causa.values():
            acc["dias"] = round(acc["dias"], 2)
            acc["pct"] = round(acc["dias"] / total * 100, 1) if total else 0.0
        # Cuantos changes concentran la mitad de la desviacion: es lo que dice
        # si esto es un problema puntual o repartido por todo el proyecto.
        acumulado, concentracion = 0.0, 0
        for x in de_ese:
            if total and acumulado >= total / 2:
                break
            acumulado += abs(x["desviacion_dias"])
            concentracion += 1
        return {
            "dias": total,
            "changes": len(de_ese),
            "por_causa": sorted(por_causa.values(), key=lambda c: -c["dias"]),
            "sin_senal_dias": round(sin_senal, 2),
            "sin_senal_pct": round(sin_senal / total * 100, 1) if total else 0.0,
            "changes_sin_senal": [x["change"] for x in de_ese if not x.get("causas")],
            "changes_que_concentran_la_mitad": concentracion,
            "mayores": [{"change": x["change"], "dias": x["desviacion_dias"],
                         "causas": [c["senal"] for c in x.get("causas") or []]}
                        for x in de_ese[:3]],
        }

    retraso = reparto("retrasado", perdidos)
    adelanto = reparto("adelantado", ganados)
    total_desv = perdidos + ganados
    sin_senal = retraso["sin_senal_dias"] + adelanto["sin_senal_dias"]
    return {
        "retraso": retraso,
        "adelanto": adelanto,
        "sin_senal_pct_global": round(sin_senal / total_desv * 100, 1) if total_desv else 0.0,
        # Por encima de esto el hallazgo deja de ser sobre el proyecto y pasa a
        # ser sobre el registro: no se puede explicar lo que no se anoto.
        "auditoria_insuficiente": bool(total_desv and sin_senal / total_desv > 0.5),
        "base": ("la desviacion se agrega desde la atribucion por change; no se "
                 "calcula ninguna causa nueva a nivel de proyecto"),
    }
