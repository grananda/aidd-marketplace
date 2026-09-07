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
4. **Sube las versiones en el propio PR, y actualiza los README.** No lo dejes
   para despues del merge: viajan en el mismo PR que el cambio.

   La regla de las versiones es una y tiene dos mitades:

   - **`VERSION`, la global, sube siempre**, y **en la medida de lo cambiado**:
     una averia corregida es `patch`, comportamiento nuevo es `minor`. **Es lo
     que dispara el release**: `release.yml` corre en cada push a `main` pero
     solo publica si la etiqueta `v<VERSION>` no existe, asi que un merge sin
     subirla **no publica nada y tampoco falla** --el cambio se queda en `main`
     en verde sin llegar a quien tiene el marketplace instalado--.
   - **La del skill y la de su plugin suben solo cuando cambia ese skill o ese
     plugin concreto.** No se tocan las de los demas. Y a la inversa: si tocas
     un skill, su `metadata.version` sube, aunque el cambio te parezca menor.
     Retocar solo un README no cuenta: no cambia lo que el skill hace.

   **Y el README acompana al `SKILL.md`.** Si el skill tiene `README.md` --seis
   de treinta y cinco lo tienen-- y cambias su `SKILL.md`, cambias tambien el
   README: el README es lo que lee una persona y el `SKILL.md` lo que lee el
   agente, y cuando divergen el skill hace una cosa y el repo promete otra. Si
   el cambio altera lo que el marketplace promete, toca ademas el `README.md`
   de la raiz y la `description` del `plugin.json`.

   > Esto lo vigila `check_versions.py` en cada PR, y no por gusto: el commit
   > `81fa321` modifico diecinueve `SKILL.md` --les metio el bloque entero sobre
   > resolver `${CLAUDE_PLUGIN_ROOT}`-- y subio una sola version. Dieciocho
   > skills cambiaron de comportamiento y siguen anunciando la version de antes.
   > La regla escrita ya existia; lo que faltaba era quien la comprobara.

5. **Draft a final y merge, solo cuando el humano lo diga.** No marques el PR
   como listo ni lo mergees por iniciativa propia, ni siquiera con el CI en
   verde y todo el trabajo hecho. Esa decision es del humano, siempre.

Si el humano pide saltarse un paso, se salta ese paso y no los demas.

## Convenciones del repositorio

- **Los commits y los PR van en espanol**, con prefijo `feat(<plugin>)`,
  `fix(<plugin>)` o `docs`. El titulo dice el efecto para quien usa el skill, no
  el fichero que se ha tocado.
- **Los `SKILL.md` se escriben sin acentos**, por compatibilidad entre
  plataformas de agentes. La regla es del codigo fuente: **el contenido que
  generan los skills --un `.docx` que firma un cliente-- va en espanol correcto,
  con sus tildes.**
- **CI:** `.github/workflows/validate.yml` corre los `check_*.py` de
  `.github/scripts/` en cada PR. Ejecuta localmente el que cubra tu cambio antes
  de empujar; `check_versions.py` acepta la base como argumento
  (`python3 .github/scripts/check_versions.py main`).
