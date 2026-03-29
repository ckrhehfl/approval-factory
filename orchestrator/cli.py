from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from orchestrator.pipeline import (
    activate_pr,
    bootstrap_run,
    build_approval_request,
    cleanup_rehearsal_artifacts,
    create_clarification,
    create_goal,
    create_pr_plan,
    create_work_item,
    evaluate_gates,
    get_factory_status,
    record_docs_sync,
    record_qa,
    record_review,
    record_verification,
    resolve_clarification,
    resolve_latest_run_id,
    resolve_approval,
    start_execution,
)


def _default_run_id() -> str:
    return datetime.now(timezone.utc).strftime("RUN-%Y%m%dT%H%M%SZ")


def _render_status(status: dict[str, object]) -> str:
    lines = ["Active PR:"]

    active_pr = status["active_pr"]
    if isinstance(active_pr, dict):
        lines.append(f"- pr_id: {active_pr['pr_id']}")
        lines.append(f"- work_item_id: {active_pr['work_item_id']}")
        if active_pr.get("path"):
            lines.append(f"- path: {active_pr['path']}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Latest Run:")
    latest_run = status["latest_run"]
    if isinstance(latest_run, dict):
        lines.append(f"- run_id: {latest_run['run_id']}")
        lines.append(f"- state: {latest_run['state']}")
        if latest_run.get("path"):
            lines.append(f"- path: {latest_run['path']}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Approval:")
    approval = status["approval"]
    lines.append(f"- status: {approval['status']}")
    if isinstance(approval, dict) and approval.get("path"):
        lines.append(f"- path: {approval['path']}")

    open_clarifications = status["open_clarifications"]
    if isinstance(open_clarifications, list) and open_clarifications:
        lines.append("")
        lines.append(f"Open Clarifications ({len(open_clarifications)}):")
        for clarification_id in open_clarifications:
            lines.append(f"- clarification_id: {clarification_id}")

    return "\n".join(lines)


def _render_create_pr_plan_summary(path: Path, had_active_pr: bool, pr_id: str) -> str:
    lines = ["PR Plan Created:"]
    lines.append(f"- pr_id: {pr_id}")
    lines.append(f"- location: {'archive' if had_active_pr else 'active'}")
    lines.append(f"- path: {path.as_posix()}")
    if had_active_pr:
        lines.append("- reason: active PR already exists, so the new plan was created in archive")
        lines.append(f"- next: factory activate-pr --root . --pr-id {pr_id}")
    else:
        lines.append("- reason: no active PR existed, so the new plan became active")
    return "\n".join(lines)


def _render_activate_pr_summary(pr_id: str, active_path: Path, archived_paths: list[Path]) -> str:
    lines = ["Active PR Updated:"]
    lines.append(f"- active_pr_id: {pr_id}")
    lines.append(f"- active_path: {active_path.as_posix()}")
    if archived_paths:
        for archived_path in archived_paths:
            lines.append(f"- archived_previous_active: {archived_path.as_posix()}")
    else:
        lines.append("- archived_previous_active: none")
    return "\n".join(lines)


def _render_start_execution_error(root_dir: Path, run_id: str) -> str:
    active_dir = root_dir / "prs" / "active"
    active_plans = sorted(active_dir.glob("*.md"))
    if not active_plans:
        return "\n".join(
            [
                "start-execution could not start because there is no active PR plan under prs/active/.",
                "Next action: create a PR plan, or activate the intended archived PR before starting execution.",
                f"Examples: factory create-pr-plan --root . --pr-id PR-XXX --work-item-id WI-XXX --title \"...\" --summary \"...\"; factory activate-pr --root . --pr-id PR-XXX; factory start-execution --root . --run-id {run_id}",
            ]
        )
    if len(active_plans) > 1:
        plan_list = ", ".join(path.as_posix() for path in active_plans)
        return "\n".join(
            [
                f"start-execution could not start because prs/active/ must contain exactly one active PR plan, but found {len(active_plans)}.",
                f"Current active candidates: {plan_list}",
                f"Next action: leave one active PR plan, usually by moving the intended PR through `factory activate-pr --root . --pr-id <id>`, then rerun `factory start-execution --root . --run-id {run_id}`.",
            ]
        )

    pr_plan_path = active_plans[0]
    work_item_id = "unknown"
    current_heading = None
    for raw_line in pr_plan_path.read_text(encoding="utf-8").splitlines():
        if raw_line.startswith("## "):
            current_heading = raw_line[3:].strip()
            continue
        if current_heading == "Work Item ID" and raw_line.strip():
            work_item_id = raw_line.strip()
            break
    work_item_dir = root_dir / "docs" / "work-items"
    expected_exact = work_item_dir / f"{work_item_id}.md"
    matches = sorted(work_item_dir.glob(f"{work_item_id}-*.md"))
    if not expected_exact.exists() and not matches:
        return "\n".join(
            [
                f"start-execution found active PR {pr_plan_path.as_posix()}, but its Work Item ID '{work_item_id}' does not resolve to a work item artifact under docs/work-items/.",
                "Next action: create or restore the matching work item artifact before starting execution.",
                f"Examples: docs/work-items/{work_item_id}.md or docs/work-items/{work_item_id}-<slug>.md; then rerun `factory start-execution --root . --run-id {run_id}`.",
            ]
        )
    return "start-execution could not start because the active PR linkage is invalid."


def _render_cleanup_summary(result: dict[str, object]) -> str:
    include_demo = bool(result["include_demo"])
    mode = str(result["mode"])
    targets = result["targets"]

    lines = ["Cleanup Rehearsal:"]
    lines.append(f"- mode: {mode}")
    lines.append(f"- scope: {'rehearsal+demo' if include_demo else 'rehearsal-only'}")
    lines.append(f"- matched: {result['matched_count']}")

    if isinstance(targets, list) and targets:
        lines.append("")
        lines.append("Targets:")
        for target in targets:
            if isinstance(target, dict):
                lines.append(f"- {target['path']}")
    else:
        lines.append("")
        lines.append("Targets:")
        lines.append("- none")

    return "\n".join(lines)


def _add_run_selector_arguments(parser: argparse.ArgumentParser) -> None:
    selector = parser.add_mutually_exclusive_group()
    selector.add_argument("--run-id")
    selector.add_argument(
        "--latest",
        action="store_true",
        help="Use the latest run selected from runs/latest/*/run.yaml",
    )


def _resolve_run_id_argument(parser: argparse.ArgumentParser, args: argparse.Namespace) -> str:
    if getattr(args, "run_id", None):
        return str(args.run_id)
    if getattr(args, "latest", False):
        try:
            return resolve_latest_run_id(root_dir=Path(args.root))
        except ValueError as exc:
            parser.error(str(exc))
    parser.error(f"{args.command} requires either --run-id <id> or --latest")
    return ""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="factory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status", help="Show current repo-local system status")
    status_parser.add_argument("--root", default=".", help="Repository root path")

    bootstrap_parser = subparsers.add_parser("bootstrap-run", help="Create baseline run artifacts")
    bootstrap_parser.add_argument("--root", default=".", help="Repository root path")
    bootstrap_parser.add_argument("--run-id", default=_default_run_id())
    bootstrap_parser.add_argument("--work-item-id", default="WI-000")
    bootstrap_parser.add_argument("--work-item-title", default="bootstrap-run")
    bootstrap_parser.add_argument("--pr-id", default="PR-000")

    record_review_parser = subparsers.add_parser("record-review", help="Record review result")
    record_review_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(record_review_parser)
    record_review_parser.add_argument("--status", choices=["pass", "fail"], required=True)
    record_review_parser.add_argument("--summary", required=True)

    record_verification_parser = subparsers.add_parser("record-verification", help="Record verification checks result")
    record_verification_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(record_verification_parser)
    record_verification_parser.add_argument("--lint", choices=["pass", "fail", "pending"], required=True)
    record_verification_parser.add_argument("--tests", choices=["pass", "fail", "pending"], required=True)
    record_verification_parser.add_argument("--type-check", choices=["pass", "fail", "pending"], required=True)
    record_verification_parser.add_argument("--build", choices=["pass", "fail", "pending"], required=True)
    record_verification_parser.add_argument("--summary", required=True)

    record_qa_parser = subparsers.add_parser("record-qa", help="Record QA result")
    record_qa_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(record_qa_parser)
    record_qa_parser.add_argument("--status", choices=["pass", "fail"], required=True)
    record_qa_parser.add_argument("--summary", required=True)

    record_docs_sync_parser = subparsers.add_parser("record-docs-sync", help="Record docs sync result")
    record_docs_sync_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(record_docs_sync_parser)
    record_docs_sync_parser.add_argument("--status", choices=["complete", "required", "not-needed"], required=True)
    record_docs_sync_parser.add_argument("--summary", required=True)

    gate_check_parser = subparsers.add_parser("gate-check", help="Evaluate gate status")
    gate_check_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(gate_check_parser)

    build_approval_parser = subparsers.add_parser("build-approval", help="Build evidence and approval request")
    build_approval_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(build_approval_parser)

    create_goal_parser = subparsers.add_parser("create-goal", help="Create a goal intake artifact")
    create_goal_parser.add_argument("--root", default=".", help="Repository root path")
    create_goal_parser.add_argument("--goal-id", required=True)
    create_goal_parser.add_argument("--title", required=True)
    create_goal_parser.add_argument("--problem", required=True)
    create_goal_parser.add_argument("--outcome", required=True)
    create_goal_parser.add_argument("--constraints")

    create_clarification_parser = subparsers.add_parser(
        "create-clarification",
        help="Create a clarification artifact for a goal",
    )
    create_clarification_parser.add_argument("--root", default=".", help="Repository root path")
    create_clarification_parser.add_argument("--goal-id", required=True)
    create_clarification_parser.add_argument("--clarification-id", required=True)
    create_clarification_parser.add_argument("--title", required=True)
    create_clarification_parser.add_argument("--category", required=True)
    create_clarification_parser.add_argument("--question", required=True)
    create_clarification_parser.add_argument("--escalation", action="store_true")

    resolve_clarification_parser = subparsers.add_parser(
        "resolve-clarification",
        help="Resolve an open clarification artifact for a goal",
    )
    resolve_clarification_parser.add_argument("--root", default=".", help="Repository root path")
    resolve_clarification_parser.add_argument("--goal-id", required=True)
    resolve_clarification_parser.add_argument("--clarification-id", required=True)
    resolve_clarification_parser.add_argument("--decision", choices=["resolved", "deferred", "escalated"], required=True)
    resolve_clarification_parser.add_argument("--resolution-notes", required=True)
    resolve_clarification_parser.add_argument("--next-action", required=True)
    resolve_clarification_parser.add_argument("--suggested-resolution")

    create_work_item_parser = subparsers.add_parser("create-work-item", help="Create a work item artifact")
    create_work_item_parser.add_argument("--root", default=".", help="Repository root path")
    create_work_item_parser.add_argument("--work-item-id", required=True)
    create_work_item_parser.add_argument("--title", required=True)
    create_work_item_parser.add_argument("--goal-id", required=True)
    create_work_item_parser.add_argument("--description", required=True)
    create_work_item_parser.add_argument("--acceptance-criteria")
    create_work_item_parser.add_argument(
        "--clarification-id",
        action="append",
        dest="clarification_ids",
        help="Link one or more clarification artifacts under the same goal",
    )

    create_pr_plan_parser = subparsers.add_parser("create-pr-plan", help="Create the single active PR plan artifact")
    create_pr_plan_parser.add_argument("--root", default=".", help="Repository root path")
    create_pr_plan_parser.add_argument("--pr-id", required=True)
    create_pr_plan_parser.add_argument("--work-item-id", required=True)
    create_pr_plan_parser.add_argument("--title", required=True)
    create_pr_plan_parser.add_argument("--summary", required=True)

    activate_pr_parser = subparsers.add_parser("activate-pr", help="Switch the single active PR plan")
    activate_pr_parser.add_argument("--root", default=".", help="Repository root path")
    activate_pr_parser.add_argument("--pr-id", required=True)

    start_execution_parser = subparsers.add_parser(
        "start-execution",
        help="Start a run from the single active PR plan",
    )
    start_execution_parser.add_argument("--root", default=".", help="Repository root path")
    start_execution_parser.add_argument("--run-id", default=_default_run_id())

    resolve_approval_parser = subparsers.add_parser("resolve-approval", help="Resolve pending approval request")
    resolve_approval_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(resolve_approval_parser)
    resolve_approval_parser.add_argument("--decision", choices=["approve", "reject", "exception"], required=True)
    resolve_approval_parser.add_argument("--actor", required=True)
    resolve_approval_parser.add_argument("--note", required=True)

    cleanup_parser = subparsers.add_parser(
        "cleanup-rehearsal",
        help="List or remove rehearsal artifacts from repo-local operating paths",
    )
    cleanup_parser.add_argument("--root", default=".", help="Repository root path")
    cleanup_parser.add_argument("--apply", action="store_true", help="Actually delete matched artifacts")
    cleanup_parser.add_argument(
        "--include-demo",
        action="store_true",
        help="Include legacy DEMO artifacts in addition to rehearsal artifacts",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "status":
        print(_render_status(get_factory_status(root_dir=Path(args.root))))
        return 0

    if args.command == "bootstrap-run":
        run_root = bootstrap_run(
            root_dir=Path(args.root),
            run_id=args.run_id,
            work_item_id=args.work_item_id,
            work_item_title=args.work_item_title,
            pr_id=args.pr_id,
        )
        print(run_root.as_posix())
        return 0

    if args.command == "record-review":
        run_id = _resolve_run_id_argument(parser, args)
        path = record_review(
            root_dir=Path(args.root),
            run_id=run_id,
            status=args.status,
            summary=args.summary,
        )
        print(path.as_posix())
        return 0

    if args.command == "record-verification":
        run_id = _resolve_run_id_argument(parser, args)
        path = record_verification(
            root_dir=Path(args.root),
            run_id=run_id,
            lint=args.lint,
            tests=args.tests,
            type_check=args.type_check,
            build=args.build,
            summary=args.summary,
        )
        print(path.as_posix())
        return 0

    if args.command == "record-qa":
        run_id = _resolve_run_id_argument(parser, args)
        path = record_qa(
            root_dir=Path(args.root),
            run_id=run_id,
            status=args.status,
            summary=args.summary,
        )
        print(path.as_posix())
        return 0

    if args.command == "record-docs-sync":
        run_id = _resolve_run_id_argument(parser, args)
        path = record_docs_sync(
            root_dir=Path(args.root),
            run_id=run_id,
            status=args.status,
            summary=args.summary,
        )
        print(path.as_posix())
        return 0

    if args.command == "gate-check":
        run_id = _resolve_run_id_argument(parser, args)
        path = evaluate_gates(root_dir=Path(args.root), run_id=run_id)
        print(path.as_posix())
        return 0

    if args.command == "build-approval":
        run_id = _resolve_run_id_argument(parser, args)
        approval_path, queue_path = build_approval_request(root_dir=Path(args.root), run_id=run_id)
        print(approval_path.as_posix())
        if queue_path is not None:
            print(queue_path.as_posix())
        return 0

    if args.command == "create-goal":
        try:
            path = create_goal(
                root_dir=Path(args.root),
                goal_id=args.goal_id,
                title=args.title,
                problem=args.problem,
                outcome=args.outcome,
                constraints=args.constraints,
            )
        except FileExistsError as exc:
            parser.error(str(exc))
        print(path.as_posix())
        return 0

    if args.command == "create-clarification":
        try:
            path = create_clarification(
                root_dir=Path(args.root),
                goal_id=args.goal_id,
                clarification_id=args.clarification_id,
                title=args.title,
                category=args.category,
                question=args.question,
                escalation=args.escalation,
            )
        except (FileExistsError, ValueError) as exc:
            parser.error(str(exc))
        print(path.as_posix())
        return 0

    if args.command == "resolve-clarification":
        try:
            path = resolve_clarification(
                root_dir=Path(args.root),
                goal_id=args.goal_id,
                clarification_id=args.clarification_id,
                decision=args.decision,
                resolution_notes=args.resolution_notes,
                next_action=args.next_action,
                suggested_resolution=args.suggested_resolution,
            )
        except (FileNotFoundError, ValueError) as exc:
            parser.error(str(exc))
        print(path.as_posix())
        return 0

    if args.command == "create-work-item":
        try:
            path = create_work_item(
                root_dir=Path(args.root),
                work_item_id=args.work_item_id,
                title=args.title,
                goal_id=args.goal_id,
                description=args.description,
                acceptance_criteria=args.acceptance_criteria,
                clarification_ids=args.clarification_ids,
            )
        except (FileExistsError, FileNotFoundError, ValueError) as exc:
            parser.error(str(exc))
        print(path.as_posix())
        return 0

    if args.command == "create-pr-plan":
        root_dir = Path(args.root)
        had_active_pr = any((root_dir / "prs" / "active").glob("*.md"))
        try:
            path = create_pr_plan(
                root_dir=root_dir,
                pr_id=args.pr_id,
                work_item_id=args.work_item_id,
                title=args.title,
                summary=args.summary,
            )
        except FileExistsError as exc:
            parser.error(str(exc))
        print(_render_create_pr_plan_summary(path, had_active_pr, args.pr_id))
        return 0

    if args.command == "activate-pr":
        root_dir = Path(args.root)
        active_dir = root_dir / "prs" / "active"
        archive_dir = root_dir / "prs" / "archive"
        prior_active_paths = sorted(path for path in active_dir.glob("*.md") if path.name != f"{args.pr_id}.md")
        try:
            path = activate_pr(root_dir=root_dir, pr_id=args.pr_id)
        except (FileNotFoundError, ValueError) as exc:
            parser.error(str(exc))
        archived_paths = [archive_dir / path.name for path in prior_active_paths if (archive_dir / path.name).exists()]
        print(_render_activate_pr_summary(args.pr_id, path, archived_paths))
        return 0

    if args.command == "start-execution":
        root_dir = Path(args.root)
        try:
            run_root = start_execution(root_dir=root_dir, run_id=args.run_id)
        except ValueError as exc:
            parser.error(_render_start_execution_error(root_dir, args.run_id))
        print(run_root.as_posix())
        return 0

    if args.command == "resolve-approval":
        run_id = _resolve_run_id_argument(parser, args)
        decision_path, queue_path = resolve_approval(
            root_dir=Path(args.root),
            run_id=run_id,
            decision=args.decision,
            actor=args.actor,
            note=args.note,
        )
        print(decision_path.as_posix())
        print(queue_path.as_posix())
        return 0

    if args.command == "cleanup-rehearsal":
        result = cleanup_rehearsal_artifacts(
            root_dir=Path(args.root),
            apply=args.apply,
            include_demo=args.include_demo,
        )
        print(_render_cleanup_summary(result))
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
