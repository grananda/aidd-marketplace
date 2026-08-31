# aiba-test-plan

Genera el **Plan de Pruebas** de cada historia de usuario a partir de la documentación que producen AIDD y AIBA.

```text
aiba test-plan          # todas las HU
aiba test-plan HU-06    # solo esa
```

Alias: `aiba plan-pruebas`, `aiba pruebas`.

## Qué produce

Dos ficheros por HU en `docs/pruebas/`, generados del **mismo manifiesto** para que no puedan describir cosas distintas.

**`PP - HU-06 - <título>.xlsx`** — el inventario:

| Hoja | Qué lleva |
|---|---|
| `Hoja de Control` | Proyecto, historia, entorno, versión y registro de modificaciones |
| `Especificaciones` | El inventario, con las diecisiete columnas de la plantilla de referencia |
| `Parámetros` | La nomenclatura con la que se han formado los códigos |
| `Ejecución 1` | Rejilla de ejecución: entorno, plataforma, navegador, fecha, resultado |
| `Qmetry` | Proyección del inventario al formato de importación de la herramienta |
| `Resumen` | KPIs con fórmulas vivas y reparto manual / automatizable |

**`Evidencias - HU-06 - <título>.docx`** — portada con índice, datos generales, catálogo de casos de uso, y un bloque por caso con su ficha, sus pasos y el hueco para pegar la captura bajo «Resultado actual».

## De dónde saca el contenido

La fuente de verdad es **`docs/detalle-historias-usuario.md`**: cada criterio de aceptación Dado/Cuando/Entonces se convierte en uno o varios casos. Sin él el comando se detiene y remite a `aidd user-story-details`.

**Si existe el DF de la HU en `docs/df/`, es mejor fuente que los criterios.** Sus tablas de validaciones, mensajes y campos ya son casos de prueba casi literales, y sus puntos abiertos dicen qué *no* se puede probar todavía. Como un `.docx` no se lee de un vistazo, `gen_df_docx.py --extraer` lo vuelca a JSON.

Completa con `requisitos.md` (traza RF/NFR), `mapa-historias-usuario.md` (agrupación), `arquitectura-base.md` (de su estrategia de testing sale la marca de automatizable) y `roadmap.md` (el `change_hint` de cada caso).

## Lo que no hace

**No ejecuta las pruebas.** Este comando corre en tiempo de diseño, cuando el código puede no existir. Quien ejecuta es el **Outcome Validator** al cerrar un change, el humano con `aiad test` sobre los casos automatizables, o un tester de QA con estos dos ficheros.

Recoger los resultados de vuelta no lo hace nadie hoy. Lo que sí queda preparado para el día que se haga son dos datos por caso: su **código**, estable y único, y **el change al que pertenece**.

**No inventa casos.** Cada uno sale de un criterio de aceptación, de una validación del DF o de un requisito. Un plan inflado con casos plausibles le cuesta tiempo real de ejecución a alguien.

**Solo genera `Pruebas de Sistema-Funcionales`.** Es lo que se deriva de una historia. Las unitarias las escribe quien conoce el código, no quien lee la historia.

## Nomenclatura

`PS.FU.CU01.01` — nivel, subnivel, caso de uso y correlativo, que **reinicia dentro de cada caso de uso**. Los tramos vacíos se colapsan, y dos casos que caen en el mismo código se avisan al generar, que es cuando todavía se puede arreglar en el origen.

## Sin macros

La plantilla de referencia es un `.xlsm` con dos botones: uno genera los códigos concatenando columnas, otro monta la hoja de ejecución pidiendo plan, plataforma y build. Los dos existen porque un humano teclea el inventario a mano.

Aquí eso sale hecho al construir el fichero, así que el entregable es un `.xlsx` limpio — que además no dispara el aviso de seguridad al abrirlo. Lo que sí se conserva son las reglas de esas macros: el correlativo por prefijo, el colapso de tramos vacíos y el aviso de duplicado.

## Diseño: genérico, pero estructurado

Los dos ficheros salen **sin logotipos ni colores corporativos**, y el comando **pregunta antes** si quieres aplicar una marca —desde una carpeta local o desde una URL— con la opción de no aplicar ninguna como recomendada.

La razón es la misma que en el DF: un plan de pruebas acaba en manos de un cliente que tiene su propia identidad. Generarlo neutro pero bien estructurado permite aplicarla después en minutos, porque los colores viven en los estilos.

En Excel eso significa cabeceras con estilo, desplegables de validación, panel congelado, autofiltro y el código de cada fila de ejecución enlazado a su fila del inventario. En Word, índice como campo `TOC` y cabecera y pie como campos.

## Reedición

**Nunca se pisan resultados ejecutados.** Antes de regenerar, los dos scripts responden con `--comprobar`:

```bash
gen_test_plan_xlsx.py --comprobar "docs/pruebas/PP - HU-06 - Tomador.xlsx"
gen_evidence_docx.py  --comprobar "docs/pruebas/Evidencias - HU-06 - Tomador.docx"
```

Salen con código 1 si hay resultados anotados, capturas pegadas, o el fichero no lo generó este skill. El `.xlsx` guarda el resultado y el `.docx` guarda la prueba de haberlo obtenido: se pierden por separado, así que se comprueban los dos.

Si no hay nada ejecutado, se regenera y se **añade una fila** al registro de modificaciones sin tocar el historial. Los códigos de los casos que siguen existiendo no cambian, aunque desaparezca uno del medio: alguien puede tener ya ese código en una incidencia.

## Requisitos

Python 3 y `openpyxl` y `python-docx`, que los scripts instalan solos si faltan. Si no pueden, lo dicen y no bloquean.

El **logo en el Excel** necesita además `Pillow`, que `openpyxl` no arrastra. Si falta, el fichero sale sin logo y con un aviso; los colores sí se aplican.

## Relación con el resto

Consume lo que producen `aidd user-story-details`, `aidd requirements`, `aidd architecture`, `aisdd roadmap` y `aiba functional-design`. No modifica ninguno de sus documentos: lee `docs/` y escribe solo en `docs/pruebas/`.

La marca corporativa la comparte con `aiba-functional-design` a través de `${CLAUDE_PLUGIN_ROOT}/scripts/branding.py`, que vive a nivel de plugin junto a `stamp_doc.py` y por la misma razón: la usan skills distintos, y una copia por skill se queda atrás sin que nada falle.
