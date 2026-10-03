#!/usr/bin/env python3
"""Sharing boundary: resolve share.txt and scan the files it lists for contact details.

Shared by check.py (blocks commits) and export_share.py (blocks exports) so the two
can't drift apart. Flags email addresses, North American phone numbers, and any
person named in a contacts/ file (full name, plus first names of 4+ letters;
case-insensitive, whole words). Standard library only.
"""
import fnmatch, glob, os, re

ALLOWLIST = "share.txt"
FORBIDDEN_PREFIXES = ("contacts/", "interviews/", "inbox/")
FORBIDDEN_GLOBS = ("reports/outreach-*",)

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# fictional examples: (555) 555-0123, 555-555-0123, 555.555.0123, 555 555 0123, 5555550123, +1 555 555 0123
PHONE = re.compile(r"(?<![\w])(?:\+?1[\s.\-–]?)?\(?\d{3}\)?[\s.\-–]?\d{3}[\s.\-–]?\d{4}(?![\w])")

def _fm(text):
    text = text.replace("\r\n", "\n")  # CRLF files (Windows) parse the same
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    d = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1); d[k.strip()] = v.strip()
    return d

def load_patterns(root):
    """Lines of share.txt, minus blanks and # comments. None if share.txt is missing."""
    p = os.path.join(root, ALLOWLIST)
    if not os.path.exists(p):
        return None
    out = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if line:
                out.append(line.replace("\\", "/"))
    return out

def _forbidden(rel):
    rel = rel.replace("\\", "/")
    return rel.startswith(FORBIDDEN_PREFIXES) or any(fnmatch.fnmatch(rel, g) for g in FORBIDDEN_GLOBS)

def resolve(root, patterns):
    """-> (sorted relative file paths, list of allowlist errors)."""
    files, errors = set(), []
    for pat in patterns:
        if os.path.isabs(pat) or ".." in pat.split("/"):
            errors.append(f"share.txt: '{pat}' must be a relative path inside the repo"); continue
        if _forbidden(pat.rstrip("/") + "/") or _forbidden(pat):
            errors.append(f"share.txt: '{pat}' is private (contacts/, interviews/, inbox/, reports/outreach-* never leave the repo)")
        for hit in glob.glob(os.path.join(root, pat), recursive=True):
            paths = [hit] if os.path.isfile(hit) else [os.path.join(d, f) for d, _, fs in os.walk(hit) for f in fs]
            for p in paths:
                rel = os.path.relpath(p, root).replace("\\", "/")
                if rel.startswith(".git/"): continue
                if _forbidden(rel):
                    errors.append(f"share.txt: '{pat}' matches private file {rel}")
                else:
                    files.add(rel)
    return sorted(files), errors

def contact_names(root):
    """Full names and first names (4+ letters) from contacts/*.md `name:` fields."""
    names = set()
    cdir = os.path.join(root, "contacts")
    for fn in sorted(os.listdir(cdir)) if os.path.isdir(cdir) else []:
        if not fn.endswith(".md"): continue
        with open(os.path.join(cdir, fn), encoding="utf-8") as f:
            name = _fm(f.read()).get("name", "").strip()
        if not name: continue
        names.add(name)
        first = name.split()[0]
        if len(re.sub(r"[^A-Za-z]", "", first)) >= 4:
            names.add(first)
    return sorted(names, key=len, reverse=True)

def scan(root, files):
    """-> list of 'file:line: kind: match' strings for every hit."""
    names = contact_names(root)
    name_re = re.compile(r"(?<![\w])(?:" + "|".join(re.escape(n) for n in names) + r")(?![\w])", re.I) if names else None
    hits = []
    for rel in files:
        try:
            with open(os.path.join(root, rel), encoding="utf-8") as f:
                lines = f.read().splitlines()
        except UnicodeDecodeError:
            hits.append(f"{rel}: not a UTF-8 text file; can't be scanned, so it can't be shared"); continue
        for n, line in enumerate(lines, 1):
            for kind, rx in (("email", EMAIL), ("phone", PHONE), ("contact name", name_re)):
                for m in (rx.finditer(line) if rx else []):
                    hits.append(f"{rel}:{n}: {kind}: {m.group(0)}")
    return hits

def check(root):
    """Everything check.py and export_share.py need. -> (files, errors); errors empty means shareable."""
    patterns = load_patterns(root)
    if patterns is None:
        return [], []
    files, errors = resolve(root, patterns)
    return files, errors + scan(root, files)
