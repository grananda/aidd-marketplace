# Proximos pasos al terminar un comando

> Referencia del skill `aisdd-specs`. El indice y las reglas comunes estan en `SKILL.md`.

## Por que existe

`aidd` y `aiba` encadenan: cada uno de sus comandos termina diciendo cual es el siguiente. AISDD no lo hacia, y es donde mas falta hace — es el bucle donde el usuario pasa la mayor parte del proyecto, y **cual es el siguiente paso depende del estado**, no de una secuencia fija: del modo de faseado, de que changes hay vivos, de si queda una barrera bloqueada, de que lane esta activo y de si existe capa de entrega.

**Todo comando de `aisdd-specs` y `aisdd-amend` cierra con esta seccion**, despues de la verificacion final.

## Reglas

1. **Da comandos ejecutables, con el argumento ya resuelto.** `aisdd implement change portal-catalogo`, no "implementa el change". El usuario tiene que poder copiar y pegar.
2. **Como maximo tres.** Uno principal y hasta dos alternativas o complementos. Una lista larga no es una sugerencia, es un menu.
3. **No sugieras lo que ya esta hecho** ni lo que no puede ejecutarse todavia. Si un comando tiene precondiciones sin cumplir, o lo omites o dices que falta.
4. **Di el porque en media linea** cuando no sea evidente: *"...porque el roadmap cambio y el sprint-plan quedo desalineado"*.
5. **Si no hay siguiente paso claro, dilo.** Es informacion: el roadmap agotado o un bloqueo son estados legitimos.
6. **Un comando que se detiene tambien sugiere.** Es donde mas falta hace: di la duda concreta que bloquea y el mismo comando para relanzarlo una vez resuelta. El paso final no se alcanza en ese camino, asi que la sugerencia va **en el propio punto de parada** (ver "Pre-flight de dudas", `references/preflight.md`, y los limites de `aisdd amend change`).

## Que sugerir, por comando

### `aisdd init`

| Estado | Sugerencia |
|---|---|
| No hay `docs/roadmap.md` | `aisdd roadmap` |
| Ya hay roadmap | `aisdd open change` — el proyecto ya esta faseado |

### `aisdd roadmap`

El roadmap es **insumo de la capa de entrega**, asi que aqui hay una bifurcacion que el usuario no tiene por que conocer:

| Estado | Sugerencia | Por que |
|---|---|---|
| No hay `docs/planificacion-proyecto.md` | `aiba project-plan`, y **despues** `aiba sprint-planning` | Es el orden correcto: sin plan de recursos no hay capacidad contra la que planificar. Aun asi `sprint-planning` **no se detiene** — avisa y puede seguir con supuestos de equipo explicitos, asi que ofrecelo como alternativa si el usuario tiene prisa |
| Hay plan de recursos, no hay `docs/sprint-plan.md` | `aiba sprint-planning` | Ya tiene sus dos insumos: roadmap y recursos |
| Hay `sprint-plan.md` **anterior a este roadmap** | `aiba sprint-planning` otra vez | El faseado ha cambiado y el reparto en sprints quedo desalineado. **Dilo**: re-ejecutarlo es seguro, no recrea Stories |
| Cualquiera | `booster-docs` sobre `docs/roadmap.md` | Vista HTML del roadmap, opcional |

Y siempre, como paso de ejecucion: **`aisdd open change`** (en `multilane`, precedido de `aisdd lane switch <lane-id>` si el lane activo no es el de la primera fase).

### `aisdd open change`

`aisdd implement change <change-slug>`, con el slug del change recien abierto.

### `aisdd implement change`

`aisdd close change <change-slug>`. Si registraste correcciones de **nivel 3 o superior**, nombra ademas el documento AIDD que queda pendiente de actualizar: cerrar sin eso deja el diseno contradiciendo al codigo.

### `aisdd close change`

Es el que mas depende del estado. Resuelve **la siguiente fase abrible** con el mismo criterio que "Resolver el change objetivo (compartido)" (`references/target-change.md`), variante `open change`, y sugiere en consecuencia:

| Situacion | Sugerencia |
|---|---|
| Hay siguiente fase y —en `multilane`— es del lane activo | `aisdd open change` nombrando la fase |
| `multilane`, la siguiente es de **otro lane** | `aisdd lane switch <lane-id>` y despues `aisdd open change` |
| `multilane`, la siguiente es una **barrera** y ya no queda ningun change abierto | `aisdd open change` sobre la barrera — **di que se ha desbloqueado**, porque es el momento que el resto del equipo esperaba |
| `multilane`, la siguiente es una **barrera** pero quedan changes abiertos | **No sugieras abrirla.** Lista que lanes faltan por cerrar: eso es lo accionable |
| Roadmap agotado | Ya no hay fases. Sugiere `aiba metrics` para medir el ciclo completo, y cerrar |

Si existe `docs/sprint-plan.md` y este change completaba las HU comprometidas de un sprint, **dilo**: es el dato que la capa de entrega necesita.

### `aisdd amend change`

`aisdd implement change <change-slug>` si quedan tareas del delta, o `aisdd close change <change-slug>` si ya esta. Si marcaste fases futuras con `amended_by`, **nombralas**: quien las abra tiene que saber que arrastran una enmienda.

### `aisdd lane`

Que se puede hacer en el lane activo: `aisdd open change` si esta libre, `aisdd implement`/`close change <change-slug>` si tiene uno vivo, o las barreras que lo bloquean.

### `aisdd prototype-ux` y `aisdd uml`

Abrir el entregable generado, y volver al ciclo del change: `aisdd implement change <change-slug>`.

## Lo que no se hace

- **No inventes comandos.** Solo los que existen en `aidd`, `aisdd`, `aiba` y los boosters. `aisdd review change` es una **propuesta** del ROADMAP, no un comando.
- **No mandes a nadie a un comando que se va a detener.** Distingue detenerse de degradar, porque no es lo mismo y suprimir una opcion valida deja al usuario sin salida:
  - **Se detienen**: `aisdd roadmap` sin `docs/detalle-historias-usuario.md`, y `aiba functional-design` sin ese mismo fichero. No los sugieras: di que falta y quien lo genera (`aidd user-story-details`).
  - **Degradan**: `aiba sprint-planning` sin `docs/planificacion-proyecto.md` y `aiba project-plan` sin `docs/arquitectura-base.md`. **Si los puedes sugerir**, diciendo con que se degradan.
- **No repitas la verificacion final.** Aqui va lo que el usuario **hace ahora**, no lo que acaba de pasar.
