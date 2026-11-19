# Source integrity and accessibility audit runbook

This project intentionally distinguishes **metadata completeness**, **network reachability**, **evidence validity** and **human accessibility testing**. Passing one does not establish the others.

## 1. Offline checks on each build

From the repository root, with Python 3.12 or later:

```sh
python scripts/audit_sources.py
python generate.py
python scripts/audit_accessibility.py
python scripts/validate.py
```

The curated `sources.json` registry has institutionally attributed sources with stable IDs. Offline validation checks required descriptive fields, dates and public URL syntax. The public `source-integrity-index.json` is labelled `offline-metadata-only` with every URL **not-probed**. It does not claim live access to an institution or validate a historical claim.

The accessibility script checks representative page types for a document language, visible skip-to-content path, main landmark, document heading, image alternative attributes, labelled form controls, named buttons, and navigation/dialog relationships. Full generated-site validation checks navigation, links and fragments; these inspections **do not certify WCAG**.

## 2. Periodic remote source checks

To conduct a limited local test:

```sh
python scripts/audit_sources.py --network --limit 10 --workers 3 --timeout 8 --output .qa/source-health.json
```

For all curated sources:

```sh
python scripts/audit_sources.py --network --workers 4 --timeout 8 --output .qa/source-health.json
```

## Daily archive review and continuous improvement

`.github/workflows/daily-review.yml` runs daily at 22:37 UTC (approximately 09:37 AEDT or 08:37 AEST), or on manual dispatch. It checks the current default branch, runs deterministic source and persecution tests, builds and validates the generated website, and probes a rotating, bounded sample of 12 curated external references. It updates **one rolling GitHub issue** named `Daily Assyria archive review` with the latest counts, source-health observations, results and a rotating shortlist of unmapped persecution records.

GitHub's cron schedule is best-effort, can run late and, for an inactive public repository, may eventually be disabled. The workflow uses the built-in `GITHUB_TOKEN` with only `contents: read` and `issues: write`; no long-lived token or additional paid service is required. Issue updates may be prevented by repository Actions policy; investigate the workflow log before claiming that a report was posted.

Run the report generator locally without HTTP requests:

```sh
python scripts/test_daily_review.py
python scripts/daily_review.py --report .qa/daily-report.json --summary .qa/daily-report.md
```

To include bounded network checking:

```sh
python scripts/daily_review.py --network --report .qa/daily-report.json --summary .qa/daily-report.md
```

A second, separately scheduled ChatGPT task can investigate a worthwhile project improvement and propose a reviewed GitHub pull request. It is not a substitute for this workflow's deterministic checks. Automated HTTP availability must not become an editorial review result; neither routine may invent historical cases, refresh consultation dates, merge unreviewed scholarship or issue arbitrary code patches merely to produce activity. No change to the website is necessary when the current information is sound.

GitHub Actions `.github/workflows/source-audit.yml` supports manual dispatch and a monthly schedule. Its job summary shows categories and candidates for editorial follow-up. Network probes are intentionally **separate from normal PR builds** so intermittent external outages and bot mitigation do not prevent valid site updates.

Response categories:
- `reachable`: automated request returned a successful response without a material URL change, not evidence of content accuracy.
- `redirect-review`: changed final URL; check if a normal canonical redirect or a link in need of revision.
- `missing-review`: HEAD missing responses are rechecked with GET; a 404/410 still needs human verification.
- `restricted-or-rate-limited`: HTTP 401/403/429 can represent access policy or anti-bot protections, not absence.
- `temporary-failure`: server errors and transient HTTP statuses.
- `network-unconfirmed`: timeout, blocked connection, unsafe redirect or other inconclusive transport issue.
- `not-probed`: no remote request happened.

The scope is the maintained **curated primary source registry only**. The 372 preserved reference items and URLs embedded within their full historical snapshots are not remotely audited by this script. Maintain the source's exact ID and verify redirects, edition/revision and licensing before changing a URL. Do not rewrite `checked` to a new date merely because a robot connected to a server. A real editorial investigation should record a specific reference, its role, the evidence and changes in the governance ledger.

## 3. Accessibility and functional reviews still needed

Use W3C WCAG 2.2 as a reference, testing more than the semantic HTML gate. A qualified reviewer should record device, OS, browser version, screen-reader configuration, zoom level, results and evidence for each test.

1. Keyboard-only: desktop and mobile menus; search modal; article save/remove; citation links; Bible verse filters and the historical map (including its time slider, chapter picker, zoom/pan and city selector). Confirm focus is visibly outlined and not hidden behind the sticky header. Escape should close menus and restore a sensible focus position.
2. Screen readers: VoiceOver with Safari on iOS/macOS and at least one desktop reader such as NVDA with Firefox/Edge; meaningful labels, source lists, form errors, search status, map chapter changes and headings.
3. Reflow and contrast: 320 CSS pixel width, 200%-400% zoom, landscape, target sizes, link focus and all colours against their actual rendered backgrounds. Automated labels do not establish adequate contrast.
4. Syriac: verify actual right-to-left shaping, font availability, Unicode names, mixed-direction passage markers and alternatives on desktop/mobile. Language and dialect pronunciation still await qualified speaker review.
5. Motion: reduced-motion preference, atlas timeline play/pause, animated stats and nav disclosure transitions.

Document real findings and follow-ups in the roadmap and a public correction record when a previously published mistake is confirmed and amended. Do not mark any manual scenario passed just because it appears in this checklist.

## 4. Editorial and release gates

The production configuration permits indexing on the canonical public hostname. Publication of new substantive historical claims still requires appropriate source review, rights checks, accessibility testing and an authorised maintainer decision. No private interviews are collected by these scripts; a downloadable contribution draft is not a secure submission.

- Source Library: `/sources/`
- Evidence Register: `/about/evidence/`
- Public audit hub: `/audit/`
- Editorial governance: `/governance/`
- Publication and backup runbook: `docs/PRESERVATION.md`

### Standards

W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/

W3C What is New in WCAG 2.2: https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/

**Operational status:** periodic checks are configured in GitHub Actions, but a configured schedule and an HTTP response are not evidence of completed human source review. No full WCAG 2.2 conformance, screen-reader sign-off or live external-link health certification is claimed.
