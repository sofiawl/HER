NOTE: leftover from an old `/her:teach` demo. The current skill writes one Obsidian note instead.

# Glossary

## Babashka
A fast-starting native Clojure interpreter for scripting, run as the `bb` command. Aimed at jobs you might otherwise give to bash. Example: `bb -e '(+ 1 2)'` prints `3`.
Not to be confused with: full Clojure on the JVM (same language family, different runtime).
First seen: [0001 What Babashka Is](../lessons/0001-what-babashka-is.md)

## SCI
Small Clojure Interpreter: the engine inside Babashka that runs Clojure forms without compiling them like a normal JVM Clojure app.
Not to be confused with: the Babashka binary itself (`bb` is the product; SCI is inside it).
First seen: [0001 What Babashka Is](../lessons/0001-what-babashka-is.md)

## Native binary
A program the OS runs directly (here: Babashka built with GraalVM), so you do not need a separate JVM install just to start it.
Not to be confused with: "native" as in mobile/iOS.
First seen: [0001 What Babashka Is](../lessons/0001-what-babashka-is.md)
