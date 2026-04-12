from __future__ import annotations


INITIAL_PHASE = "initialized"

_PHASE_DISPLAY = {
    INITIAL_PHASE: "Initialized",
}


def initial_pr_loop_phase() -> str:
    return INITIAL_PHASE


def validate_pr_loop_phase(phase: object) -> str:
    if not isinstance(phase, str) or phase not in _PHASE_DISPLAY:
        raise ValueError("pr-loop state phase must be one of: initialized")
    return phase


def display_pr_loop_phase(phase: object) -> str:
    return _PHASE_DISPLAY.get(validate_pr_loop_phase(phase), "Unknown")
