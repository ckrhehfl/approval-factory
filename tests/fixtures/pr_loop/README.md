# PR Loop Fixture Examples

These files are inert examples for the future `artifacts/pr_loop/PR-<number>/...` layout proposed in `docs/proposals/pr-loop-runner.md`.

They are not runtime artifacts, runtime source of truth, approval inputs, queue inputs, or merge-gate inputs. They live under `tests/fixtures/pr_loop/` so tests can verify expected example shape without introducing PR Loop runtime state load/save behavior, phase-machine behavior, or top-level active state.

`factory pr-loop inspect --pr-id PR-<number>` may read these files as local non-runtime fixtures for operator-visible fact summaries only. `factory pr-loop gate-check --pr-id PR-<number>` may read the same local non-runtime fixtures for deterministic condition summaries only. `factory pr-loop render-review --pr-id PR-<number>` may combine the same read-only fixture inspect and gate-check summaries into a markdown review packet draft only. `factory pr-loop merge --pr-id PR-<number> --dry-run` may combine the same read-only fixture inspect, gate-check, and review packet surfaces into a neutral merge dry-run summary only. Non-canonical selectors such as `latest`, `current`, `PR-1A`, or `PR-1-FOO` are refused. These paths and rendered packets do not make the fixtures live runtime state, policy authority, gate evidence, queue input, status input, approval authority, review verdict, or merge authority.

## Fixture scope

- `schema/pr-loop-artifact-manifest.yaml` lists the required example files and required low-level fields.
- `examples/artifacts/pr_loop/PR-113/` mirrors the proposed future artifact layout under a non-runtime fixture root.
- Markdown files intentionally include fixture-only wording so they cannot be mistaken for live review, gate, approval, or merge evidence.

## Authority boundary

The fixture examples do not introduce a policy source, runtime authority, or merge authority. Any future runtime use of `artifacts/pr_loop/PR-<number>/...` still requires a separate accepted design and implementation PR.
