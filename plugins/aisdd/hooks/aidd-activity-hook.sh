#!/usr/bin/env bash
# aidd-activity-hook — traza de actividad AIDD/AISDD sobre el codigo.
#
# Anota en docs/aidd-activity.md, una linea por evento:
#   run   — se invoca un skill (con sus argumentos)
#   file  — la IA escribe un fichero, atribuido al skill activo
#   turn  — fin de turno, con su duracion y cuantas acciones ha tenido
#
# Las lineas `turn` son las que permiten medir tiempo *atendido* (el humano lanza
# una peticion y espera) en vez de tiempo de calendario, que incluiria comidas,
# reuniones y noches. Sin ellas, cualquier KPI de ahorro seria ruido.
#
# Formato (campos fijos, separados por " | ", pensados para parsear):
#   - <ts> | user:<usuario> | skill:<skill> | ctx:<HU o change> | <accion> | note:<nota>
#
# Propiedades:
#   - OPT-IN      : no hace nada salvo que docs/aidd-activity.md ya exista. Se
#                   activa con `touch docs/aidd-activity.md` y se desactiva
#                   borrando el fichero. Ningun proyecto se registra sin quererlo.
#   - PASIVO      : solo registra. Nunca bloquea, nunca edita codigo, nunca pregunta.
#                   No escribe nada por stdout (en UserPromptSubmit stdout se
#                   inyectaria como contexto de la conversacion).
#   - PRIVADO     : nunca registra el texto de los prompts ni el contenido del
#                   codigo. Solo skill, fichero, argumentos del comando y tiempos.
#   - SEGURO      : nunca hace fallar la sesion. Siempre sale con 0.
#   - IDEMPOTENTE : deduplica por tool_use_id (o prompt_id en eventos de turno).
#                   Los cuatro plugins traen este hook, asi que con varios
#                   instalados se dispara varias veces por el mismo evento; solo
#                   la primera copia escribe.
#
# El matcher del hook es "*" (todas las tools) y el filtrado se hace aqui: asi
# funciona sea cual sea el nombre interno de la tool que invoca skills.
#
# SYNC: fichero compartido, identico en plugins/{aidd,aisdd,aiad,aiba,boosters}/hooks/.
#       Si lo cambias, copialo a los cuatro (todos deben tener el mismo sha256).

set -u

LOG_REL="docs/aidd-activity.md"

# Salida rapida: esto corre en cada llamada a una tool. Sin registro en el
# proyecto nos vamos antes de leer stdin y de lanzar un parser.
[ -f "$LOG_REL" ] || exit 0

input="$(cat 2>/dev/null)" || exit 0
[ -n "${input:-}" ] || exit 0

event=""; tool=""; uid=""; sid=""; pid=""; cwd=""; file=""; wrote=""; skill=""; sargs=""

if command -v jq >/dev/null 2>&1; then
  eval "$(printf '%s' "$input" | jq -r '
    def q: (. // "") | tostring | @sh;
    "event=" + (.hook_event_name | q),
    "tool="  + (.tool_name | q),
    "uid="   + (.tool_use_id | q),
    "sid="   + (.session_id | q),
    "pid="   + (.prompt_id | q),
    "cwd="   + (.cwd | q),
    "file="  + ((.tool_input.file_path // .tool_input.notebook_path
                 // (.tool_input.edits[0].file_path)
                 // .tool_input.path // .tool_input.filePath // .tool_input.file) | q),
    "wrote=" + ((if (.tool_input | type) == "object" then
                   ([.tool_input.content, .tool_input.new_string, .tool_input.new_str,
                     .tool_input.contents, .tool_input.patch, .tool_input.diff,
                     .tool_input.edits] | map(select(. != null)) | length)
                 else 0 end) | if . > 0 then "1" else "" end | q),
    "skill=" + (.tool_input.skill | q),
    "sargs=" + (.tool_input.args | q)
  ' 2>/dev/null)"
elif command -v python3 >/dev/null 2>&1; then
  eval "$(printf '%s' "$input" | python3 -c '
import sys, json, shlex
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
ti = d.get("tool_input") or {}
if not isinstance(ti, dict):
    ti = {}
f = (ti.get("file_path") or ti.get("notebook_path")
     or ti.get("path") or ti.get("filePath") or ti.get("file"))
if not f:
    edits = ti.get("edits") or []
    if isinstance(edits, list) and edits and isinstance(edits[0], dict):
        f = edits[0].get("file_path")
# Senal de escritura: la ruta sola no distingue leer de escribir.
wrote = "1" if any(ti.get(k) is not None for k in
                   ("content", "new_string", "new_str", "contents",
                    "patch", "diff", "edits")) else ""
def p(k, v):
    print(k + "=" + shlex.quote("" if v is None else str(v)))
p("event", d.get("hook_event_name"))
p("tool", d.get("tool_name"))
p("uid", d.get("tool_use_id"))
p("sid", d.get("session_id"))
p("pid", d.get("prompt_id"))
p("cwd", d.get("cwd"))
p("file", f)
p("wrote", wrote)
p("skill", ti.get("skill"))
p("sargs", ti.get("args"))
' 2>/dev/null)"
else
  # Sin parser de JSON no adivinamos nada.
  exit 0
fi

# Nombres normalizados: cada plataforma escribe el suyo. Claude Code manda
# `PostToolUse`; Codex normaliza a `post_tool_use`. Comparar literales dejaba
# fuera media plataforma **en silencio** -- el hook se disparaba, no reconocia
# el evento y salia con 0, asi que el registro quedaba vacio y `aiba metrics`
# publicaba ceros sin ninguna senal de que faltara nada.
# Sin subprocesos: esto corre en cada llamada a una tool.
norm() { local s="${1:-}"; s="${s//[-_ ]/}"; printf '%s' "${s,,}"; }
event_n="$(norm "${event:-}")"
tool_n="$(norm "${tool:-}")"

# Que hacemos con este evento.
kind=""
case "$event_n" in
  userpromptsubmit) kind="turn-start" ;;
  stop|sessionend)  kind="turn-end" ;;
  *)
    case "$tool_n" in
      skill)
        kind="skill" ;;
      # Escrituras conocidas. Claude Code: Write/Edit/MultiEdit/NotebookEdit.
      # Otros agentes usan sus propios nombres; se anaden los habituales.
      write|edit|multiedit|notebookedit|applypatch|patch|editfile|writefile|createfile|strreplaceeditor)
        kind="file" ;;
      # Lecturas y busquedas: nunca son actividad sobre el codigo. Van
      # explicitas para que el fallback de abajo no las cuele.
      read|grep|glob|search|list|ls|find|view|bash|shell|exec|task|todowrite)
        exit 0 ;;
      *)
        # Herramienta desconocida: solo cuenta si el payload trae **una ruta de
        # fichero y una senal de escritura**. Con la ruta sola no basta -- una
        # lectura tambien la trae--, y contarla inflaria el registro.
        if [ -n "${file:-}" ] && [ -n "${wrote:-}" ]; then
          kind="file"
        else
          exit 0
        fi
        ;;
    esac
    ;;
esac

# El hook puede ejecutarse desde otro directorio: nos situamos en el proyecto.
if [ -n "${cwd:-}" ] && [ -d "${cwd:-}" ]; then
  cd "$cwd" 2>/dev/null || true
fi

# Opt-in, ya en el directorio del proyecto: sin fichero de registro no se escribe.
[ -f "$LOG_REL" ] || exit 0

safe() { printf '%s' "${1:-}" | tr -c 'A-Za-z0-9._-' '_' | cut -c1-64; }

# Estado por sesion: skill activo, contexto (HU/change), inicio de turno y
# contadores. Compartido por las cuatro copias del hook (va por session_id).
dir=""
base="${TMPDIR:-/tmp}/aidd-activity"
sid_safe="$(safe "${sid:-nosession}")"
if mkdir -p "$base/$sid_safe" 2>/dev/null; then
  dir="$base/$sid_safe"
fi

# Deduplicacion atomica entre las copias del hook: la primera crea el directorio
# marca, las demas fallan en el mkdir y se van sin escribir. Los eventos de turno
# no traen tool_use_id, asi que se deduplican por prompt_id.
mark=""
case "$kind" in
  turn-start) mark="turnstart-$(safe "${pid:-}")" ;;
  turn-end)   mark="turnend-$(safe "${pid:-}")" ;;
  *)          mark="uid-$(safe "${uid:-}")" ;;
esac
if [ -n "$dir" ] && [ -n "$mark" ] && [ "$mark" != "uid-" ] \
   && [ "$mark" != "turnstart-" ] && [ "$mark" != "turnend-" ]; then
  mkdir "$dir/$mark" 2>/dev/null || exit 0
fi

now="$(date -u +%s 2>/dev/null || printf '%s' 0)"

# --- Inicio de turno: solo marca tiempo, no escribe en el registro -----------
# (Aqui llega el texto del prompt; no lo tocamos ni lo guardamos.)
if [ "$kind" = "turn-start" ]; then
  if [ -n "$dir" ]; then
    printf '%s' "$now" > "$dir/turn-start" 2>/dev/null
    : > "$dir/turn-tools" 2>/dev/null
    : > "$dir/turn-skills" 2>/dev/null
  fi
  exit 0
fi

oneline() {
  printf '%s' "${1:-}" | tr '\n\r\t|' '    ' | cut -c1-120
}

user="${USER:-}"
[ -n "$user" ] || user="$(id -un 2>/dev/null || printf '%s' '-')"

ts="$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date 2>/dev/null)"

# Contexto de trabajo (HU o change de OpenSpec) heredado del ultimo detectado.
ctx="-"
if [ -n "$dir" ] && [ -f "$dir/current-ctx" ]; then
  ctx="$(cat "$dir/current-ctx" 2>/dev/null)"
  [ -n "$ctx" ] || ctx="-"
fi
remember_ctx() {
  ctx="$1"
  [ -n "$dir" ] && printf '%s' "$ctx" > "$dir/current-ctx" 2>/dev/null
}

skill_field="-"
action=""
note="-"

case "$kind" in
  skill)
    [ -n "${skill:-}" ] || exit 0
    [ -n "$dir" ] && printf '%s' "$skill" > "$dir/current-skill" 2>/dev/null
    [ -n "$dir" ] && printf 'x' >> "$dir/turn-skills" 2>/dev/null
    skill_field="$skill"
    action="run"
    note="$(oneline "${sargs:-}")"
    [ -n "$note" ] || note="-"
    # Una HU o US citada en los argumentos fija el contexto de lo que viene.
    if [[ "${sargs:-}" =~ (HU|US)-[0-9]+ ]]; then
      remember_ctx "${BASH_REMATCH[0]}"
    fi
    ;;
  file)
    [ -n "${file:-}" ] || exit 0
    case "$file" in
      "$PWD"/*) rel="${file#"$PWD"/}" ;;
      *)        rel="$file" ;;
    esac
    # Nunca registrar la escritura del propio registro (evita el bucle).
    [ "$rel" = "$LOG_REL" ] && exit 0
    [ -n "$dir" ] && printf 'x' >> "$dir/turn-tools" 2>/dev/null
    if [ -n "$dir" ] && [ -f "$dir/current-skill" ]; then
      skill_field="$(cat "$dir/current-skill" 2>/dev/null)"
      [ -n "$skill_field" ] || skill_field="-"
    fi
    # Trabajar dentro de un change de OpenSpec fija el contexto.
    if [[ "$rel" =~ ^openspec/changes/([^/]+)/ ]]; then
      remember_ctx "${BASH_REMATCH[1]}"
    fi
    action="file:$(oneline "$rel")"
    ;;
  turn-end)
    start=""
    [ -n "$dir" ] && [ -f "$dir/turn-start" ] && start="$(cat "$dir/turn-start" 2>/dev/null)"
    # Sin marca de inicio no sabemos cuanto ha durado: no inventamos una duracion.
    dur="-"
    if [ -n "$start" ] && [ "$start" -gt 0 ] 2>/dev/null && [ "$now" -ge "$start" ] 2>/dev/null; then
      dur="$((now - start))s"
    fi
    tools=0; skills=0
    if [ -n "$dir" ]; then
      [ -f "$dir/turn-tools" ] && tools="$(wc -c < "$dir/turn-tools" 2>/dev/null || printf '0')"
      [ -f "$dir/turn-skills" ] && skills="$(wc -c < "$dir/turn-skills" 2>/dev/null || printf '0')"
    fi
    # Turno sin actividad sobre el codigo: no aporta nada al registro.
    [ "${tools:-0}" -eq 0 ] && [ "${skills:-0}" -eq 0 ] && exit 0
    action="turn"
    note="dur=$dur skills=$(printf '%s' "${skills:-0}" | tr -d ' ') files=$(printf '%s' "${tools:-0}" | tr -d ' ')"
    [ -n "$dir" ] && rm -f "$dir/turn-start" 2>/dev/null
    ;;
esac

# Cabecera la primera vez (el fichero se crea vacio con `touch`).
if [ ! -s "$LOG_REL" ]; then
  {
    printf '# Registro de actividad AIDD\n\n'
    printf 'Traza automatica de las acciones sobre el codigo: que skill se ejecuta, que\n'
    printf 'ficheros toca la IA y cuanto dura cada turno. La escribe el hook\n'
    printf '`aidd-activity-hook.sh` que traen los plugins del marketplace aidd-sdd, y la\n'
    printf 'consume `aiba metrics` para calcular los KPIs. Es opt-in: existe este fichero,\n'
    printf 'se registra; borralo y el registro se apaga en este proyecto.\n\n'
    printf 'No se guarda el texto de los prompts ni el contenido del codigo.\n\n'
    printf 'Formato (marcas de tiempo en UTC):\n\n'
    printf '`- <fecha-hora> | user:<usuario> | skill:<skill> | ctx:<HU o change> | <accion> | note:<nota>`\n\n'
    printf 'Acciones: `run` (skill invocado), `file:<ruta>` (fichero escrito por la IA),\n'
    printf '`turn` (fin de turno, con duracion y numero de acciones).\n\n'
  } >> "$LOG_REL" 2>/dev/null
fi

printf -- '- %s | user:%s | skill:%s | ctx:%s | %s | note:%s\n' \
  "$ts" "$(oneline "$user")" "$(oneline "$skill_field")" "$(oneline "$ctx")" "$action" "$note" \
  >> "$LOG_REL" 2>/dev/null

exit 0
