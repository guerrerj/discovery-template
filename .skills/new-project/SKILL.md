---
name: new-project
description: Bootstrap a fresh customer-discovery repo for a new startup idea from this template — scaffold the folder, set personas, and write the project brief, starting hypotheses and persona rules from the founder's one-paragraph description. Use whenever the user says they have a new idea, want to start discovery on something else, want to "set up the repo for X", or asks to reuse this method for another project or team.
---

# New project

Purpose: go from "I have an idea" to a repo that can take its first interview in under fifteen minutes, with hypotheses written down *before* the first conversation so they can't be back-fitted later.

## Steps

1. **Get the brief.** Ask the user for, or extract from the conversation: the idea in one paragraph (their words), who they think has the problem, who they think pays, what alternatives exist, and a project name. Ask at most three questions; if something is unknown, it becomes a hypothesis, not a blocker.

2. **Derive the personas.** From the brief, list 3–6 personas: distinct roles who experience, decide on, or influence the problem (e.g. owner / manager / front-desk / member). Always include `intermediary`. Use lowercase, hyphenated, one or two words. Confirm the list with the user in one line.

3. **Scaffold.** Pick the mode:
   - **Default, `--here`:** use it when you're inside a fresh clone of the template, meaning `project.md` still starts with `# <Project name> — project brief` and `contacts/`, `interviews/` and `insights/` hold only `.gitkeep`. Run
     `python3 scripts/new_project.py --here --name "<Name>" --slug <slug> --personas <a,b,c>`
     It turns this repo into the project, installs the hooks and commits `new-project: <Name>`. In the steps below, "the new repo" is this repo. If it refuses, report its message; don't work around it.
   - **`--dest <path>`:** only if the user asks for a separate folder, or this isn't a fresh template clone. It copies the method into a new folder; you'll tell the user to `git init` it in step 11.
   Either way the script sets personas in check.py, templates and the intake skill, and writes stubs for `project.md` and `hypotheses.md` plus a default `share.txt`. The sharing scripts (`coverage.py`, `export_share.py`) and the share scan in `check.py` come with the method.

4. **Fill `project.md`** in the new repo from the brief. Keep the founder's words for the idea paragraph. Under "What would kill it", write the two or three findings that would mean the idea is wrong (these become the interview targets).

5. **Write `hypotheses.md`**: 4–7 hypotheses, each with `**Statement:**`, `**Status:** untested`, `**Evidence:** —`, `**Log:**` (empty). Cover at minimum: the core pain, who the buyer is, who the user is, why they haven't solved it already / what they'd switch from, and pricing or willingness to pay. Number them HYP-001 upward. Phrase each so an interview can contradict it.

6. **Fill the persona rules** in the new repo's `.skills/intake/SKILL.md` — one line per persona saying who counts (job titles, role descriptions), so intake classifies consistently.

7. **Replace the generic examples** in the new repo's extract and synthesize skills. The script doesn't touch these; rewrite each with an example from the new domain using the new personas, keeping the point it illustrates:
   - `.skills/extract/SKILL.md`, step 1: `(a front-line user's pains are day-to-day tasks; a manager's are reporting, cost and staffing)` — two personas whose pains live in different phases or contexts.
   - `.skills/extract/SKILL.md`, Rules: ``"I'll send you the spreadsheet we use" is `[artifact]` `` — a document or file this domain's personas would actually share.
   - `.skills/synthesize/SKILL.md`, Rules, "Persona matters": `A manager saying "reporting works fine" and a front-line user saying "handoffs are painful" are not in tension` — two new personas with different pains.
   - `.skills/synthesize/SKILL.md`, Rules, "Don't smooth contradictions": `If INT-003 says the manager approves exceptions and INT-005 says the front-line user does` — two new personas disagreeing about who owns a task.
   Then run `grep -nF -e "pains are day-to-day tasks" -e "the spreadsheet we use" -e "reporting works fine" -e "handoffs are painful" -e "manager approves exceptions" .skills/extract/SKILL.md .skills/synthesize/SKILL.md` in the new repo; it should print nothing. It matches the exact example phrases, so it still works when one of the new personas is called `manager` or `user`. (The intake persona placeholder is already replaced by the script.)

8. **Edit `CLAUDE.md` rule 12** in the new repo to name the new product (the script substitutes the name for "the product"; check it reads correctly).

9. **Suggest the first batch**: 15 contacts split across personas and intermediaries, and two or three intermediary types for this domain. Put this in `reports/plan-first-batch.md`.

10. **Confirm the sharing allowlist.** Show the user the new repo's `share.txt` (default: `hypotheses.md`, `guides/*.md`, `reports/synthesis-*.md`, `reports/team-coverage.md`) and ask who will receive exports for this project and whether anything should be added or removed. Edit `share.txt` to match their answer. Never add `contacts/`, `interviews/`, `inbox/` or `reports/outreach-*`; `check.py` blocks them, and listed files must refer to people by CON-### only.

11. **Hand over.**
   - With `--here`: the hooks are installed and the scaffold is committed. Commit the files you filled in steps 4–10 (`new-project: brief, hypotheses, personas`) and tell the user to `git push` to their private repo.
   - With `--dest`: tell the user to run `git init && sh scripts/install-hooks.sh` in the new folder and push it to a new private repo.

   Either way, `python3 scripts/check.py` should print OK with no interviews. Remind the user that interviews open broad and hypotheses are not shown to interviewees.

## Rules

- Hypotheses are guesses, labelled as such. Never write "validated" or "supported" at creation.
- Don't carry insights, contacts or interviews from another project into the new one; the method transfers, the evidence doesn't.
- Don't add features, mockups or architecture to `project.md`. It describes the problem and the people, not the solution.
- If the user's brief is really two ideas, say so and ask which to scaffold first.

## Before finishing
Run `python3 scripts/check.py` in the new repo; report the result and the path.
