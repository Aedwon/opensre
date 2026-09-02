"""Evidence mapper for Lambda function inspection."""

from __future__ import annotations

from typing import Any

from core.domain.types.evidence import record_evidence_entry, unique_evidence_source


def map_inspect_lambda_function(
    evidence: dict[str, Any], output: dict[str, Any], tool_input: dict[str, Any]
) -> None:
    """Cite safe Lambda configuration metadata from a successful inspection."""
    if output.get("error") or output.get("found") is not True:
        return

    function_name = output.get("function_name") or tool_input.get("function_name")
    parts: list[str] = []

    runtime = output.get("runtime")
    if runtime:
        parts.append(f"runtime {runtime}")

    state = output.get("state")
    if state:
        parts.append(f"state {state}")

    memory_size = output.get("memory_size")
    if memory_size is not None:
        parts.append(f"{memory_size} MB")

    timeout = output.get("timeout")
    if timeout is not None:
        parts.append(f"{timeout}s timeout")

    code = output.get("code")
    if isinstance(code, dict):
        file_count = code.get("file_count")
        if isinstance(file_count, int) and not isinstance(file_count, bool) and file_count >= 0:
            file_label = "code file" if file_count == 1 else "code files"
            parts.append(f"{file_count} {file_label}")

    name = str(function_name).strip() if function_name else ""
    if parts:
        summary = f"{name}: {', '.join(parts)}" if name else ", ".join(parts)
    else:
        summary = f"{name}: configuration inspected" if name else "configuration inspected"

    record_evidence_entry(
        evidence,
        source=unique_evidence_source(evidence, "inspect_lambda_function"),
        label="Lambda Function",
        summary=summary,
    )
