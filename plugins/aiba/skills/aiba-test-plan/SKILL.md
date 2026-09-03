---
name: aiba-test-plan
description: AIBA (AI Business Analyst) — genera el Plan de Pruebas de cada historia de usuario, mediante el comando `aiba test-plan [HU-XX]` (alias `aiba plan-pruebas`, `aiba pruebas`). Actua como analista de QA que lee `docs/detalle-historias-usuario.md` como fuente de verdad —y el Diseno Funcional de `docs/df/` cuando existe, que es mejor fuente porque sus validaciones y mensajes ya son casos de prueba— y produce dos entregables por HU en `docs/pruebas/`: un `.xlsx` con el inventario de casos (Hoja de Control, Especificaciones con las diecisiete columnas de la plantilla de referencia, Parametros de nomenclatura, rejilla de Ejecucion, exportacion a Qmetry y Resumen con KPIs vivos) y un `.docx` de evidencias con un bloque por caso listo para adjuntar la captura. Cubre el nivel Pruebas de Sistema-Funcionales, que es el que se deriva de los criterios de aceptacion; no inventa unitarias ni de integracion. Cada caso lleva codigo estable `PS.FU.CU01.01`, marca de ejecucion manual o automatizable —que dimensiona el trabajo de cada regresion— y el change del roadmap al que pertenece, para que el Outcome Validator sepa que casos le tocan al cerrar cada change. El diseno es generico y sin marca: usa estilos nativos de Word y de Excel para que una paleta corporativa y un logo se apliquen despues sin rehacer nada, y pregunta antes si se desea aplicar una marca. Funciona sobre todas las HU o una sola. Genera el plan; no ejecuta las pruebas. Usar cuando el usuario pida "genera el plan de pruebas", "casos de prueba de la HU-06", "documento de evidencias", "plan de testing", o equivalentes.
metadata:
  author: NTT DATA Spain GDN-e
  version: "0.1.0"
---

# aiba-test-plan (AIBA · Plan de Pruebas)

Usa este skill cuando el usuario quiera generar o actualizar el **plan de pruebas** de una o varias historias de usuario ya detalladas. Comandos:

- `aiba test-plan [HU-XX]`
- Alias: `aiba plan-pruebas [HU-XX]`, `aiba pruebas [HU-XX]`

Responde y documenta en espanol. Conserva en ingles nombres de comandos, ficheros, rutas y terminos tecnicos establecidos.

## Que es AIBA y donde encaja este skill

**AIBA** (AI Business Analyst) es el conjunto de skills que da la cara ante el negocio. Su metodologia esta en `${CLAUDE_PLUGIN_ROOT}/methodology/native-ai-aiba.md` (referencia de solo lectura). Este skill produce el **inventario de lo que hay que probar** y el documento donde se recoge la evidencia de haberlo probado.

**Consume lo que producen AIDD y AIBA**, y no los sustituye:

| Produce | Skill | Este skill lo usa para |
|---|---|---|
| `docs/detalle-historias-usuario.md` | `aidd user-story-details` | **Fuente de verdad**: cada criterio de aceptacion Dado/Cuando/Entonces es un caso de prueba |
| `docs/df/*.docx` | `aiba functional-design` | **Mejor fuente cuando existe**: validaciones, mensajes y pantallas ya son casos casi literales |
| `docs/requisitos.md` | `aidd requirements` | Los RF/NFR que cada caso traza |
| `docs/mapa-historias-usuario.md` | `aidd user-stories` | Persona y fase, para agrupar |
| `docs/arquitectura-base.md` | `aidd architecture` | Integraciones y estrategia de testing, de donde sale la marca automatizable |
| `docs/roadmap.md` | `aisdd roadmap` | El `change_hint` de la fase que implementa la HU |

Criterio de salida: existen los dos ficheros por cada HU solicitada en `docs/pruebas/`, cada caso tiene codigo, criticidad, pasos y resultado esperado, y ningun caso se ha inventado sin un criterio de aceptacion o una regla del DF que lo sostenga.

## Que hace y que no

**Genera el plan. No ejecuta nada.** Este comando corre en tiempo de diseno, cuando el codigo puede no existir todavia. Quien ejecuta es otro:

| Quien | Cuando | Con que |
|---|---|---|
| **Outcome Validator** | En `aisdd close change`, antes de archivar | El inventario como checklist de la validacion |
| **El humano** (AIAD) | Mientras implementa | `aiad test` sobre los casos marcados como automatizables |
| **Un tester de QA** | Campana de pruebas formal | El `.xlsx` y el documento de evidencias |

Recoger los resultados de vuelta no es trabajo de este skill y hoy no lo hace nadie. Lo que este skill deja preparado para el dia que se haga son dos datos: el **codigo del caso**, estable y unico, y **el change al que pertenece**.

## Reglas generales

- Trabaja desde la raiz del proyecto del usuario.
- **La fuente de verdad es `docs/detalle-historias-usuario.md`.** Si no existe, detente y propon ejecutar antes `aidd user-story-details`: sin criterios de aceptacion no hay nada que convertir en casos.
- **No inventes casos.** Cada caso sale de un criterio de aceptacion, de una validacion del DF o de un requisito. Un plan inflado con casos plausibles cuesta tiempo real de ejecucion a alguien.
- **No modifiques los documentos de AIDD.** Este skill lee `docs/` y escribe **solo** en `docs/pruebas/`.
- **Un plan por HU.** Se revisa y se cierra por historia, igual que el DF.
- **Solo `Pruebas de Sistema-Funcionales`.** Los criterios de aceptacion de una historia son eso. Derivar unitarias o de integracion desde una HU es inventar: las unitarias las escribe quien conoce el codigo, no quien lee la historia.
- **Un solo manifiesto para los dos ficheros.** El `.xlsx` y el `.docx` se generan del mismo JSON, para que no puedan describir cosas distintas.
- **Sin marca por defecto**, salvo que el usuario pida lo contrario en el paso 1.
- Los dos ficheros son el entregable; **no** hay un `.md` intermedio. La fuente sigue siendo el detalle de HU.

## Flujo del comando

### 1. Marca corporativa (preguntar SIEMPRE, antes de generar nada)

Antes de leer documentacion o generar ficheros, **pregunta al usuario si quiere aplicar una marca**. Es lo primero porque condiciona los dos formatos y porque rehacer veinte planes por no haber preguntado es caro.

Usa `AskUserQuestion` si la plataforma lo soporta, con estas opciones:

1. **Sin marca `(Recomendada)`** — estilos nativos, paleta gris legible al imprimir. Queda listo para que cualquiera le aplique despues su identidad sin rehacerlo.
2. **Marca desde una carpeta local** — pide la ruta y busca el logo (`.png`, `.jpg`) y, si existe, tokens o guia de estilos de donde extraer los colores.
3. **Marca desde una URL** — pide la URL corporativa o de la guia de marca, y extrae de ahi el logo y los colores dominantes.

Si elige 2 o 3, pide ademas **color principal**, **color secundario** y **texto de cabecera y pie**. Confirma lo detectado antes de usarlo.

En modo no interactivo, toma **sin marca** y registralo como supuesto.

> **Por que el default es sin marca.** Un plan de pruebas acaba en manos de un cliente que tiene su propia identidad. Generarlo con la marca de quien lo escribe obliga a rehacerlo; generarlo neutro pero bien estructurado permite aplicar cualquier identidad en minutos, porque los colores viven en los estilos.
>
> **El logo en el Excel necesita Pillow**, que `openpyxl` no arrastra. Si falta, el fichero sale sin logo y con un aviso; los colores si se aplican. Dilo al presentar el resultado en vez de dejarlo pasar.

### 2. Recopilacion de contexto

Lee y consolida, en este orden:

1. `docs/detalle-historias-usuario.md` — la HU, su prioridad, sus criterios de aceptacion Dado/Cuando/Entonces, los marcados como imprescindibles, y sus notas tecnicas.
2. **`docs/df/*.docx` de esa HU, si existe** — es mejor fuente que los criterios: sus tablas de validaciones, mensajes y campos son casos de prueba casi literales, y sus puntos abiertos dicen que **no** se puede probar todavia. Un `.docx` no se lee de un vistazo, asi que **volcalo a JSON primero**:

> **Antes de ejecutar cualquiera de estos scripts, comprueba que la ruta resuelve.** `${CLAUDE_PLUGIN_ROOT}` la define Claude Code; **otros agentes la dejan vacia**, y entonces la orden se convierte en `/skills/...` y falla con `No such file or directory`. Si eso pasa, el script **sigue estando en el disco**: localizalo una vez con `find` --por ejemplo en `~/.claude/plugins` o en el directorio de plugins del agente que uses--, quedate con la **ruta absoluta** y usala en todas las invocaciones de esta sesion. Si no aparece, aplica la degradacion descrita mas abajo: haz el trabajo segun la prosa y dilo. **Nunca des por hecho que se ejecuto un script que no ejecutaste.**

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/aiba-functional-design/scripts/gen_df_docx.py" \
     --extraer "docs/df/<fichero>.docx"
   ```

   Devuelve las secciones con sus parrafos y sus tablas. Las que mas dan: *Filtros/Campos*, *Validaciones* (frontal y core), *Mensajes y avisos*, y *Puntos abiertos*. Si el volcado falla, sigue con los criterios de aceptacion y **dilo** en el resumen: el plan sale con menos base.
3. `docs/requisitos.md` — los RF/NFR que la HU realiza, para rellenar `Requisitos relacionados`.
4. `docs/mapa-historias-usuario.md` — persona y fase.
5. `docs/arquitectura-base.md` — su estrategia de testing y su stack, de donde sale la marca de automatizable.
6. `docs/roadmap.md`, si existe — el `change_hint` de la fase que implementa la HU.

Si falta el detalle de HU, **detente**. Si faltan los demas, avisa de que se genera con menos base y sigue.

### 3. Seleccion de historias

- **Sin argumento**: genera el plan de **todas** las HU del detalle. Antes de escribir nada, **lista las que va a generar y espera confirmacion** — treinta historias son sesenta ficheros.
- **Con `HU-XX`**: solo esa. Si el identificador no existe, dilo y lista los validos.
- **Si los ficheros ya existen**, no los pises: ve a "Reedicion".

### 4. Derivar los casos de prueba

**Agrupa primero en casos de uso.** Un caso de uso es una interaccion completa del usuario con la historia: entrar y ver, editar y guardar, cancelar. Salen de agrupar los criterios de aceptacion que comparten pantalla y proposito. Nombralos `CU01`, `CU02`... por orden de flujo, no por orden de aparicion en el documento.

**Despues, un caso de prueba por comportamiento verificable.** De cada criterio salen normalmente varios:

| De donde | Caso |
|---|---|
| El camino feliz del criterio | El que confirma que la funcionalidad hace lo que promete |
| Cada validacion o mensaje de error | Uno por regla: formato invalido, campo obligatorio vacio, limite superado |
| Cada integracion que puede fallar | El error tecnico del backend, el timeout, el dato que no existe |
| Cada permiso o rol distinto | Lo que ve y lo que no ve cada perfil |

**Cada caso lleva, sin excepcion:** nombre que describe lo que verifica (no "Probar la pantalla"), descripcion, precondiciones, pasos numerados y resultado esperado concreto y comprobable. Un resultado esperado que diga "funciona correctamente" no sirve para ejecutar ni para discutir.

**Criticidad**: `Alta` si el criterio esta marcado como imprescindible o si su fallo bloquea el flujo; `Media` por defecto; `Baja` para lo cosmetico.

**Marca de ejecucion**: `automatizable` si el caso es determinista y no necesita juicio humano ni datos que solo existen en un entorno concreto; `manual` en lo demas. Derivala de la estrategia de testing de `arquitectura-base.md`, no de una intuicion. **Esta marca no automatiza nada**: dimensiona cuanto trabajo manual arrastra cada regresion, que es una cifra que alguien necesita al planificar.

### 5. Generacion de los dos ficheros

Compon **un solo manifiesto JSON** y pasalo a los dos scripts. Escribelo en un fichero temporal **fuera de `docs/`** (por ejemplo `.aiba-test-plan-HU-06.json` en la raiz, y borralo al terminar): no es un entregable y no debe acabar versionado. El esquema completo:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aiba-test-plan/scripts/gen_test_plan_xlsx.py" --schema
```

Despues, en este orden:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aiba-test-plan/scripts/gen_test_plan_xlsx.py" \
  --manifest <manifiesto.json> \
  --output "docs/pruebas/PP - HU-06 - Tomador.xlsx"
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aiba-test-plan/scripts/gen_evidence_docx.py" \
  --manifest <manifiesto.json> \
  --output "docs/pruebas/Evidencias - HU-06 - Tomador.docx"
```

**Los codigos los pone el script**, no tu. Reinicia el correlativo dentro de cada caso de uso y avisa cuando dos casos comparten caso de uso y nombre — casi siempre un duplicado que hay que arreglar **en el origen**, no renombrando en el Excel. Si el script emite ese aviso, **corrigelo y regenera** en vez de entregarlo.

Si un script falla, dilo y no entregues el otro a medias: los dos describen el mismo plan y uno solo induce a error.

### 6. Reedicion

Si los ficheros ya existen, **pregunta antes a los propios scripts**. La regla es no pisar trabajo ejecutado, y ese dato esta dentro de los ficheros:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aiba-test-plan/scripts/gen_test_plan_xlsx.py" \
  --comprobar "docs/pruebas/PP - HU-06 - Tomador.xlsx"
python3 "${CLAUDE_PLUGIN_ROOT}/skills/aiba-test-plan/scripts/gen_evidence_docx.py" \
  --comprobar "docs/pruebas/Evidencias - HU-06 - Tomador.docx"
```

Devuelven `regenerable` y el motivo, y **salen con codigo 1 cuando no se puede regenerar**: hay resultados anotados, hay capturas pegadas, o el fichero no lo genero este skill. En cualquiera de los tres casos **detente y preguntale al usuario**: regenerar borraria trabajo que no se recupera.

- **Corre las dos comprobaciones, no una.** El `.xlsx` guarda el resultado y el `.docx` guarda la prueba de haberlo obtenido; se pierden por separado.
- Si no hay nada ejecutado, muestra que ha cambiado en la documentacion de origen, regenera, y **anade una fila** al `Registro de Modificaciones` de la `Hoja de Control` (`1.0` -> `1.1`) sin tocar el historial.
- **Los codigos de los casos que siguen existiendo no deben cambiar.** Si un caso desaparece del medio, no renumeres los siguientes: alguien puede tener ya ese codigo en una incidencia o en el board.

### 7. Resumen final

Informa siempre de:

- **Rutas de los dos ficheros** por cada HU. Sin esto el usuario no sabe donde ha quedado el entregable.
- **Cuantos casos y como se reparten** por caso de uso, criticidad y manual/automatizable. El reparto manual es la cifra que alguien va a usar para estimar.
- **Decision de marca** y su origen, y si el logo del Excel se omitio por falta de Pillow.
- **Casos que no se han podido derivar** porque el criterio de aceptacion era ambiguo o el DF tenia un punto abierto. Es el trabajo que el plan deja pendiente, y es mas importante que el recuento.
- **Que este plan no ejecuta nada** y quien lo ejecuta, si es la primera vez que se genera en el proyecto.

## Diseno de los entregables

Los dos salen **genericos pero estructurados**, con el mismo criterio que el DF:

- **Estilos nativos**, no formato directo. Cambiar la paleta es cambiar el estilo.
- **Excel**: cabeceras con estilo, desplegables de validacion en Criticidad, Estado, Keywords y Resultado, panel congelado, autofiltro, y el codigo de cada fila de ejecucion **enlazado a su fila del inventario**.
- **`Resumen` con formulas vivas**, no con recuentos congelados: quien ejecuta anota en la rejilla y los KPIs se actualizan solos.
- **`Parámetros` visible**, no oculta. La nomenclatura con la que se han formado los codigos es informacion de quien lee el plan.
- **Word**: indice como campo `TOC`, cabecera y pie como campos, un bloque por caso con su ficha y el hueco de la captura bajo "Resultado actual".
- **Sin macros.** La plantilla de referencia es un `.xlsm` cuyos botones generan los codigos y montan la hoja de ejecucion; aqui eso sale hecho al construir el fichero, y ademas evita el aviso de seguridad al abrirlo.

## Verificacion final

Antes de dar el comando por terminado:

- Los dos ficheros existen y abren.
- Todo caso tiene codigo, nombre, criticidad, pasos y resultado esperado. Ninguno dice "funciona correctamente".
- El script no ha emitido avisos de codigo duplicado sin resolver.
- Ningun caso de uso usado en `casos` falta en `casos_uso`.
- Si el plan es una reedicion, has corrido `--comprobar` sobre **los dos** ficheros antes de regenerar.
- El fichero temporal del manifiesto no ha quedado en `docs/` ni sin borrar.

## Siguiente paso sugerido

- Si la HU aun no tiene DF: `aiba functional-design HU-XX`, que ademas mejora el proximo plan.
- Si el proyecto usa AISDD: el inventario es la checklist del Outcome Validator en `aisdd close change`.
- Si hay casos marcados como automatizables y ya existe codigo: `aiad test` sobre ellos.
