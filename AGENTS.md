# AGENTS.md

Instrucciones para agentes que trabajan en este repositorio.

## Flujo de trabajo (obligatorio)

Nada se toca directamente sobre `main`. El ciclo es siempre este, y **cada paso
espera a que el humano lo apruebe** antes de pasar al siguiente:

1. **Issue primero.** Antes de escribir codigo, abre un issue en GitHub con la
   tarea: que problema hay, que se propone hacer y como se sabra que esta bien.
   El issue es donde se discute el *que*; el PR, el *como*.
2. **Rama nueva, cuando el humano aprueba el issue.** No empieces a trabajar por
   tu cuenta porque el issue ya este escrito: el visto bueno es una senal
   explicita del humano. Con ella, rama a partir de `main`.
3. **Los commits van siempre a un PR en draft.** Abre el PR **en borrador** con
   el primer commit --no al final-- y enlaza el issue. Trabajar en draft es lo
   que hace que el humano pueda ver el avance y cortar a tiempo si va por mal
   camino; un PR que aparece terminado ya no se puede redirigir.
4. **Sube la version en el propio PR.** Todo cambio que entre en `main` tiene
   que traer version nueva en el fichero `VERSION` de la raiz, y en el
   `plugin.json` de cada plugin que hayas tocado. **Es lo que dispara el
   release**: `release.yml` corre en cada push a `main` pero solo publica si la
   etiqueta `v<VERSION>` no existe todavia, asi que un merge sin subir `VERSION`
   **no publica nada y no falla** --el cambio se queda en `main` sin llegar a
   quien tiene el marketplace instalado, y nadie se entera--. No lo dejes para
   despues del merge: la version viaja en el mismo PR que el cambio.
   > `validate.yml` solo caza el caso de un `plugin.json` subido con `VERSION`
   > sin subir. Un cambio que no toque ningun `plugin.json` --documentacion,
   > scripts de `.github/`-- pasa el CI en verde sin release. Ese es tuyo.

5. **Draft a final y merge, solo cuando el humano lo diga.** No marques el PR
   como listo ni lo mergees por iniciativa propia, ni siquiera con el CI en
   verde y todo el trabajo hecho. Esa decision es del humano, siempre.

Si el humano pide saltarse un paso, se salta ese paso y no los demas.

## Convenciones del repositorio

- **Los commits y los PR van en espanol**, con prefijo `feat(<plugin>)`,
  `fix(<plugin>)` o `docs`. El titulo dice el efecto para quien usa el skill, no
  el fichero que se ha tocado.
- **Tres versiones, no una** (ver el paso 4): la del `SKILL.md` que hayas
  tocado, la del `plugin.json` de su plugin y la de `VERSION`. Semver sobre el
  efecto para quien usa el skill: comportamiento nuevo es `minor`, una averia
  corregida es `patch`.
- **Los `SKILL.md` se escriben sin acentos**, por compatibilidad entre
  plataformas de agentes. La regla es del codigo fuente: **el contenido que
  generan los skills --un `.docx` que firma un cliente-- va en espanol correcto,
  con sus tildes.**
- **`SKILL.md` y `README.md` de un skill se cambian juntos.** El README es lo que
  lee una persona y el SKILL lo que lee el agente; si divergen, el skill hace una
  cosa y el repo promete otra.
- **CI:** `.github/workflows/validate.yml` corre los `check_*.py` de
  `.github/scripts/` en cada PR. Ejecuta localmente el que cubra tu cambio antes
  de empujar.
