#!/bin/sh
# Injecte la ligne de locale au démarrage de session (contexte seulement, aucun appel réseau, aucune écriture).
# Effet mesuré sur l'appel du skill : voir banc/BILAN.md.
cat > /dev/null
python3 -I -c 'import json,sys; print(json.dumps({"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":open(sys.argv[1],encoding="utf-8").read().strip()}},ensure_ascii=False))' "${CLAUDE_PLUGIN_ROOT}/hooks/ligne.txt"
