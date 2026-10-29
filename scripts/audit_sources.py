"""External source audit. A network probe is not an editorial verification.

Offline mode validates curated metadata and URL structure. Network mode is
explicit, read-only and nonblocking for normal builds. HTTP 403/429, timeout,
robots restrictions and other transient failures are NOT declared broken links.
"""
import argparse
import concurrent.futures
import datetime
import ipaddress
import json
import re
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = ROOT / "sources.json"
USER_AGENT = "Assyria-Living-Archive-SourceAudit/1.0 (link integrity; no scraping)"
STATUSES = {"reachable", "redirect-review", "missing-review", "restricted-or-rate-limited",
            "temporary-failure", "network-unconfirmed", "not-probed"}
FIELDS = ("id", "title", "publisher", "url", "type", "access", "checked")


def _public_host(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or not parsed.hostname:
        return False
    if parsed.username or parsed.password or parsed.fragment or any(c.isspace() for c in url):
        return False
    host = parsed.hostname.lower().strip(".")
    if host in {"localhost"} or host.endswith(".local") or host.endswith(".internal"):
        return False
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return "." in host and len(host) > 3
    return address.is_global


def load_records(path=SOURCE_FILE):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError("Expected a non-empty curated source list")
    ids = set()
    for record in data:
        if not isinstance(record, dict) or any(not isinstance(record.get(f), str) or not record[f].strip() for f in FIELDS):
            raise ValueError("Incomplete source record")
        if not re.fullmatch(r"[a-z][a-z0-9-]*", record["id"]) or record["id"] in ids:
            raise ValueError("Duplicate or invalid source ID: " + record["id"])
        if not _public_host(record["url"]):
            raise ValueError("Invalid or unsafe public source URL: " + record["id"])
        try:
            datetime.date.fromisoformat(record["checked"])
        except ValueError as exc:
            raise ValueError("Invalid recorded consultation date: " + record["id"]) from exc
        ids.add(record["id"])
    return data


class PublicRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not _public_host(newurl):
            raise ValueError("Redirect targets an unsupported or private address")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


OPENER = urllib.request.build_opener(PublicRedirect)


def _request(url, method, timeout):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                                    "Accept": "text/html,application/json,*/*;q=0.2"},
                                     method=method)
    try:
        with OPENER.open(request, timeout=timeout) as response:
            # Never download the entire remote page.
            response.read(256) if method == "GET" else None
            return response.status, response.url
    except urllib.error.HTTPError as error:
        return error.code, error.geturl()


def classify(status, requested, final):
    if status in (401, 403, 429):
        return "restricted-or-rate-limited"
    if status in (404, 410):
        return "missing-review"
    if status in (408, 425) or 500 <= status <= 599:
        return "temporary-failure"
    if 200 <= status < 400:
        return "redirect-review" if requested.rstrip("/") != final.rstrip("/") else "reachable"
    return "network-unconfirmed"


def probe(record, timeout=8):
    url = record["url"]
    try:
        status, final = _request(url, "HEAD", timeout)
        if status in (400, 404, 405, 410, 501):
            # HEAD can be unsupported or misconfigured. Recheck using GET.
            status, final = _request(url, "GET", timeout)
        kind = classify(status, url, final)
        return {"id": record["id"], "url": url, "status": kind,
                "http_status": status, "final_url": final,
                "note": "Machine link probe only; redirects and unavailable responses need editorial review."}
    except (OSError, ValueError, socket.timeout, urllib.error.URLError) as exc:
        return {"id": record["id"], "url": url, "status": "network-unconfirmed",
                "http_status": None, "final_url": None,
                "note": "Network failure or restricted target; no claim that the published source is missing.",
                "error_class": type(exc).__name__}


def audit(records, network=False, workers=4, timeout=8, limit=None):
    if limit is not None and (type(limit) is not int or limit < 1):
        raise ValueError("Limit must be a positive integer")
    selection = records[:limit] if limit else records
    if network:
        if not 1 <= workers <= 8 or not 1 <= timeout <= 30:
            raise ValueError("Bound external request concurrency and timeout")
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            entries = list(pool.map(lambda item: probe(item, timeout), selection))
    else:
        entries = [{"id": item["id"], "url": item["url"], "status": "not-probed",
                    "http_status": None, "final_url": None,
                    "note": "Metadata passed structural checks; URL not requested."} for item in selection]
    counts = dict(sorted(Counter(x["status"] for x in entries).items()))
    if any(x not in STATUSES for x in counts):
        raise ValueError("Unrecognised external link audit result")
    return {
        "schema_version": 1,
        "mode": "network-probe" if network else "offline-metadata-only",
        "scope": "Curated primary sources in sources.json only; archived Wikipedia snapshot source URLs and embedded references are not remotely probed.",
        "caution": "Network status is not historical verification, publication permission, licence assurance or a guarantee of lasting URL availability. Missing, redirected, blocked and transient responses require human review.",
        "record_count": len(entries), "source_count": len(records), "summary": counts, "results": entries,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--network", action="store_true", help="Explicitly test remote endpoints")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=8)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    records = load_records()
    result = audit(records, network=args.network, workers=args.workers,
                   timeout=args.timeout, limit=args.limit)
    print("Source audit:", result["mode"], "|", result["record_count"], "records |",
          ", ".join(f"{key}: {value}" for key, value in result["summary"].items()))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    # A remote 403, 429, 404 or timeout must not misrepresent the source as false
    # or spuriously break a website release. Curated confirmed issues need review.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
