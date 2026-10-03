#!/usr/bin/env python3
"""Structural checks for the discovery repo. Exit 1 on any failure.

- interview frontmatter has required fields; raw notes match raw_sha if set
- extracted interviews have every required extraction heading
- open-loop lines have a date
- insight supporting/contradicting IDs exist
- hypothesis log lines cite an INS/INT id
- share.txt lists no private paths, and its files carry no emails, phones or contact names (sharescan.py)
- flags unextracted / unreviewed interviews (warning, not failure)
Usage: python3 scripts/check.py [--root PATH] [--strict]  (--strict makes warnings fail)
"""
import argparse, hashlib, os, re, sys

sys.dont_write_bytecode = True  # no __pycache__ in the repo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sharescan  # same scan as export_share.py, so the two can't drift

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQ_INT = ["id", "contact", "persona", "date", "format", "extracted", "reviewed"]
REQ_HEADINGS = ["Summary", "Pains", "Unprompted vs prompted", "Workarounds they built", "Tools they pay for",
                "Commitments obtained", "Asks I owe them", "They owe me", "Referrals given", "Vocabulary",
                "Contradicts or complicates our thinking", "Candidate insights"]
PERSONAS = {"buyer", "user", "influencer", "intermediary"}

def read(p):
    with open(p, encoding="utf-8") as f: return f.read()

def fm(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    d = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1); d[k.strip()] = v.strip()
    return d, (text[m.end():] if m else text)

def raw_section(body):
    m = re.search(r"^## Raw notes\s*\n(.*?)(?=^## Extraction|\Z)", body, re.S | re.M)
    return m.group(1) if m else ""

def sha(s):
    return hashlib.sha256(s.strip().encode("utf-8")).hexdigest()[:16]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--root", default=ROOT); ap.add_argument("--strict", action="store_true")
    a = ap.parse_args(); root = a.root
    errors, warns = [], []
    ids = {"INT": set(), "INS": set(), "CON": set()}

    cdir = os.path.join(root, "contacts")
    for fn in sorted(os.listdir(cdir)) if os.path.isdir(cdir) else []:
        if fn.endswith(".md"):
            d, _ = fm(read(os.path.join(cdir, fn)))
            if d.get("id"): ids["CON"].add(d["id"])

    idir = os.path.join(root, "interviews")
    for fn in sorted(os.listdir(idir)) if os.path.isdir(idir) else []:
        if not fn.endswith(".md"): continue
        p = os.path.join(idir, fn); d, body = fm(read(p)); iid = d.get("id", fn)
        ids["INT"].add(iid)
        for k in REQ_INT:
            if not d.get(k): errors.append(f"{fn}: missing frontmatter '{k}'")
        if d.get("persona") and d["persona"] not in PERSONAS:
            errors.append(f"{fn}: persona '{d['persona']}' not in {sorted(PERSONAS)}")
        if d.get("contact") and d["contact"] not in ids["CON"]:
            errors.append(f"{fn}: contact {d['contact']} has no file in contacts/")
        raw = raw_section(body)
        if not raw.strip(): errors.append(f"{fn}: empty '## Raw notes'")
        if d.get("raw_sha"):
            if sha(raw) != d["raw_sha"]:
                errors.append(f"{fn}: RAW NOTES CHANGED since intake (raw_sha mismatch)")
        else:
            warns.append(f"{fn}: no raw_sha — run 'python3 scripts/check.py --seal {iid}' or let intake set it")
        if d.get("extracted", "no").lower() == "yes":
            for h in REQ_HEADINGS:
                if not re.search(r"^###\s+" + re.escape(h), body, re.M):
                    errors.append(f"{fn}: extraction missing heading '### {h}'")
            for h in ("Asks I owe them", "They owe me"):
                m = re.search(r"^###\s+" + re.escape(h) + r"\s*$\n(.*?)(?=^###\s|^## |\Z)", body, re.S | re.M)
                for l in (m.group(1).splitlines() if m else []):
                    l = l.strip()
                    if l.startswith("- ") and not l.startswith("- (") and not re.match(r"- \d{4}-\d{2}-\d{2} \|", l):
                        errors.append(f"{fn}: loop line without date under '{h}': {l[:60]}")
            if d.get("reviewed", "no").lower() != "yes":
                warns.append(f"{fn}: extracted but not reviewed")
        else:
            warns.append(f"{fn}: not extracted yet")

    sdir = os.path.join(root, "insights")
    for fn in sorted(os.listdir(sdir)) if os.path.isdir(sdir) else []:
        if not fn.endswith(".md"): continue
        d, body = fm(read(os.path.join(sdir, fn))); ids["INS"].add(d.get("id", fn))
        for key in ("supporting_interviews", "contradicting_interviews"):
            v = d.get(key, "").strip("[] ")
            for x in [s.strip() for s in v.split(",") if s.strip()]:
                if x not in ids["INT"]: errors.append(f"{fn}: {key} references unknown {x}")
        if not re.search(r"^- INT-\d+", body, re.M):
            errors.append(f"{fn}: no evidence line with an INT-### id")

    hp = os.path.join(root, "hypotheses.md")
    if os.path.exists(hp):
        in_log = False
        for n, line in enumerate(read(hp).splitlines(), 1):
            if line.startswith("**Log:**"): in_log = True; continue
            if line.startswith("## "): in_log = False
            if in_log and line.startswith("- ") and not re.search(r"(INS|INT)-\d+", line):
                errors.append(f"hypotheses.md:{n}: log line cites no INS/INT id")

    _, share_errors = sharescan.check(root)
    errors += share_errors

    for e in errors: print("ERROR ", e)
    for w in warns: print("WARN  ", w)
    if errors or (a.strict and warns):
        print(f"\ncheck: FAILED ({len(errors)} errors, {len(warns)} warnings)"); sys.exit(1)
    print(f"check: OK ({len(warns)} warnings)")

if __name__ == "__main__":
    if "--seal" in sys.argv:
        # seal raw notes: write raw_sha into the interview frontmatter
        sp = argparse.ArgumentParser(); sp.add_argument("--seal", required=True, metavar="INT-###"); sp.add_argument("--root", default=ROOT)
        sa = sp.parse_args(); iid = sa.seal
        p = os.path.join(sa.root, "interviews", f"{iid}.md")
        if not os.path.isfile(p):
            sys.exit(f"seal: no interview file for '{iid}' at {p} (expected e.g. --seal INT-007)")
        t = read(p); d, body = fm(t)
        if not raw_section(body).strip():
            sys.exit(f"seal: {iid} has an empty '## Raw notes' section; paste the notes before sealing")
        s = sha(raw_section(body))
        if "raw_sha:" in t:
            t = re.sub(r"raw_sha:.*", f"raw_sha: {s}", t, count=1)
        else:
            t = t.replace("\n---\n", f"\nraw_sha: {s}\n---\n", 1)
        with open(p, "w", encoding="utf-8", newline="\n") as f: f.write(t)
        print(f"sealed {iid} raw_sha={s}")
    else:
        main()
