# Evolución de Native AI

Presentación ejecutiva que compara tres niveles de madurez:

1. la metodología AI-Native original;
2. el procedimiento ejecutable de `native-ai-specs` v1.6.0;
3. el sistema actual de seis plugins del marketplace.

La presentación separa un cuerpo ejecutivo, pensado para exposición, de un anexo con el detalle metodológico y técnico.

## Artefactos

- `evolucion-native-ai-v2.pptx`: presentación panorámica con textos y gráficos editables.
- `evolucion-native-ai-v2.pdf`: copia para revisión, una diapositiva por página.
- `generate.py`: fuente reproducible de ambos artefactos.
- `requirements.txt`: dependencias fijadas del generador.

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
