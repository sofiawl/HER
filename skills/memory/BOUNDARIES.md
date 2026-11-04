# Where memory lives (HER + ai-memory)

One fact, one home. Do not mirror the same paragraph in two places.

| Store | Owns | HER touch |
|---|---|---|
| **ai-memory wiki** (per repo checkout) | What happened in this project: sessions, tool work, compiled pages, searchable history | `/her:memory` installs and wires hooks; session end captures automatically |
| **`~/.her/runs/<id>/`** | Orchestrator ledger: `decisions.md`, `plan.json`, step reports, `summary.md` | Wiki **points at paths**, never paste the plan |
| **Kineloop** | Cards, team status, pt-BR descriptions and comments | Ticket truth for shipping; link `https://loop.zslippy.com/issue/<CARD>` |
| **Obsidian** (`ObsidianPipa`) | Personal learning (`/her:teach`), debate records (`/her:debate`), research notes | Not the project wiki; link from ai-memory pages if useful |
| **Git repo** | Specs, ADRs, code, committed docs | Source of truth for design; ai-memory summarizes and links |
| **Other chat** | Whatever that session still holds | Paste the session link into the new Claude or Cursor chat |

**Do not put in ai-memory:** secrets, raw tokens, uncommitted `.scratch/` paths as the only copy of something the team needs (same rule as Kineloop).

**MemPalace:** not part of HER. See [ai-memory's MemPalace notes](https://github.com/akitaonrails/ai-memory/blob/main/docs/issues-mempalace.md) if comparing tools; prefer ai-memory for local project memory.
