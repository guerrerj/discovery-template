**Keep your copy PRIVATE: it will hold real people's contact details and interview notes.**

# Discovery template — a traceable customer-discovery method

## Using this for your own project

1. Click **Use this template** and set your new repo to **Private**. It will hold real people's contact details and interview notes. Never make it public.
2. **Requirements:** Python 3.7+ (standard library only), git, and Claude Code for the skills (intake, extract, synthesize, weekly-review, new-project). The scripts work without Claude Code.
3. **Quickstart:** clone your private repo, then, inside it:
   ```
   python3 scripts/new_project.py --here --name "<Name>" --slug <slug> --personas <a,b,c>
   git push
   ```
   This sets up the project in place, installs the hooks and commits. Your private repo now holds the method and your data. Or ask Claude Code to "run the new-project skill". On Windows, use `python` or `py -3` if `python3` isn't found.
   *Advanced:* `--dest ../<slug>-discovery` instead of `--here` scaffolds a separate folder that you `git init` and push yourself.

A folder of Markdown files, five skills and six small Python scripts for running customer discovery with an LLM agent. Any agent that can read files and follow a SKILL.md (Claude Code, Cowork, or a chat with the files attached) runs the method; the scripts do the checking and counting, so numbers are never hallucinated.

This repo holds only the method. Each idea gets its own private discovery repo, scaffolded from here; evidence never comes back into the template.

**Requires Python 3.7+, standard library only.** On Windows, use `python` or `py -3` wherever the docs say `python3` if `python3` isn't available; see `USAGE.md`.

## Layout

```
.skills/        the method: intake, extract, synthesize, weekly-review, new-project
scripts/        check.py         structure, raw-notes seal and share scan; runs on every commit
                tally.py         counts, open loops and kill-rule status
                new_project.py   scaffolds a private project repo from this template
                coverage.py      writes reports/team-coverage.md (firm, region, owner, status only)
                export_share.py  copies the share.txt files to a folder for the team, if the scan passes
                sharescan.py     the shared scan for emails, phone numbers and contact names
                install-hooks.sh installs the pre-commit hook and copies the skills
share.txt       allowlist of the only files that may leave the repo
guides/         interview-sheet.md: the one-page script every interviewer uses
templates/      blank contact, interview, insight and weekly files
inbox/          raw material goes here: typed notes, transcripts, emails
contacts/       one file per person   (CON-001-firstname-lastname.md)
interviews/     one file per conversation (INT-001.md): frontmatter, raw notes, extracted block
insights/       one file per pattern (INS-001.md), each linking its supporting interviews
reports/        weekly notes and kill-rule status
hypotheses.md   header and kill rule; HYP-001.. are written per project before interview one
project.md      the idea brief stub, filled per project
CLAUDE.md       rules every agent must follow
USAGE.md        how to drive the skills with an agent
```

## Starting a project

1. Make your private copy with **Use this template** and clone it (see the top of this file).
2. Inside the clone, ask the agent to run the **new-project** skill:
   ```
   > Run the new-project skill. Idea: <one paragraph>. Name: <name>.
   ```
   It runs `scripts/new_project.py --here` to turn the clone into your project, installs the hooks and commits. It then writes `project.md`, a starting `hypotheses.md`, persona rules and a first-batch plan.
3. `python3 scripts/check.py` should print OK with no interviews; then `git push`.
4. Keep the repo private (see `CONTRIBUTING.md`). *Advanced:* `--dest <path>` scaffolds a separate folder instead.

## The loop

1. After a conversation, put the raw notes in `inbox/`.
2. **intake** creates or updates the contact and creates the interview file; raw notes are sealed and never altered.
3. **extract** appends a structured block: pains as verbatim quotes, workarounds, tools, commitments, open loops, referrals, vocabulary. A human reviews it.
4. Every 4–5 interviews, **synthesize** links pains to insights and updates hypothesis statuses with written reasoning.
5. Fridays, **weekly-review** runs `scripts/tally.py` and writes the week's note with open loops and kill-rule status.

## Principles the method enforces

- **Hypotheses and a kill rule are written before interview one**, so they can't be back-fitted.
- **Raw notes are immutable.** `check.py` fails if a sealed raw section changes.
- **Every claim carries an ID.** Pains cite `INT-###`, patterns cite `INS-###`, hypothesis statuses cite insights.
- **Quotes are verbatim**; reconstructed wording is marked `~paraphrase:`.
- **Numbers come from `scripts/tally.py` only**, never from the model re-reading files.
- **Commitments are signal, compliments are noise.** Time, intros, artifacts and money count; "sounds great" doesn't.
- **Ask about the past, not the future**; open broad, then narrow; never lead with the hypothesis.
- **No product work until the kill rule says so.**
- **The method transfers; the evidence never does.**
- **A sharing boundary keeps contact details in.** Only files listed in `share.txt` leave a project repo, via `scripts/export_share.py`, and only if the scan finds no emails, phone numbers or contact names; `check.py` runs the same scan on every commit.

## Licence

The method in this repo (skills, scripts, templates and docs) is released under the MIT licence; see `LICENSE`. Project repos scaffolded from it contain interview data given in confidence and are not covered by this licence or meant to be shared.
