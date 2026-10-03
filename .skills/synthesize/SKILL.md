---
name: synthesize
description: Cross-interview synthesis for the discovery repo — link extracted pains to existing insights or propose new ones, update supporting/contradicting interview lists and replication status, and update hypothesis statuses in hypotheses.md with cited reasoning. Use every 4–5 interviews, when the user asks "what's the pattern", "has this replicated", "where are we on the hypotheses", or before any mentor/team update.
---

# Synthesize

Purpose: turn a pile of extracted interviews into a small set of insights with replication counts, and keep `hypotheses.md` honest. The model interprets; the script counts.

## Steps

1. **Run the tally first**: `python3 scripts/tally.py --json`. Use its numbers for anything numeric. If it lists unextracted interviews, stop and run extract on them first.

2. **Read** every `insights/INS-*.md` (frontmatter + pattern) and every interview's `### Pains`, `### Workarounds they built`, `### Contradicts or complicates`, and `### Candidate insights` sections.

3. **For each pain or candidate insight**, decide: does it match an existing insight (same underlying pattern, even in different words), or is it new?
   - Match → add the interview ID to that insight's `supporting_interviews` (if not already there) and add the quote under `## Evidence` with its INT-###. If the interview *contradicts* the insight, add it to `contradicting_interviews` and quote it under a `## Counter-evidence` heading.
   - New → create `insights/INS-###.md` from the template, next free number, with the pattern in our words, the quote(s) with IDs, and which HYP-### it bears on.
   - Be stingy with new insights. Two pains that are the same problem from two personas are one insight with `persona_scope` listing both.

4. **Update each insight's status** from its counts: `emerging` (1–2 supporting), `replicated` (≥3 supporting across ≥2 firms), `contradicted` (contradicting ≥ supporting), `retired` (human decision only). Update `last_updated`.

5. **Update `hypotheses.md`.** For each hypothesis, look at the insights that bear on it. Set status: `supported` when ≥1 replicated insight supports it and none contradict; `mixed` when both exist; `contradicted` when a replicated insight contradicts it; otherwise `untested` or `supported (weak)`. Append a dated Log line stating what changed and which INS/INT IDs drove it. Never change a status without a citation.

6. **Write a short synthesis note** to `reports/synthesis-YYYY-MM-DD.md`:
   - Replicated insights (ID, title, count, firms).
   - Emerging insights worth probing next.
   - Contradictions and what would resolve them.
   - Hypothesis changes since last synthesis.
   - Three questions to add to the next interviews.

## Rules

- **Every claim cites an ID.** A sentence in the synthesis note with no INT/INS reference is an opinion and gets marked as such.
- **Different firms count more than repeat interviews at one firm.** Replication requires ≥2 firms.
- **Persona matters.** A manager saying "reporting works fine" and a front-line user saying "handoffs are painful" are not in tension; they're two personas. Record scope.
- **Don't smooth contradictions.** If INT-003 says the manager approves exceptions and INT-005 says the front-line user does, write both down and propose the question that resolves it.
- **Don't propose product features here.** Insights are about the customer's world. Features go in a separate doc once the kill rule is met.

## Before finishing
Run `python3 scripts/check.py`; fix or report failures. Commit with a message naming this skill and the IDs touched. Print the list of changed files.
