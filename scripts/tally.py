#!/usr/bin/env python3
"""Deterministic tally for the discovery repo.

Counts interviews by persona, commitments, open loops, insight replication and
kill-rule status by parsing frontmatter and the extraction blocks. No LLM, no
guessing: if it isn't written in a file with the right heading, it isn't counted.

Usage:  python3 scripts/tally.py [--json] [--root PATH]
"""
import argparse, json, os, re, sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KILL_RULE = {"interviews": 15, "come_back": 3, "artifact_or_pilot": 1}
NON_COUNTING = {"intermediary"}  # context only: excluded from kill-rule interviews and commitments
COMMITMENT_TYPES = ["artifact", "intro", "follow-up", "pilot", "prepay", "come-back"]

def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()

def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    fm = {}
    if not m:
        return fm, text
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, text[m.end():]

def parse_list(v):
    v = (v or "").strip()
    if v.startswith("[") and v.endswith("]"):
        v = v[1:-1]
    return [x.strip().strip("'\"") for x in v.split(",") if x.strip()]

def section(body, heading):
    """Return the bullet lines under a '### heading' inside the extraction block."""
    m = re.search(r"^###\s+" + re.escape(heading) + r"\s*$\n(.*?)(?=^###\s|^## |\Z)", body, re.S | re.M)
    if not m:
        return []
    return [l[2:].strip() for l in m.group(1).splitlines() if l.strip().startswith("- ")]

def parse_loop(line):
    """'2026-09-25 | owe | send thank-you | done' -> dict. Missing fields tolerated."""
    if line.startswith("(") or "|" not in line:
        return {"date": "", "what": line, "status": "done"}  # a note, not a loop
    parts = [p.strip() for p in line.split("|")]
    d = {"date": "", "what": line, "status": "open"}
    if len(parts) >= 2:
        d["date"] = parts[0]
        d["what"] = parts[1] if len(parts) == 2 else " | ".join(parts[1:-1]) if parts[-1].lower() in ("open", "done") else " | ".join(parts[1:])
        if parts[-1].lower() in ("open", "done"):
            d["status"] = parts[-1].lower()
    return d

def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles default to cp1252, which can't print → or ≥
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--root", default=ROOT)
    a = ap.parse_args()
    root = a.root

    out = {"date": str(date.today()), "interviews": [], "by_persona": {}, "commitments": {t: 0 for t in COMMITMENT_TYPES},
           "commitment_lines": [], "i_owe": [], "they_owe": [], "referrals": [], "unextracted": [], "unreviewed": [],
           "insights": [], "contacts": {"total": 0, "by_status": {}}, "kill_rule": {}}

    idir = os.path.join(root, "interviews")
    for fn in sorted(os.listdir(idir)) if os.path.isdir(idir) else []:
        if not fn.endswith(".md"):
            continue
        text = read(os.path.join(idir, fn))
        fm, body = frontmatter(text)
        iid = fm.get("id", fn[:-3])
        persona = fm.get("persona", "unknown")
        out["interviews"].append({"id": iid, "persona": persona, "date": fm.get("date", ""), "name": fm.get("name", ""), "firm": fm.get("firm", "")})
        out["by_persona"][persona] = out["by_persona"].get(persona, 0) + 1
        if fm.get("extracted", "no").lower() != "yes":
            out["unextracted"].append(iid)
            continue
        if fm.get("reviewed", "no").lower() != "yes":
            out["unreviewed"].append(iid)
        for line in section(body, "Commitments obtained"):
            m = re.match(r"\[(\w[\w-]*)\]\s*(.*)", line)
            if m and m.group(1) in COMMITMENT_TYPES:
                if persona not in NON_COUNTING:
                    out["commitments"][m.group(1)] += 1
                out["commitment_lines"].append({"interview": iid, "type": m.group(1), "what": m.group(2)})
        for line in section(body, "Asks I owe them"):
            d = parse_loop(line); d["interview"] = iid
            if d["status"] == "open":
                out["i_owe"].append(d)
        for line in section(body, "They owe me"):
            d = parse_loop(line); d["interview"] = iid
            if d["status"] == "open":
                out["they_owe"].append(d)
        for line in section(body, "Referrals given"):
            out["referrals"].append({"interview": iid, "who": line})

    sdir = os.path.join(root, "insights")
    for fn in sorted(os.listdir(sdir)) if os.path.isdir(sdir) else []:
        if not fn.endswith(".md"):
            continue
        fm, _ = frontmatter(read(os.path.join(sdir, fn)))
        sup = parse_list(fm.get("supporting_interviews"))
        con = parse_list(fm.get("contradicting_interviews"))
        out["insights"].append({"id": fm.get("id", fn[:-3]), "title": fm.get("title", ""), "support": len(sup),
                                "contradict": len(con), "status": fm.get("status", ""), "supporting": sup})

    cdir = os.path.join(root, "contacts")
    for fn in sorted(os.listdir(cdir)) if os.path.isdir(cdir) else []:
        if not fn.endswith(".md"):
            continue
        fm, _ = frontmatter(read(os.path.join(cdir, fn)))
        out["contacts"]["total"] += 1
        st = fm.get("status", "unknown")
        out["contacts"]["by_status"][st] = out["contacts"]["by_status"].get(st, 0) + 1

    # Replication matches the synthesize skill: ≥3 supporting interviews across ≥2 distinct firms (blank firms don't count).
    firm_of = {i["id"]: i["firm"].strip().lower() for i in out["interviews"]}
    for i in out["insights"]:
        i["firms"] = len({firm_of[x] for x in i["supporting"] if firm_of.get(x)})

    n_all = len(out["interviews"])
    n = sum(1 for i in out["interviews"] if i["persona"] not in NON_COUNTING)
    cb = out["commitments"]["come-back"]
    ap_ = out["commitments"]["artifact"] + out["commitments"]["pilot"] + out["commitments"]["prepay"]
    out["kill_rule"] = {
        "interviews": f"{n}/{KILL_RULE['interviews']}",
        "come_back": f"{cb}/{KILL_RULE['come_back']}",
        "artifact_or_pilot": f"{ap_}/{KILL_RULE['artifact_or_pilot']}",
        "met": n >= KILL_RULE["interviews"] and cb >= KILL_RULE["come_back"] and ap_ >= KILL_RULE["artifact_or_pilot"],
        "replicated_insights": [i["id"] for i in out["insights"] if i["support"] >= 3 and i["firms"] >= 2],
    }
    for k in ("i_owe", "they_owe"):
        out[k].sort(key=lambda d: d["date"] or "9999")

    if a.json:
        print(json.dumps(out, indent=2)); return

    print(f"Tally — {out['date']}")
    print(f"Interviews: {n_all} total, {n} (excl. intermediaries)  by persona: {out['by_persona']}")
    print(f"Contacts: {out['contacts']['total']}  by status: {out['contacts']['by_status']}")
    print(f"Commitments (excl. intermediaries): {out['commitments']}")
    print(f"Unextracted: {out['unextracted'] or 'none'}   Unreviewed: {out['unreviewed'] or 'none'}")
    print("\nInsights:")
    for i in out["insights"]:
        print(f"  {i['id']}  support={i['support']} firms={i['firms']} contradict={i['contradict']}  [{i['status']}]  {i['title']}")
    print("\nOpen loops — I owe them:")
    for d in out["i_owe"]:
        print(f"  {d['date'] or '????-??-??'}  {d['interview']}  {d['what']}")
    print("Open loops — they owe me:")
    for d in out["they_owe"]:
        print(f"  {d['date'] or '????-??-??'}  {d['interview']}  {d['what']}")
    print("\nReferrals:")
    for r in out["referrals"]:
        print(f"  {r['interview']}  {r['who']}")
    kr = out["kill_rule"]
    print(f"\nKill rule (excl. intermediaries): interviews {kr['interviews']}, come-back {kr['come_back']}, artifact/pilot {kr['artifact_or_pilot']}  → {'MET' if kr['met'] else 'not yet'}")
    print(f"Replicated insights (≥3 interviews, ≥2 firms): {kr['replicated_insights'] or 'none'}")

if __name__ == "__main__":
    main()
