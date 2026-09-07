#!/usr/bin/env python3
"""Las versiones acompanan a lo que cambia, y los README a sus SKILL.

Existe porque la regla escrita no basto. El commit `81fa321` modifico
diecinueve `SKILL.md` --les metio el bloque entero sobre resolver
`${CLAUDE_PLUGIN_ROOT}`-- y subio una sola version: dieciocho skills cambiaron
de comportamiento y siguen anunciando la version de antes. Quien tiene el
marketplace instalado no tiene forma de saber que le toca reinstalar.

Mira **solo lo que toca el PR**, que es la unica pregunta que se puede
responder sin discutir: si en esta rama cambiaste un skill, su version cambia en
esta rama. La deriva vieja no la toca; se corrige sola segun se vaya tocando
cada skill.

Las cuatro reglas:

1. Si cambia cualquier fichero versionado, cambia `VERSION`. Es lo que dispara
   el release: `release.yml` solo publica si la etiqueta `v<VERSION>` no existe,
   asi que un merge sin subirla no publica nada **y tampoco falla**.
2. Si cambia el `SKILL.md` de un skill o algo de sus `scripts/`, cambia su
   `metadata.version`. Un README retocado no cuenta: no cambia lo que el skill
   hace.
3. Si algun skill de un plugin necesita bump, o cambian los scripts comunes del
   plugin, cambia la version de su `plugin.json`.
4. Si cambia un `SKILL.md` que **tiene** README, cambia tambien el README. No
   obliga a crear los que faltan; obliga a que el que existe no mienta.

Uso:  python3 .github/scripts/check_versions.py [base]     # base: origin/main
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def sh(*args: str) -> str:
    return subprocess.run(args, cwd=RAIZ, capture_output=True, text=True).stdout


def en(ref: str, ruta: str) -> str | None:
    """El contenido de un fichero en una referencia, o None si no existia."""
    r = subprocess.run(["git", "show", f"{ref}:{ruta}"],
                       cwd=RAIZ, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def version_skill(texto: str | None) -> str | None:
    if not texto:
        return None
    m = re.search(r'^\s*version:\s*"([^"]+)"', texto, re.M)
    return m.group(1) if m else None


def version_plugin(texto: str | None) -> str | None:
    if not texto:
        return None
    try:
        return json.loads(texto).get("version")
    except json.JSONDecodeError:
        return None


def cambia(base: str, ruta: str, extractor) -> bool:
    """True si el valor que extrae `extractor` es distinto entre base y HEAD."""
    return extractor(en(base, ruta)) != extractor(en("HEAD", ruta))


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    if subprocess.run(["git", "rev-parse", "--verify", base],
                      cwd=RAIZ, capture_output=True).returncode != 0:
        print(f"No existe la referencia base '{base}'; no hay nada que comparar.")
        return 0

    ficheros = [f for f in sh("git", "diff", "--name-only",
                              f"{base}...HEAD").splitlines() if f]
    if not ficheros:
        print("Sin cambios respecto a la base.")
        return 0

    errores: list[str] = []

    # 1. VERSION acompana a cualquier cambio.
    if "VERSION" not in ficheros:
        errores.append(
            f"VERSION sigue en {en('HEAD', 'VERSION').strip()} y el PR cambia "
            f"{len(ficheros)} fichero(s). Sin subirla no se publica release, y el "
            "CI no falla por su cuenta: el cambio se queda en main sin llegar a nadie.")

    # 2. Los skills tocados suben su version.
    skills_con_bump_pendiente: set[str] = set()
    for skill in sorted({"/".join(f.split("/")[:4]) for f in ficheros
                         if re.match(r"plugins/[^/]+/skills/[^/]+/", f)}):
        propios = [f for f in ficheros if f.startswith(skill + "/")]
        sustantivos = [f for f in propios
                       if f.endswith("/SKILL.md") or "/scripts/" in f]
        if not sustantivos:
            continue  # solo se toco el README: no cambia lo que el skill hace
        if not cambia(base, f"{skill}/SKILL.md", version_skill):
            errores.append(
                f"{skill}: cambia {', '.join(Path(f).name for f in sustantivos)} "
                f"pero metadata.version sigue en {version_skill(en('HEAD', skill + '/SKILL.md'))}.")
            skills_con_bump_pendiente.add(skill)

        # 4. El README que existe no se queda atras.
        readme = f"{skill}/README.md"
        if f"{skill}/SKILL.md" in ficheros and en("HEAD", readme) is not None \
                and readme not in ficheros:
            errores.append(
                f"{skill}: cambia el SKILL.md y su README.md no. Si divergen, el "
                "skill hace una cosa y el repo promete otra.")

    # 3. Los plugins tocados suben la suya.
    for plugin in sorted({"/".join(f.split("/")[:2]) for f in ficheros
                          if f.startswith("plugins/")}):
        propios = [f for f in ficheros if f.startswith(plugin + "/")]
        if not [f for f in propios
                if f.endswith("/SKILL.md") or "/scripts/" in f
                or "/.claude-plugin/" in f]:
            continue
        manifiesto = f"{plugin}/.claude-plugin/plugin.json"
        if en("HEAD", manifiesto) is None:
            continue
        if not cambia(base, manifiesto, version_plugin):
            errores.append(
                f"{plugin}: cambia contenido del plugin pero su plugin.json sigue "
                f"en {version_plugin(en('HEAD', manifiesto))}.")

    if errores:
        print("Versiones que no acompanan al cambio:\n")
        for e in errores:
            print(f"  - {e}")
        print("\nRegla: la version global siempre, y la del skill o el plugin solo")
        print("cuando cambia ese skill o ese plugin concreto. Ver AGENTS.md.")
        return 1

    print(f"Versiones al dia para los {len(ficheros)} fichero(s) del PR.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
