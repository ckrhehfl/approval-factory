# PR Loop Fixture Examples

These files are inert examples for the future `artifacts/pr_loop/<PR-ID>/...` layout proposed in `docs/proposals/pr-loop-runner.md`.

They are not runtime artifacts, runtime source of truth, approval inputs, queue inputs, merge-gate inputs, or CLI inputs. They live under `tests/fixtures/pr_loop/` so tests can verify expected example shape without introducing `orchestrator/pr_loop/` runtime code, state load/save behavior, phase-machine behavior, or top-level active state.

## Fixture scope

- `schema/pr-loop-artifact-manifest.yaml` lists the required example files and required low-level fields.
- `examples/artifacts/pr_loop/PR-113/` mirrors the proposed future artifact layout under a non-runtime fixture root.
- Markdown files intentionally include fixture-only wording so they cannot be mistaken for live review, gate, approval, or merge evidence.

## Authority boundary

The fixture examples do not introduce a policy source, runtime authority, or merge authority. Any future runtime use of `artifacts/pr_loop/<PR-ID>/...` still requires a separate approved design and implementation PR.
