# Inspirations

Projects that shaped HER. Some we rewrote into skills. Some we looked at and left alone. Full credit and MIT notice at the end.

| Source | What it is | Where it shows up in HER |
|---|---|---|
| [obra/superpowers](https://github.com/obra/superpowers) | Agentic skills framework and software methodology | `judge/VERIFY.md`, shared with `/her:to-pr` |
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | Think like the laziest senior in the room | `/her:lazy` |
| [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | Codebase as a queryable knowledge graph | Not used (overlaps Understand-Anything) |
| [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | Terse agent talk; engine/proxy are BSL, we only use the skill idea | `/her:caveman` |
| [Egonex-AI/Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) | Interactive knowledge graph over a repo | Optional `/her:understand` if you still wire it |
| [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | What people said in the last 30 days across the open web | Discourse mode inside `/her:research` |
| [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) | Next-action-first output | `/her:adhd` |
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | Large scientific skill pack | Surveyed for `/her:report`, not installed |
| [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | Editorial HTML/SVG diagrams | Not used; `/her:diagram` was Mermaid-first when we had it |
| [unclebob/swarm-forge](https://github.com/unclebob/swarm-forge) | Multi-agent worktrees and tmux | Not used; rule 6 subagents cover that job |
| [ask-matt](https://github.com/mattpocock/skills/blob/main/skills/engineering/ask-matt/SKILL.md) | Router over Matt's skills | `/her:ask-her` (structure only) |
| [to-tickets](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-tickets/SKILL.md) | Tracer-bullet tickets with edges | Folded into `/her:to-pr` |
| [prototype](https://github.com/mattpocock/skills/blob/main/skills/engineering/prototype/SKILL.md) | Throwaway prototype for one design question | Mode inside `/her:research` |
| [research](https://github.com/mattpocock/skills/blob/main/skills/engineering/research/SKILL.md) | Cited primary-source research note | `/her:research` |
| [grilling](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md) | Relentless one-question interview | `/her:grilling` |
| [handoff](https://github.com/mattpocock/skills/blob/main/skills/productivity/handoff/SKILL.md) | Compact the chat for the next agent | `/her:handoff` |
| [teach](https://github.com/mattpocock/skills/blob/main/skills/productivity/teach/SKILL.md) | Multi-session teaching workspace | `/her:teach` |
| [mattpocock/skills](https://github.com/mattpocock/skills) | Parent of the Matt skills above | grill-me, grilling, handoff, teach, research, to-pr planning |
| [akitaonrails/ai-memory](https://github.com/akitaonrails/ai-memory) | Cross-harness project wiki + hooks | `/her:memory` (binary not vendored) |
| [typesafe-ai / Jev](https://docs.typesafe.ai/llms.txt) | System One typed judgments | Optional judgments; not a HER skill yet |
| [tamaratran/fast-jev-compaction](https://github.com/tamaratran/fast-jev-compaction) | Compaction experiment | Keep disabled unless you accept the risks |

Local wiki UI when ai-memory is running: [http://127.0.0.1:49374](http://127.0.0.1:49374). Older dated snapshots of HER itself live in [`LOG.md`](./LOG.md).

## Credits

HER skills are rewritten in HER's own words. Wrappers call upstream plugins; we do not vendor their code into this repo.

MIT License notice (applies to adapted material): Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files, to deal in the Software without restriction, subject to including the copyright notice and this permission notice in all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
