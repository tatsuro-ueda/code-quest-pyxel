from __future__ import annotations

"""source_trace_refs の coverage を source document ごとに集計する。"""

import argparse
import json
import re
from pathlib import Path
from typing import Any

from . import check_stakeholder_voices


ROOT = Path(__file__).resolve().parents[2]
TRACKED_TRACE_STATUSES = {"active", "later", "wont"}


def _error(kind: str, **payload: Any) -> dict[str, Any]:
    data = {"kind": kind}
    data.update(payload)
    return data


def _iter_tracked_source_trace_refs(data: dict[str, Any]) -> list[dict[str, str]]:
    trace_refs: list[dict[str, str]] = []
    for section_name in ("requests", "requirements", "acceptance"):
        for item in data["facts"][section_name]:
            if item.get("status", "active") not in TRACKED_TRACE_STATUSES:
                continue
            for trace_ref in item.get("source_trace_refs", []):
                trace_refs.append(
                    {
                        "section": section_name,
                        "item_id": item["id"],
                        "trace_ref": trace_ref,
                    }
                )
    return trace_refs


def _collect_referenced_refs(data: dict[str, Any]) -> tuple[dict[str, set[str]], list[dict[str, Any]]]:
    source_documents = {
        source_document["id"]: source_document for source_document in data["facts"]["source_documents"]
    }
    referenced_refs: dict[str, set[str]] = {}
    errors: list[dict[str, Any]] = []

    for usage in _iter_tracked_source_trace_refs(data):
        trace_ref = usage["trace_ref"]
        if not isinstance(trace_ref, str) or ":" not in trace_ref:
            errors.append(_error("invalid_trace_ref_format", **usage))
            continue
        doc_id, stable_ref = trace_ref.split(":", 1)
        if not doc_id or not stable_ref:
            errors.append(_error("invalid_trace_ref_format", **usage))
            continue
        if doc_id not in source_documents:
            errors.append(_error("unknown_doc_id", doc_id=doc_id, stable_ref=stable_ref, **usage))
            continue
        referenced_refs.setdefault(doc_id, set()).add(stable_ref)

    return referenced_refs, errors


def extract_stable_refs(
    repo_root: Path,
    source_document: dict[str, Any],
) -> tuple[set[str], list[dict[str, Any]]]:
    doc_id = source_document["id"]
    doc_path = repo_root / source_document["path"]
    if not doc_path.exists():
        return set(), [_error("missing_source_document_path", doc_id=doc_id, path=source_document["path"])]

    extraction = source_document.get("extraction")
    if not isinstance(extraction, dict):
        return set(), [
            _error(
                "invalid_extraction_contract",
                doc_id=doc_id,
                path=source_document["path"],
                reason="missing extraction dict",
            )
        ]

    regex_patterns = extraction.get("regex", [])
    literal_refs = extraction.get("literals", [])
    if not isinstance(regex_patterns, list) or not isinstance(literal_refs, list):
        return set(), [
            _error(
                "invalid_extraction_contract",
                doc_id=doc_id,
                path=source_document["path"],
                reason="regex and literals must be lists",
            )
        ]
    if not regex_patterns and not literal_refs:
        return set(), [
            _error(
                "invalid_extraction_contract",
                doc_id=doc_id,
                path=source_document["path"],
                reason="at least one regex or literal is required",
            )
        ]

    text = doc_path.read_text(encoding="utf-8")
    extracted_refs: set[str] = set()
    errors: list[dict[str, Any]] = []

    for pattern in regex_patterns:
        if not isinstance(pattern, str) or not pattern.strip():
            errors.append(
                _error(
                    "invalid_regex_pattern",
                    doc_id=doc_id,
                    path=source_document["path"],
                    pattern=pattern,
                )
            )
            continue
        try:
            compiled = re.compile(pattern)
        except re.error as exc:
            errors.append(
                _error(
                    "invalid_regex_pattern",
                    doc_id=doc_id,
                    path=source_document["path"],
                    pattern=pattern,
                    reason=str(exc),
                )
            )
            continue
        extracted_refs.update(match.group(0) for match in compiled.finditer(text))

    for literal in literal_refs:
        if not isinstance(literal, str) or not literal.strip():
            errors.append(
                _error(
                    "invalid_literal_ref",
                    doc_id=doc_id,
                    path=source_document["path"],
                    literal=literal,
                )
            )
            continue
        if literal not in text:
            errors.append(
                _error(
                    "missing_literal_in_source_document",
                    doc_id=doc_id,
                    path=source_document["path"],
                    literal=literal,
                )
            )
            continue
        extracted_refs.add(literal)

    if not extracted_refs:
        errors.append(
            _error(
                "no_refs_extracted",
                doc_id=doc_id,
                path=source_document["path"],
            )
        )

    return extracted_refs, errors


def build_report(repo_root: Path, rules_path: Path) -> dict[str, Any]:
    data = check_stakeholder_voices.load_rules(rules_path)
    referenced_refs, errors = _collect_referenced_refs(data)

    documents: list[dict[str, Any]] = []
    broken_documents = 0
    for source_document in data["facts"]["source_documents"]:
        doc_id = source_document["id"]
        extracted_refs, extraction_errors = extract_stable_refs(repo_root, source_document)
        doc_errors = list(extraction_errors)
        referenced = sorted(referenced_refs.get(doc_id, set()))
        unexpected_referenced = sorted(ref for ref in referenced if ref not in extracted_refs)
        if unexpected_referenced:
            doc_errors.append(
                _error(
                    "referenced_ref_missing_from_source_document",
                    doc_id=doc_id,
                    path=source_document["path"],
                    refs=unexpected_referenced,
                )
            )
        missing_refs = sorted(ref for ref in extracted_refs if ref not in set(referenced))
        status = "broken" if doc_errors else "ok"
        if doc_errors:
            broken_documents += 1
            errors.extend(doc_errors)
        documents.append(
            {
                "doc_id": doc_id,
                "path": source_document["path"],
                "status": status,
                "total_refs": len(extracted_refs),
                "extracted_refs": sorted(extracted_refs),
                "referenced_refs": referenced,
                "missing_refs": missing_refs,
                "unexpected_referenced_refs": unexpected_referenced,
            }
        )

    summary = {
        "total_documents": len(documents),
        "broken_documents": broken_documents,
        "total_extracted_refs": sum(document["total_refs"] for document in documents),
        "total_referenced_refs": sum(len(document["referenced_refs"]) for document in documents),
        "total_missing_refs": sum(len(document["missing_refs"]) for document in documents),
    }
    return {
        "status": "BROKEN_TRACEABILITY" if errors else "OK",
        "summary": summary,
        "documents": documents,
        "errors": errors,
    }


def run_report(repo_root: Path, rules_path: Path) -> dict[str, Any]:
    return build_report(repo_root, rules_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="stakeholder voices source-trace coverage")
    parser.add_argument("--rules-path", type=Path, default=ROOT / "docs" / "stakeholder_voices.yml")
    args = parser.parse_args(argv)

    payload = run_report(ROOT, args.rules_path)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
