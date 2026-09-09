# Evolución de Native AI — resumen ejecutivo

Cinco diapositivas para presentar, en una reunión corta, qué le hemos aportado a la metodología Native AI: qué recibimos, qué hemos construido encima y qué gana el negocio con ello.

**Esto es el resumen, no el informe.** El detalle completo —los dos procedimientos comparados, el inventario de skills, las diez mejoras, lo que no se tocó y los costes— está en `native-ia-source/evolucion-native-ai.html`, con su PDF al lado. El deck no lo repite a propósito: si lo repitiera, habría dos documentos que mantener en paso y uno de los dos acabaría mintiendo.

## Artefactos

- [PowerPoint](evolucion-native-ai-v2.pptx): cinco diapositivas, con textos y gráficos editables.
- [PDF](evolucion-native-ai-v2.pdf): una diapositiva por página.
- [Vista previa](preview.png): las cinco de un vistazo.
- [Generador](generate.py): fuente reproducible de los tres artefactos.
- [Dependencias](requirements.txt): versiones fijadas del generador.

El lienzo se dibuja con Liberation Sans, clon métrico de la Arial que pide el PPTX, para que la previsualización y el PDF reflejen lo que verá PowerPoint.

## Las cinco diapositivas

1. **Recibimos un método. Devolvimos una cadena de entrega.** La tesis, con las tres cifras que la sostienen.
2. **El método cubría tres de los ocho tramos. Hoy cubre los ocho.** La prueba, en una sola imagen.
3. **Del cliente que firma al KPI que se defiende.** Qué se ha construido, en cuatro eslabones sobre una única fuente de verdad.
4. **Cuatro cosas que antes no podíamos hacer delante de un cliente.** Qué cambia en la práctica.
5. **Está en uso, se instala en un comando y sigue creciendo.** Dónde estamos, qué falta y qué proponemos.

## Fuentes

Las cifras se recalculan en cada generación sobre:

- `.claude-plugin/marketplace.json`;
- `plugins/*/.claude-plugin/plugin.json`;
- `plugins/*/skills/*/SKILL.md`;
- `.github/scripts/check_*.py`.

`metrics()` aborta la generación si alguna cifra se desvía de la esperada, para que el relato no se quede desfasado respecto al repositorio sin que nadie se entere. El material de referencia (`native-ia-source/`) es local y está ignorado por Git.

## Regeneración

```bash
python3 -m venv .venv
.venv/bin/pip install -r docs/presentaciones/evolucion-native-ai/requirements.txt
.venv/bin/python docs/presentaciones/evolucion-native-ai/generate.py
```

El generador deja el PPTX, el PDF y las imágenes de control visual en esta misma carpeta.
