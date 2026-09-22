# Adapters

Adapters are **search and verification hints** for ChatGPT Web. They are not deterministic dependency graphs.

Language adapters describe:
- how to search for likely target symbols/files;
- how to inspect direct dependencies;
- how to search reverse consumers;
- useful project-native verification tools;
- static-analysis limitations.

Framework adapters add framework-native context such as routes, components, providers, jobs, hooks or file-system routing.

The session/plan skills should combine all detected language/framework hints but keep the actual model context bounded. Current source, native tooling, tests and CI remain authoritative.
