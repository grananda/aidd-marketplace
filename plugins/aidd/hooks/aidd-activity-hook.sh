#!/usr/bin/env bash
# aidd-activity-hook — traza de actividad AIDD/AISDD sobre el codigo.
#
# Anota en docs/aidd-activity.md, una linea por accion:
#   - que skill se ejecuta (con sus argumentos), y
#   - que fichero toca la IA, atribuido al skill que estaba activo en ese momento.
#
# Hereda las convenciones de aiad-journal-hook.sh:
#   - OPT-IN      : no hace nada salvo que docs/aidd-activity.md ya exista. Se
#                   activa con `touch docs/aidd-activity.md` y se desactiva
#                   borrando el fichero. Ningun proyecto se registra sin quererlo.
#   - PASIVO      : solo registra. Nunca bloquea, nunca edita codigo, nunca pregunta.
#   - SEGURO      : nunca hace fallar la sesion. Siempre sale con 0.
#   - IDEMPOTENTE : deduplica por tool_use_id. Los cuatro plugins del marketplace
#                   traen este hook, asi que con varios instalados se dispara
#                   varias veces por la misma accion; solo la primera escribe.
#
# El matcher del hook es "*" (todas las tools) y el filtrado se hace aqui: asi
# funciona sea cual sea el nombre interno de la tool que invoca skills.
#
# SYNC: fichero compartido, identico en plugins/{aidd,aisdd,aiad,boosters}/hooks/.
#       Si lo cambias, copialo a los cuatro (todos deben tener el mismo sha256).

set -u

LOG_REL="docs/aidd-activity.md"

# Salida rapida: el matcher es "*", asi que esto corre en cada llamada a una tool.
# Sin registro en el proyecto nos vamos antes de leer stdin y de lanzar un parser.
[ -f "$LOG_REL" ] || exit 0

input="$(cat 2>/dev/null)" || exit 0
[ -n "${input:-}" ] || exit 0

tool=""; uid=""; sid=""; cwd=""; file=""; skill=""; sargs=""

if command -v jq >/dev/null 2>&1; then
  eval "$(printf '%s' "$input" | jq -r '
    def q: (. // "") | tostring | @sh;
    "tool="  + (.tool_name | q),
    "uid="   + (.tool_use_id | q),
    "sid="   + (.session_id | q),
    "cwd="   + (.cwd | q),
    "file="  + ((.tool_input.file_path // .tool_input.notebook_path // (.tool_input.edits[0].file_path)) | q),
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
f = ti.get("file_path") or ti.get("notebook_path")
if not f:
    edits = ti.get("edits") or []
    if isinstance(edits, list) and edits:
        f = (edits[0] or {}).get("file_path")
def p(k, v):
    print(k + "=" + shlex.quote("" if v is None else str(v)))
p("tool", d.get("tool_name"))
p("uid", d.get("tool_use_id"))
p("sid", d.get("session_id"))
p("cwd", d.get("cwd"))
p("file", f)
p("skill", ti.get("skill"))
p("sargs", ti.get("args"))
' 2>/dev/null)"
else
  # Sin parser de JSON no adivinamos nada.
  exit 0
fi

# Solo interesan la invocacion de skills y las escrituras de fichero.
case "${tool:-}" in
  Skill)                             kind="skill" ;;
  Write|Edit|MultiEdit|NotebookEdit) kind="file" ;;
  *)                                 exit 0 ;;
esac

# El hook puede ejecutarse desde otro directorio: nos situamos en el proyecto.
if [ -n "${cwd:-}" ] && [ -d "${cwd:-}" ]; then
  cd "$cwd" 2>/dev/null || true
fi

# Opt-in, ya en el directorio del proyecto: sin fichero de registro no se escribe.
[ -f "$LOG_REL" ] || exit 0

# Estado por sesion: skill activo + marcas de deduplicacion. Compartido por las
# cuatro copias del hook (va por session_id, no por plugin).
safe() { printf '%s' "${1:-}" | tr -c 'A-Za-z0-9._-' '_' | cut -c1-64; }

dir=""
base="${TMPDIR:-/tmp}/aidd-activity"
if mkdir -p "$base/$(safe "${sid:-nosession}")" 2>/dev/null; then
  dir="$base/$(safe "${sid:-nosession}")"
fi

# Deduplicacion atomica: la primera copia del hook que llega crea el directorio;
# las demas fallan en el mkdir y se van sin escribir.
if [ -n "$dir" ] && [ -n "${uid:-}" ]; then
  mkdir "$dir/uid-$(safe "$uid")" 2>/dev/null || exit 0
fi

# Una linea, sin barras verticales que rompan el formato ni saltos de linea.
oneline() {
  printf '%s' "${1:-}" | tr '\n\r\t|' '    ' | cut -c1-120
}

user="${USER:-}"
[ -n "$user" ] || user="$(id -un 2>/dev/null || printf '%s' '-')"

ts="$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date 2>/dev/null)"

if [ "$kind" = "skill" ]; then
  [ -n "${skill:-}" ] || exit 0
  # Recordamos el skill activo para atribuirle los ficheros que se toquen despues.
  [ -n "$dir" ] && printf '%s' "$skill" > "$dir/current-skill" 2>/dev/null
  action="run"
  note="$(oneline "${sargs:-}")"
  [ -n "$note" ] || note="-"
else
  [ -n "${file:-}" ] || exit 0
  case "$file" in
    "$PWD"/*) rel="${file#"$PWD"/}" ;;
    *)        rel="$file" ;;
  esac
  # Nunca registrar la escritura del propio registro (evita el bucle).
  [ "$rel" = "$LOG_REL" ] && exit 0
  active="-"
  if [ -n "$dir" ] && [ -f "$dir/current-skill" ]; then
    active="$(cat "$dir/current-skill" 2>/dev/null)"
    [ -n "$active" ] || active="-"
  fi
  skill="$active"
  action="file:$(oneline "$rel")"
  note="-"
fi

# Cabecera la primera vez (el fichero se crea vacio con `touch`).
if [ ! -s "$LOG_REL" ]; then
  {
    printf '# Registro de actividad AIDD\n\n'
    printf 'Traza automatica de las acciones sobre el codigo: que skill se ejecuta y que\n'
    printf 'ficheros toca la IA. La escribe el hook `aidd-activity-hook.sh` que traen los\n'
    printf 'plugins del marketplace aidd-sdd. Es opt-in: existe este fichero, se registra;\n'
    printf 'borralo y el registro se apaga en este proyecto.\n\n'
    printf 'Formato (marcas de tiempo en UTC):\n\n'
    printf '`- <fecha-hora> | user:<usuario> | skill:<skill> | run | note:<argumentos>`\n'
    printf '`- <fecha-hora> | user:<usuario> | skill:<skill activo> | file:<fichero> | note:-`\n\n'
  } >> "$LOG_REL" 2>/dev/null
fi

printf -- '- %s | user:%s | skill:%s | %s | note:%s\n' \
  "$ts" "$(oneline "$user")" "$(oneline "$skill")" "$action" "$note" >> "$LOG_REL" 2>/dev/null

exit 0
