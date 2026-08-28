# Resolver el change objetivo

> Referencia del skill `aisdd-specs`. El indice y las reglas comunes estan en `SKILL.md`.

## Resolver el change objetivo (compartido)

Lo usan **`aisdd implement change`**, **`aisdd close change`**, **`aisdd uml`** y, en su variante de apertura, **`aisdd open change`**.

**El argumento es opcional en todos.** Nunca lo exijas: si llega, usalo; si no, resuelvelo. Lo que **si** es obligatorio es no elegir por tu cuenta cuando hay mas de un candidato razonable.

### La regla

1. **Si llega el argumento**, usalo y no preguntes nada.
2. **Si no llega, reune los candidatos** (que son, segun el comando, en la seccion siguiente).
3. **Un solo candidato** -> usalo sin preguntar. Dilo en el resumen, para que el usuario sepa sobre que has trabajado.
4. **Varios candidatos** -> **presentalos con su contexto y deja elegir**. Nunca escojas tu, ni por orden alfabetico, ni por fecha, ni por ser el primero de la lista.
5. **Ningun candidato** -> no falles con un error seco: explica por que no hay ninguno y cual es el paso que corresponde.

### Que son los candidatos

| Comando | Candidatos | Si no hay ninguno |
|---|---|---|
| `implement change` | Changes **abiertos** (`openspec list`) | No hay nada que implementar. Remite a `aisdd open change` |
| `close change` | Changes **abiertos**. En `multilane`, **primero los del lane activo**: si ese lane tiene exactamente uno, usalo sin preguntar — que otros lanes tengan trabajo vivo no genera ambiguedad, porque no es tuyo | Nada que archivar. Dilo y para |
| `uml` | Changes **abiertos**, igual que `implement` | Sin change no hay diagramas. Remite a `aisdd open change` |
| `open change` | Fases **abribles ahora** del roadmap (`roadmap.phases` en `config.yaml`): no archivadas y con todas sus `depends_on` cerradas. En `multilane` ademas: las **fases de lane** solo si son del lane activo y ese lane esta libre; las **barreras** (`F0`, `FB-NN`, sin `lane`) solo si **ningun** lane tiene changes abiertos. En `waves` no se filtra por oleada: el ancho `N` no lo comprueba ningun comando | El roadmap esta agotado o todo esta bloqueado. Di **cual** es el bloqueo (barrera pendiente, dependencia sin cerrar, lane ocupado) |

### Por que esto importa mas con paralelismo

En `atomic` con un solo change vivo, resolver es trivial. **En `waves` y en `multilane`, varios changes abiertos es el caso normal, no la excepcion** — es el proposito de esos modos. Preguntar "cual de estos" sin mas contexto le traslada al usuario un trabajo de correlacion que tu ya tienes hecho: el sabe en que esta trabajando, pero no necesariamente que slug le corresponde ni que fase es de quien.

### Como presentar las opciones

Usa **`AskUserQuestion`** si la plataforma lo soporta, con una opcion por candidato. Si no, lista numerada en texto plano.

Cada opcion lleva, ademas del slug o el id de fase, **el contexto que permite reconocerlo sin abrir nada**:

| Modo | Contexto que anadir a cada opcion |
|---|---|
| `atomic` | Fase del roadmap y objetivo en una linea |
| `waves` | Lo anterior **+ oleada** (`Oleada 2`) y las fases de las que depende |
| `multilane` | Lo anterior **+ lane** (`lane: api`) y si es el lane activo del dev |

Marca `(Recomendada)` cuando tengas criterio real:

- **En `multilane`**, el candidato del **lane activo**.
- **En `waves`**, el de la **oleada mas baja** que siga abierta.
- **En `atomic`**, el mas antiguo, porque tenerlo abierto bloquea el resto.

Si no tienes criterio, no marques ninguna: una recomendacion inventada es peor que ninguna.

### Lo que no se hace

- **No elijas en silencio.** Un change equivocado en `implement` escribe codigo donde no toca; en `close` archiva trabajo sin terminar.
- **No pidas el slug a ciegas.** Preguntar "que change quieres implementar?" sin listar los abiertos obliga al usuario a ir a buscarlo.
- **No inventes candidatos.** Solo lo que devuelve `openspec list` o lo que declara `roadmap.phases`.
- **En modo no interactivo**, con varios candidatos y sin poder preguntar, **detente** y lista los candidatos en el resumen. Escribe la entrada de auditoria con `status: aborted` (ver `references/audit.md`). Elegir por defecto es exactamente el error que esta seccion existe para evitar.
