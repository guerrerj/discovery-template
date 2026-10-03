#!/bin/sh
# Installs a git pre-commit hook that runs check.py. Run once after `git init`.
set -e
cd "$(dirname "$0")/.."
[ -d .git ] || { echo "run 'git init' first"; exit 1; }
cat > .git/hooks/pre-commit << 'H'
#!/bin/sh
# Use the first Python 3.7+ that actually runs: python3, then python, then py -3 (Windows launcher).
# Each is test-run, because Windows can have a python3 alias with no Python behind it.
for PY in "python3" "python" "py -3"; do
  if $PY -c "import sys; sys.exit(sys.version_info < (3, 7))" >/dev/null 2>&1; then
    $PY scripts/check.py || { echo "pre-commit: check.py failed; commit blocked"; exit 1; }
    exit 0
  fi
done
echo "pre-commit: no working Python 3.7+ found (tried python3, python, py -3). Install Python 3.7+ and commit again; commit blocked."
exit 1
H
chmod +x .git/hooks/pre-commit
mkdir -p .claude/skills && cp -r .skills/* .claude/skills/
echo "hook installed; skills copied to .claude/skills/"
