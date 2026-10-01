NOTE: leftover from an old `/her:teach` demo. The current skill writes one Obsidian note instead.

# 0001 What Babashka Is

Mission link: decide SwarmForge Q14 (Babashka vs Python for the throwaway).

## You already know

You treat a scripting language as **commands in the terminal that automate something**. Babashka's authors aim at that same job: places you would otherwise write **bash**.

Primary sources: [babashka.org](https://babashka.org/), [GitHub README](https://github.com/babashka/babashka), [Babashka book](https://book.babashka.org/).

## The idea

**Babashka** (`bb`) is a **fast-starting, native Clojure interpreter for scripting**.

Break that down:

| Word | Meaning |
|---|---|
| Clojure | A Lisp (lots of parentheses). Same family as the `(+ 1 2)` shape you have seen. |
| Interpreter | Runs your script form by form. It does not compile it the way full JVM Clojure apps usually do. |
| Native | Shipped as a standalone binary (GraalVM). You do not need to install a JVM just to run `bb`. |
| Fast-starting | Starts in tens of milliseconds, so it feels like a script tool, not a heavy app boot. |

Official goal (README): leverage Clojure where you would use **bash**. Non-goal: replace your shell. You still use zsh; `bb` is a program you call from zsh.

Under the hood it uses **SCI** (Small Clojure Interpreter) inside that native binary. You do not need SCI details to decide Q14.

## Tiny example (shape only)

```bash
bb -e '(+ 1 2)'
# => 3
```

Same idea as a shell one-liner, but the language inside is Clojure, not bash.

## Vs things you might confuse it with

| Thing | Relation to Babashka |
|---|---|
| **bash / zsh** | Same *job* (automate in the terminal). Different *language*. Babashka sits *inside* your shell. |
| **Python** | Also used for scripting. Different language and ecosystem. SwarmForge four-pack does **not** default to Python. |
| **Clojure on the JVM** | Same language family. JVM Clojure boots slower and needs a JDK; better for long-running apps. Babashka is the scripting-shaped cousin. |

## Common misconception

"Babashka replaces my shell."  
No. The README says it is a tool **inside** existing shells and is designed to play well with them.

## Why this matters for Q14

Four-pack's `project.prompt` says **project language: Babashka**, and shared engineering law expects that stack. Choosing Python means you add local overrides and accept more toolchain friction. Choosing Babashka means the kata language is unfamiliar, but the **factory defaults** stop fighting you.

Your own baseline: you already fear toolkit friction more than learning a new language for one kata. That is the decision-relevant fact.

## Primary source to skim (5 min)

[Babashka README: Introduction + Goals and features](https://github.com/babashka/babashka) (stop before deep feature lists).

Ask follow-up questions here anytime. Teacher mode stays on until you answer Q14.
