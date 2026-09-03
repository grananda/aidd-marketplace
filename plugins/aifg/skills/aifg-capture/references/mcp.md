# Hablar con Figma

> Referencia del skill `aifg-capture`. El indice y las reglas comunes estan en `SKILL.md`.

## Solo MCP

Este plugin habla con Figma **unicamente a traves de un MCP**. El recomendado es `figma-developer-mcp` (Framelink), que se ejecuta por npx, lee los archivos desde la web a partir de un enlace y se autentica con un token personal de Figma.

```
claude mcp add figma-developer-mcp -- npx -y figma-developer-mcp --figma-api-key=figd_XXXX --stdio
```

**No hay camino alternativo.** Nada de llamadas REST a `api.figma.com`, nada de pedir un token para usarlo directamente, nada de gestionar credenciales desde el skill. Es la misma regla que rige la integracion con Jira en `aisdd-specs`, y por los mismos motivos: un token en un flag acaba en el historial del shell, en los logs de CI y a veces en los ficheros de salida de una auditoria.

- **Ofrece el comando `claude mcp add` para que lo ejecute el usuario.** No lo ejecutes tu con un token que te acaben de dar por chat.
- **Scope de usuario**, nunca un `.mcp.json` de proyecto commiteado.
- **No escribas el token en ningun documento generado**, ni en el registro, ni en la auditoria, ni en el resumen del comando.

## Descubrimiento

**Localiza las tools por funcion, no por nombre.** Los nombres varian entre versiones y entre servidores equivalentes; asumirlos rompe la integracion en la siguiente actualizacion. Busca con la herramienta de descubrimiento de MCP y usa lo que encuentres.

Necesitas, como minimo, poder: **leer la estructura del archivo** (paginas, frames, componentes), **leer las propiedades de un nodo**, y **exportar una imagen de un nodo**. Si el servidor disponible no expone la exportacion de imagenes, dilo: se puede capturar igual, pero **sin canal de verificacion**, y eso hay que saberlo antes y no despues.

## Si no hay MCP

**Detente y dilo.** Aqui **no se degrada** produciendo un arbol a medias: un `docs/design/` incompleto es peor que ninguno, porque `aisdd implement change` lo va a encontrar y lo va a creer.

La degradacion correcta esta fuera de este plugin y ya existe: sin arbol de diseno, `aisdd implement change` tira de `docs/guia-estilos.md`, y si tampoco la hay, improvisa. **No hace falta que hagas nada para que eso ocurra.**
