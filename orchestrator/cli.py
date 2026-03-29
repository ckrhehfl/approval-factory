from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from orchestrator.pipeline import (
    activate_pr,
    bootstrap_run,
    build_approval_request,
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
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Latest Run:")
    latest_run = status["latest_run"]
    if isinstance(latest_run, dict):
        lines.append(f"- run_id: {latest_run['run_id']}")
        lines.append(f"- state: {latest_run['state']}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Approval:")
    approval = status["approval"]
    lines.append(f"- status: {approval['status']}")

    open_clarifications = status["open_clarifications"]
    if isinstance(open_clarifications, list) and open_clarifications:
        lines.append("")
        lines.append("Open Clarifications:")
        for clarification_id in open_clarifications:
            lines.append(f"- clarification_id: {clarification_id}")

    return "\n".join(lines)


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
    record_review_parser.add_argument("--run-id", required=True)
    record_review_parser.add_argument("--status", choices=["pass", "fail"], required=True)
    record_review_parser.add_argument("--summary", required=True)

    record_verification_parser = subparsers.add_parser("record-verification", help="Record verification checks result")
    record_verification_parser.add_argument("--root", default=".", help="Repository root path")
    record_verification_parser.add_argument("--run-id", required=True)
    record_verification_parser.add_argument("--lint", choices=["pass", "fail", "pending"], required=True)
    record_verification_parser.add_argument("--tests", choices=["pass", "fail", "pending"], required=True)
    record_verification_parser.add_argument("--type-check", choices=["pass", "fail", "pending"], required=True)
    record_verification_parser.add_argument("--build", choices=["pass", "fail", "pending"], required=True)
    record_verification_parser.add_argument("--summary", required=True)

    record_qa_parser = subparsers.add_parser("record-qa", help="Record QA result")
    record_qa_parser.add_argument("--root", default=".", help="Repository root path")
    record_qa_parser.add_argument("--run-id", required=True)
    record_qa_parser.add_argument("--status", choices=["pass", "fail"], required=True)
    record_qa_parser.add_argument("--summary", required=True)

    record_docs_sync_parser = subparsers.add_parser("record-docs-sync", help="Record docs sync result")
    record_docs_sync_parser.add_argument("--root", default=".", help="Repository root path")
    record_docs_sync_parser.add_argument("--run-id", required=True)
    record_docs_sync_parser.add_argument("--status", choices=["complete", "required", "not-needed"], required=True)
    record_docs_sync_parser.add_argument("--summary", required=True)

    gate_check_parser = subparsers.add_parser("gate-check", help="Evaluate gate status")
    gate_check_parser.add_argument("--root", default=".", help="Repository root path")
    gate_check_parser.add_argument("--run-id", required=True)

    build_approval_parser = subparsers.add_parser("build-approval", help="Build evidence and approval request")
    build_approval_parser.add_argument("--root", default=".", help="Repository root path")
    build_approval_parser.add_argument("--run-id", required=True)

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

    create_work_item_parser = subparsers.add_parser("create-work-item", help="Create a work item artifact")
    create_work_item_parser.add_argument("--root", default=".", help="Repository root path")
    create_work_item_parser.add_argument("--work-item-id", required=True)
    create_work_item_parser.add_argument("--title", required=True)
    create_work_item_parser.add_argument("--goal-id", required=True)
    create_work_item_parser.add_argument("--description", required=True)
    create_work_item_parser.add_argument("--acceptance-criteria")

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
    resolve_approval_parser.add_argument("--run-id", required=True)
    resolve_approval_parser.add_argument("--decision", choices=["approve", "reject", "exception"], required=True)
    resolve_approval_parser.add_argument("--actor", required=True)
    resolve_approval_parser.add_argument("--note", required=True)

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
        path = record_review(
            root_dir=Path(args.root),
            run_id=args.run_id,
            status=args.status,
            summary=args.summary,
        )
        print(path.as_posix())
        return 0

    if args.command == "record-verification":
        path = record_verification(
            root_dir=Path(args.root),
            run_id=args.run_id,
            lint=args.lint,
            tests=args.tests,
            type_check=args.type_check,
            build=args.build,
            summary=args.summary,
        )
        print(path.as_posix())
        return 0

    if args.command == "record-qa":
        path = record_qa(
            root_dir=Path(args.root),
            run_id=args.run_id,
            status=args.status,
            summary=args.summary,
        )
        print(path.as_posix())
        return 0

    if args.command == "record-docs-sync":
        path = record_docs_sync(
            root_dir=Path(args.root),
            run_id=args.run_id,
            status=args.status,
            summary=args.summary,
        )
        print(path.as_posix())
        return 0

    if args.command == "gate-check":
        path = evaluate_gates(root_dir=Path(args.root), run_id=args.run_id)
        print(path.as_posix())
        return 0

    if args.command == "build-approval":
        approval_path, queue_path = build_approval_request(root_dir=Path(args.root), run_id=args.run_id)
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

    if args.command == "create-work-item":
        try:
            path = create_work_item(
                root_dir=Path(args.root),
                work_item_id=args.work_item_id,
                title=args.title,
                goal_id=args.goal_id,
                description=args.description,
                acceptance_criteria=args.acceptance_criteria,
            )
        except FileExistsError as exc:
            parser.error(str(exc))
        print(path.as_posix())
        return 0

    if args.command == "create-pr-plan":
        try:
            path = create_pr_plan(
                root_dir=Path(args.root),
                pr_id=args.pr_id,
                work_item_id=args.work_item_id,
                title=args.title,
                summary=args.summary,
            )
        except FileExistsError as exc:
            parser.error(str(exc))
        print(path.as_posix())
        return 0

    if args.command == "activate-pr":
        try:
            path = activate_pr(root_dir=Path(args.root), pr_id=args.pr_id)
        except (FileNotFoundError, ValueError) as exc:
            parser.error(str(exc))
        print(path.as_posix())
        return 0

    if args.command == "start-execution":
        try:
            run_root = start_execution(root_dir=Path(args.root), run_id=args.run_id)
        except ValueError as exc:
            parser.error(str(exc))
        print(run_root.as_posix())
        return 0

    if args.command == "resolve-approval":
        decision_path, queue_path = resolve_approval(
            root_dir=Path(args.root),
            run_id=args.run_id,
            decision=args.decision,
            actor=args.actor,
            note=args.note,
        )
        print(decision_path.as_posix())
        print(queue_path.as_posix())
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
