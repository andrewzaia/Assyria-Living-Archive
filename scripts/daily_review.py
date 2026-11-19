"""Daily archive health snapshot and bounded source triage.

Produces a factual, read-only maintenance report. It does not approve claims,
change source consultation dates or publish historical material.
"""
import argparse
import datetime as dt
import json
from collections import Counter
from pathlib import Path
from zoneinfo import ZoneInfo

from audit_sources import audit, load_records

ROOT = Path(__file__).resolve().parents[1]
SYDNEY = ZoneInfo("Australia/Sydney")
FIRST_DAY = dt.date(2020, 1, 1)
DASHES = dict.fromkeys(map(ord, "\u2010\u2011\u2012\u2013\u2014\u2015\u2212"), "-")


def plain(value):
    """Keep reports using the project's ASCII dash convention."""
    return str(value).translate(DASHES).replace("\n", " ").strip()


def read_json(root, relative):
    return json.loads((root / relative).read_text(encoding="utf-8"))


def rotate(items, when, amount):
    """Deterministically rotate across the full source list without repeats."""
    if amount < 1:
        raise ValueError("Sample size must be positive")
    if not items:
        return []
    count = min(amount, len(items))
    start = max(0, (when - FIRST_DAY).days) * count % len(items)
    return [items[(start + n) % len(items)] for n in range(count)]


def snapshot(root, when, sample=12, network=False):
    catalogue = read_json(root, "static/persecution-records.json")
    registry = read_json(root, "data/persecution-source-audit.json")
    roadmap = read_json(root, "data/project-roadmap.json")
    records = catalogue["records"]
    register = registry["sources"]
    ids = [record["id"] for record in records]
    by_id = {record["id"]: record for record in records}
    issues = []

    if len(ids) != len(by_id):
        issues.append("Duplicate catalogue record IDs")
    if not records:
        issues.append("Catalogue has no records")

    referenced = set()
    for source in register:
        if not source.get("url") or not source.get("captured_record_ids"):
            issues.append("Incomplete source audit row")
            continue
        for record_id in source["captured_record_ids"]:
            referenced.add(record_id)
            record = by_id.get(record_id)
            if record is None:
                issues.append("Audit references unknown record " + plain(record_id))
            elif not any(item.get("url") == source["url"] for item in record.get("sources", [])):
                issues.append("Source URL mismatch for " + plain(record_id))

    for record in records:
        if not record.get("sources") or not record.get("summary"):
            issues.append("Incomplete catalogue entry " + plain(record["id"]))
        for related in record.get("related_ids", []):
            if related not in by_id or related == record["id"]:
                issues.append("Invalid related record from " + plain(record["id"]))

    research_gaps = sorted((record for record in records if record["id"] not in referenced),
                           key=lambda record: int(record["id"].split("-")[-1]))
    roadmap_item = next((item for item in roadmap["milestones"]
                         if item["id"] == "assyrian-persecution"), None)
    if roadmap_item is None:
        issues.append("Persecution milestone missing from roadmap")
    elif str(len(records)) not in roadmap_item.get("delivered", ""):
        issues.append("Roadmap persecution count differs from catalogue")

    selections = rotate(research_gaps, when, 3)
    sources = load_records(root / "sources.json")
    sampled = rotate(sources, when, sample)
    probe_result = audit(sampled, network=network, workers=3, timeout=7)

    return {
        "schema_version": 1,
        "date": when.isoformat(),
        "timezone": "Australia/Sydney",
        "catalogue_records": len(records),
        "catalogue_countries": len({record["country"] for record in records}),
        "catalogue_media": sum(bool(record.get("media")) for record in records),
        "source_audit_publications": len(register),
        "curated_sources": len(sources),
        "outstanding_source_triage": len(research_gaps),
        "priority_cases": [{"id": record["id"], "title": plain(record["title"])}
                           for record in selections],
        "roadmap_in_progress": [plain(item["title"]) for item in roadmap["milestones"]
                                if item["status"] == "in-progress"],
        "source_health": probe_result,
        "diagnostics": sorted(set(issues)),
    }


def markdown(report, validation="unknown", run_url=""):
    output = [
        "# Assyria Living Archive - Daily review",
        "",
        "**Local date:** " + report["date"] + " (Australia/Sydney)",
        "**Repository validation:** " + plain(validation),
        "**Workflow:** " + (run_url if run_url.startswith("https://github.com/") else "Not supplied"),
        "",
        "## Catalogue and evidence coverage",
        "",
        "- Assyrian persecution records: " + str(report["catalogue_records"]),
        "- Countries represented: " + str(report["catalogue_countries"]),
        "- Records with locally referenced media: " + str(report["catalogue_media"]),
        "- Publications in persecution source-audit register: " + str(report["source_audit_publications"]),
        "- Curated encyclopedia sources: " + str(report["curated_sources"]),
        "- Records without source-triage mapping: " + str(report["outstanding_source_triage"]),
        "",
        "## Suggested source verification",
        "",
        "Research queue entries are **not marked reviewed** by this workflow."
    ]
    if report["priority_cases"]:
        for item in report["priority_cases"]:
            output.append("- " + item["id"] + ": " + item["title"])
    else:
        output.append("- No unmapped catalogue records; review historical claims or other roadmap tasks.")

    health = report["source_health"]
    output.extend([
        "",
        "## Bounded external source link check",
        "",
        "Checked " + str(health["record_count"]) + " URLs, rotating daily through the curated list.",
        "An HTTP response is **not** historical verification or a licence check.",
        ""
    ])
    for status, count in sorted(health["summary"].items()):
        output.append("- " + plain(status) + ": " + str(count))
    follow_up = [entry for entry in health["results"]
                 if entry["status"] not in ("reachable", "not-probed")]
    if follow_up:
        output.extend(["", "Items to inspect manually (network responses are inconclusive):", ""])
        for entry in follow_up[:20]:
            output.append("- " + plain(entry["id"]) + ": " + plain(entry["status"]) +
                          " (HTTP " + str(entry.get("http_status") or "unknown") + ")")
    output.extend(["", "## Structural findings", ""])
    if report["diagnostics"]:
        output.extend("- " + plain(issue) for issue in report["diagnostics"])
    else:
        output.append("- No structural discrepancy detected by the daily snapshot.")
    output.extend([
        "",
        "## Release controls",
        "",
        "This routine does not change the website, rewrite source links, reset consultation dates,",
        "mark historical claims verified, or merge pull requests. New editorial material and",
        "code changes require supported evidence, passing tests and review. A daily ChatGPT",
        "improvement task separately prepares focused proposals where appropriate.",
        ""
    ])
    return "\n".join(output)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=dt.date.fromisoformat,
                        default=dt.datetime.now(SYDNEY).date())
    parser.add_argument("--sample-size", type=int, default=12)
    parser.add_argument("--network", action="store_true")
    parser.add_argument("--validation", default="unknown")
    parser.add_argument("--run-url", default="")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args(argv)
    result = snapshot(ROOT, args.date, args.sample_size, args.network)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    args.summary.write_text(markdown(result, validation=args.validation,
                                     run_url=args.run_url), encoding="utf-8")
    print("Daily snapshot:", len(result["priority_cases"]), "research leads;",
          result["outstanding_source_triage"], "unmapped records;",
          len(result["diagnostics"]), "structural findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
