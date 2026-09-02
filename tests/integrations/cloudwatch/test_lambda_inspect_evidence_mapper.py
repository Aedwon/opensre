"""Regression coverage for Lambda inspection evidence mapping."""

from __future__ import annotations

from typing import Any

from core.domain.types.evidence import CATALOG_ENTRIES_KEY
from integrations.aws_lambda.tools.lambda_inspect_tool._evidence import (
    map_inspect_lambda_function,
)
from tools.investigation.stages.gather_evidence.tools import merge_tool_evidence
from tools.registry import get_registered_tool


def test_mapper_records_compact_safe_lambda_metadata() -> None:
    evidence: dict[str, Any] = {}
    output = {
        "found": True,
        "function_name": "orders-worker",
        "function_arn": "arn:aws:lambda:us-east-1:123456789012:function:orders-worker",
        "runtime": "python3.13",
        "handler": "app.handler",
        "timeout": 30,
        "memory_size": 512,
        "state": "Active",
        "environment_variables": {"DATABASE_PASSWORD": "do-not-cite"},
        "description": "internal deployment detail",
        "layers": [{"arn": "secret-ish-layer-detail"}],
        "code": {
            "file_count": 2,
            "files": {"app.py": "print('sensitive source')", "config.py": "TOKEN='secret'"},
        },
    }

    map_inspect_lambda_function(evidence, output, {"function_name": "orders-worker"})

    entries = evidence[CATALOG_ENTRIES_KEY]
    assert entries == [
        {
            "source": "inspect_lambda_function",
            "label": "Lambda Function",
            "summary": "orders-worker: runtime python3.13, state Active, 512 MB, 30s timeout, 2 code files",
            "url": None,
            "snippet": None,
        }
    ]
    rendered = repr(entries)
    assert "do-not-cite" not in rendered
    assert "sensitive source" not in rendered
    assert "secret-ish-layer-detail" not in rendered
    assert "123456789012" not in rendered


def test_mapper_records_sparse_configuration_without_code() -> None:
    evidence: dict[str, Any] = {}

    map_inspect_lambda_function(
        evidence,
        {"found": True, "function_name": None},
        {"function_name": "requested-function", "include_code": False},
    )

    entry = evidence[CATALOG_ENTRIES_KEY][0]
    assert entry["source"] == "inspect_lambda_function"
    assert entry["summary"] == "requested-function: configuration inspected"


def test_mapper_skips_failed_inspection() -> None:
    evidence: dict[str, Any] = {}

    map_inspect_lambda_function(
        evidence,
        {"error": "AccessDenied", "function_name": "orders-worker"},
        {"function_name": "orders-worker"},
    )

    assert CATALOG_ENTRIES_KEY not in evidence


def test_registered_tool_carries_lambda_inspect_mapper() -> None:
    tool = get_registered_tool("inspect_lambda_function")

    assert tool is not None
    assert tool.evidence_mapper is not None


def test_merge_path_preserves_raw_output_and_records_evidence() -> None:
    evidence: dict[str, Any] = {}
    output = {
        "found": True,
        "function_name": "orders-worker",
        "runtime": "python3.13",
        "state": "Active",
    }

    merge_tool_evidence(
        evidence,
        "inspect_lambda_function",
        output,
        {"function_name": "orders-worker"},
    )

    assert evidence["inspect_lambda_function"] == output
    entry = evidence[CATALOG_ENTRIES_KEY][0]
    assert entry["source"] == "inspect_lambda_function"
    assert entry["summary"] == "orders-worker: runtime python3.13, state Active"


def test_repeated_merge_calls_keep_independent_citeable_entries() -> None:
    evidence: dict[str, Any] = {}

    merge_tool_evidence(
        evidence,
        "inspect_lambda_function",
        {"found": True, "function_name": "orders-worker", "runtime": "python3.13"},
        {"function_name": "orders-worker"},
    )
    second_output = {
        "found": True,
        "function_name": "billing-worker",
        "runtime": "nodejs22.x",
    }
    merge_tool_evidence(
        evidence,
        "inspect_lambda_function",
        second_output,
        {"function_name": "billing-worker"},
    )

    entries = evidence[CATALOG_ENTRIES_KEY]
    assert [entry["source"] for entry in entries] == [
        "inspect_lambda_function",
        "inspect_lambda_function#2",
    ]
    assert entries[0]["summary"] == "orders-worker: runtime python3.13"
    assert entries[1]["summary"] == "billing-worker: runtime nodejs22.x"
    assert evidence["inspect_lambda_function"] == second_output
