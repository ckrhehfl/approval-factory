from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    work_item_id: str
    pr_id: str
    state: str
    created_at: str

    @classmethod
    def new(cls, run_id: str, work_item_id: str, pr_id: str, state: str) -> "RunRecord":
        created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        return cls(
            run_id=run_id,
            work_item_id=work_item_id,
            pr_id=pr_id,
            state=state,
            created_at=created_at,
        )

    def as_payload(self) -> dict:
        return {"run": asdict(self)}
