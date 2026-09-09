# Evolución de Native AI

Presentación ejecutiva que compara tres niveles de madurez:

1. la metodología AI-Native original;
2. el procedimiento ejecutable de `native-ai-specs` v1.6.0;
3. el sistema actual de seis plugins del marketplace.

La presentación separa un cuerpo ejecutivo, pensado para exposición, de un anexo con el detalle metodológico y técnico.

## Artefactos

- [PowerPoint V2](evolucion-native-ai-v2.pptx): presentación panorámica con textos y gráficos editables.
- [PDF de revisión](evolucion-native-ai-v2.pdf): una diapositiva por página.
- [Vista previa completa](preview.png): contacto visual de las 18 diapositivas.

El lienzo se dibuja con Liberation Sans, clon métrico de la Arial que pide el PPTX, para que la previsualización y el PDF reflejen lo que verá PowerPoint.
- [Generador](generate.py): fuente reproducible de los tres artefactos.
- [Dependencias](requirements.txt): versiones fijadas del generador.

## Estructura narrativa

- **3 diapositivas de resumen ejecutivo**, pensadas para sostenerse solas: quien solo vea esas tres entiende qué ha mejorado y cuánto.
  1. *Lo cualitativo* — ocho áreas con su antes y su ahora.
  2. *Lo cuantitativo* — cinco indicadores contados sobre los ficheros.
  3. *La cobertura* — qué tramo del proyecto cubría cada procedimiento.
- **8 diapositivas de desarrollo:** arquitectura por capas, ecosistema, doble motor de ejecución, cadena de valor, gobierno, adopción y recomendación.
- **7 diapositivas de anexo:** procedimiento comparado, inventario de skills, diez mejoras, continuidad, costes y fuentes.

El informe completo, mejora a mejora, no está en el deck: está en `native-ia-source/evolucion-native-ai.html`. Esta presentación es su resumen.

## Fuentes

La comparación se recalcula sobre:

- `native-ia-source/ai-native.md` y `native-ia-source/native-ai-specs-v1.6.0/`, material de referencia local ignorado por Git;
- `.claude-plugin/marketplace.json`;
- `plugins/*/.claude-plugin/plugin.json`;
- `plugins/*/skills/*/SKILL.md`;
- las metodologías y README vigentes del repositorio.

Las cifras cuantitativas describen los artefactos disponibles en el momento de generar el deck; las valoraciones cualitativas se identifican como tales.

## Regeneración

```bash
python3 -m venv .venv
.venv/bin/pip install -r docs/presentaciones/evolucion-native-ai/requirements.txt
.venv/bin/python docs/presentaciones/evolucion-native-ai/generate.py
```

El generador dejará el PPTX, el PDF y las imágenes de control visual en esta misma carpeta.
