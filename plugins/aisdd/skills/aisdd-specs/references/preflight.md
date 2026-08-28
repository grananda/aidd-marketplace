# Pre-flight de dudas

> Referencia del skill `aisdd-specs`. El indice y las reglas comunes estan en `SKILL.md`.

## Pre-flight de dudas (compartido)

Lo usan **`aisdd open change`** e **`aisdd implement change`**. Antes de generar los specs (**[APERTURA]**) o de aplicar las instrucciones de OpenSpec (**[IMPLEMENTACION]**), revisa el contexto y resuelve ambiguedades con el usuario. Esta fase es **obligatoria** en ambos comandos. Lo que difiere entre usos va marcado; el resto aplica igual a los dos.

### 1. Contexto a leer primero

**[APERTURA]** — antes de crear el cambio:

- Objetivo declarado por el usuario y `<what-you-want-to-build>` si llega.
- Documentacion del proyecto: `docs/` (en especial `docs/roadmap.md` si existe), `README.md`, `config.yaml`, `AGENTS.md`, `CLAUDE.md`.
- Cambios OpenSpec previos en `openspec/changes/` y especificaciones en `openspec/specs/` que toquen el mismo dominio funcional.

**[IMPLEMENTACION]** — artefactos del cambio:

- `openspec/changes/<change>/design.md`, `proposal.md` y todos los `specs/**/spec.md`.
- Si existen, `tasks.md` y `decisions.md` (decisiones previas del mismo cambio).

### 2. Clasifica las dudas reales

- **bloqueante**: sin respuesta no se puede avanzar. Modelo de datos, contrato de API, autenticacion, integraciones externas, migraciones, permisos; ademas, **[APERTURA]** alcance funcional, dominios afectados y criterios de aceptacion principales.
- **preferencia**: hay varias opciones validas y la elegida condiciona el resultado (libreria, patron, naming, ubicacion del fichero; **[APERTURA]** tambien la particion en uno o varios changes).
- **confirmacion**: parece claro pero conviene validar antes de redactar o codificar (actores, canales, plataformas soportadas).

### 3. No preguntes lo que ya esta resuelto

Comun a ambos:

- Convenciones documentadas en el repo (`README.md`, `CLAUDE.md`, `AGENTS.md`, `docs/`, `config.yaml`).
- Elecciones triviales y facilmente reversibles (nombres internos, formato de log).

**[APERTURA]**:

- Objetivo y alcance explicitos del usuario o del prompt del roadmap.
- **El faseado del roadmap y el reparto en sprints**: que HU entran en este change ya esta decidido (fase + sprint). **No ofrezcas adelantar HU de otras fases** ni ampliar el alcance — no es una duda, es una decision ya tomada (ver "El faseado es normativo"). Las dudas de alcance legitimas son sobre el **COMO** de las HU de esta fase, no sobre el QUE ni el CUANDO.
- Puntos ya cubiertos por specs OpenSpec previas o por cambios relacionados ya cerrados.
- **En modo `multilane`, las enmiendas ya registradas**: si la fase trae `amended_by`, ese delta es una decision tomada. Incorporalo (paso "Enmiendas pendientes de esta fase" de `open change`) en vez de preguntarlo.
- **En modo `multilane`, el contrato compartido**: esquema de datos, contrato de API, eventos y tipos compartidos quedaron fijados en `F0` o en una barrera. **No los renegocies en el pre-flight de una fase de lane** — leelos de las specs archivadas y trabaja contra ellos. Si el contrato resulta insuficiente, eso no es una duda de pre-flight: es un fallo de faseado. Detente, dilo, y remite al dueno del contrato (`roadmap.contract_owner`) y a una barrera.

**[IMPLEMENTACION]**:

- Decisiones cerradas en `design.md` o `proposal.md`.
- Puntos ya cubiertos por entradas previas de `decisions.md`.

### 4. Presupuesto de preguntas

Lee la seccion **`preflight`** de `openspec/config.yaml` (ver "Configuracion del pre-flight"). Con ella, selecciona que dudas se presentan al usuario, **en este orden**:

1. **Todas las dudas `bloqueante` reales, sin limite.** No se descartan, no se agrupan hasta desdibujarlas y no se sustituyen por una recomendacion automatica. Una bloqueante es, por definicion, aquella sin la cual no puedes producir un spec solido: caparlas cambia correccion por comodidad.
2. Hasta el valor de `preferencias` en dudas `preferencia`, **ordenadas por impacto**. Con `all`, todas.
3. Hasta el valor de `confirmaciones` en dudas `confirmacion`, ordenadas por impacto. Con `all`, todas.
4. Las `preferencia` y `confirmacion` que queden fuera del limite **no se pierden**: aplica el default recomendado y registralas en `decisions.md` con `Origen: auto-default`.

**Pregunta solo dudas reales.** El limite es un techo, nunca una cuota: si hay una duda, pregunta una; si no hay ninguna, no preguntes nada (ver el punto 9 de esta seccion). Nunca rellenes el presupuesto con asuntos ya decididos ni con confirmaciones triviales.

**Limite de la interfaz.** Si la plataforma no admite tantas preguntas en una sola interaccion (por ejemplo `AskUserQuestion`, que acepta unas pocas por llamada), **divide en tandas consecutivas**. Nunca omitas una duda bloqueante por ese limite: es un limite de presentacion, no de contenido.

### 5. Formato de las preguntas

- Si la plataforma soporta preguntas estructuradas con opciones (por ejemplo `AskUserQuestion` en Claude Code), usalo con 2-4 opciones y marca una como `(Recomendada)` cuando tengas criterio.
- En caso contrario, lista numerada en texto plano, con opciones `a)`, `b)`, `c)` y una recomendacion explicita.
- Cada duda incluye: **contexto breve** (**[APERTURA]** objetivo del usuario o seccion del roadmap/docs; **[IMPLEMENTACION]** donde aparece en el spec), **por que** se necesita la respuesta y **que impacto** tiene (**[APERTURA]** en los specs; **[IMPLEMENTACION]** en la implementacion).

### 6. Modo no interactivo

Auto mode, CI, sin terminal, o el usuario pide no ser interrumpido:

- No bloquees el comando por dudas no bloqueantes.
- Toma el default recomendado para cada `preferencia` y `confirmacion`, y marcalo `Origen: auto-default` en `decisions.md`.
- Para `bloqueantes` sin default seguro, **detente** y reporta las dudas pendientes; no ejecutes el comando OpenSpec (**[APERTURA]** `openspec new change`; **[IMPLEMENTACION]** `openspec instructions apply`). **Antes de terminar, di como desbloquear**: la duda concreta que falta por resolver y el mismo comando para relanzarlo una vez resuelta. Detenerse sin decir por donde seguir deja al usuario adivinando. Y **escribe la entrada de auditoria con `status: aborted`** y las dudas bloqueantes pendientes en `errors`: detenerse es un resultado del comando y tiene que quedar registrado igual que completarlo. Es el unico caso en el que la entrada no se escribe en el paso final del comando, porque ese paso no llega a ejecutarse.

### 7. Persistencia

Graba todas las respuestas en `openspec/changes/<change>/decisions.md`, una entrada por decision.

**[APERTURA]**: en ese momento el cambio aun no existe en disco. Crea el directorio `openspec/changes/<change>/` antes de escribir, o guarda las decisiones en un buffer y vuelcalas inmediatamente despues de `openspec new change` y antes de redactar `design.md`, `proposal.md` y los `spec.md`.

**[IMPLEMENTACION]**: crea el fichero si no existe.

```markdown
## <slug-de-la-decision>

- **Fecha**: <YYYY-MM-DD>
- **Tipo**: bloqueante | preferencia | confirmacion
- **Origen**: usuario | auto-default
- **Contexto**: <[APERTURA] objetivo del usuario / docs/roadmap.md / spec previa | [IMPLEMENTACION] design.md / proposal.md / spec.md, seccion o linea>
- **Pregunta**: <pregunta planteada>
- **Opciones evaluadas**:
  - a) <opcion>
  - b) <opcion>
- **Decision**: <opcion elegida>
- **Justificacion**: <una linea con el motivo>
```

### 8. Dudas aplazadas

Si el usuario rechaza responder o pide aplazar, registra `Decision: pendiente`. Si era **bloqueante**, detente sin ejecutar el comando OpenSpec, informa de las dudas pendientes y termina. **Antes de terminar, di como desbloquear**: la duda concreta que falta por resolver y el mismo comando para relanzarlo una vez resuelta. Detenerse sin decir por donde seguir deja al usuario adivinando. Y **escribe la entrada de auditoria con `status: aborted`** y las dudas bloqueantes pendientes en `errors`: detenerse es un resultado del comando y tiene que quedar registrado igual que completarlo. Es el unico caso en el que la entrada no se escribe en el paso final del comando, porque ese paso no llega a ejecutarse.

### 9. Sin dudas

Si tras la lectura inicial no detectas dudas reales, registra una unica entrada con `Tipo: confirmacion`, `Pregunta: No se detectaron dudas durante el pre-flight` y `Decision: continuar`. **No fuerces preguntas artificiales** solo por cumplir el flujo.

### 10. Cierre

Resume al usuario el conjunto de decisiones tomadas y confirma el siguiente paso: **[APERTURA]** que esas decisiones se reflejaran en `design.md`, `proposal.md` y los `spec.md`; **[IMPLEMENTACION]** que puede arrancar `openspec instructions apply`.

### Configuracion del pre-flight

Cuanto pregunta el pre-flight **se configura por proyecto**, porque el nivel adecuado no es el mismo en un dominio nuevo que en un repo que el equipo lleva meses tocando. Vive en `openspec/config.yaml`, junto al resto de la configuracion del skill:

```yaml
preflight:
  preferencias: all      # all | entero >= 0
  confirmaciones: all    # all | entero >= 0
```

- **`all`** (default): se plantean todas las dudas de ese tipo.
- **Un entero**: se plantean como maximo esas; el resto se resuelve con el default recomendado y queda registrado como `auto-default`.
- **`0`**: no se plantea ninguna de ese tipo; todas se auto-resuelven y se registran.

Reglas:

1. **Estas claves no afectan a las bloqueantes.** No hay forma de configurar que una bloqueante no se pregunte: si existiera, el comando podria generar specs sobre huecos conocidos.
2. Si falta la seccion `preflight`, si falta una clave o si su valor no es valido, **usa `all`** para lo que falte y **avisa en una linea** para que el usuario pueda corregirlo. No bloquees por configuracion.
3. `aisdd init` siembra la seccion con los valores por defecto (ver `aisdd init`). Si no esta, el pre-flight funciona igual.
