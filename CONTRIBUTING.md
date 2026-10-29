# Contributing

The foundation edition is a starting point for deeper, reviewed coverage. Contributions should make it easier for another reader to check a claim and understand its limits.

## Articles

Articles are defined using `add(...)` calls in `content.py`:

```python
add(
    'unique-article-slug',
    'Article title',
    'History & archaeology',
    'A concise original summary.',
    [('Section title', 'Original paragraph with a clear evidence basis.')],
    ['existing-source-id'],
    ['related-article-slug'],
)
```

Choose one of the six existing categories. Every source ID must exist in `sources.json`; every related slug must identify an existing article. Optional `image` and `note` fields are supported. If adding an image key, update the generator's alternative-text and credit functions too.

Source records use `id`, `title`, `publisher`, `url`, `type`, `access` and `checked`. Use stable institutional or publication URLs where possible. Record the actual consultation date; do not update it merely because a build ran.

Published editorial guides have article-level bibliographies and selected curated section-level source trails. The evidence register at `/about/evidence/` also presents an initial claim-level verification queue. None of these links alone establishes historical truth. Do not describe an unreviewed source as peer reviewed or a consultation date as independent validation. If substantively updating an entry, check its section trail, any anchored claim-review records and their limitations. Claim reviews require exact source roles, passages and named specialist review before a completed-review label can be used.

## Evidence and identity

- Distinguish primary records, scholarly interpretation, oral testimony, community advocacy and institutional self-description.
- Respect individual and institutional self-designations. Language, ethnicity and church membership are distinct categories.
- Separate ancient Akkadian, Aramaic, Classical Syriac and living Neo-Aramaic varieties accurately.
- Give contested claims named sources and acknowledge important alternative interpretations.
- Avoid unsupported population totals, casualty totals and claims of unchanged practices across millennia.
- Mark personal recollections as testimony. Check consent before publishing interviews, family details or contributed photographs.
- Use original summaries and check reuse rights for every imported asset.

## Oral histories and community heritage

Use the public `/heritage/` hub only for original summaries and linked material already published by the original custodians. Every entry in `data/heritage-records.json` requires a traceable source, a clear source role, an original guide route and an explicit external-reference-only rights status. Do not commit contributed interviews, photographs, signed consent forms, family contacts, recordings, transcripts or unapproved biographical material to GitHub.

The downloadable `archive/heritage/` files are original **blank planning aids**, not consent agreements, legal releases or upload endpoints. Consent to record, private preservation, research access, public quotation, reproduction and commercial or machine-learning reuse must be considered separately. Narrators and appropriate rights holders should know the intended custody, restrictions, review/correction opportunities and realistic withdrawal limits before recording or publication. Sensitive details of third parties and children need further safeguards. Informed consent and custodial approval cannot be inferred from a publicly accessible recording.

The current project **has no operational intake or media archive**, and the existing contribution form only creates a local draft. Do not solicit private material as if it will be reviewed or securely stored until a separately approved system and accountable editorial team exist. For method, consult Oral History Australia and the National Library of Australia rights guidance in `sources.json`.

## Editorial governance and revision provenance

`/governance/` is the public corrections policy and curated release ledger. Before a significant change, inspect claim-level anchors, section citations, Scripture or inscriptions, reuse rights and the project roadmap. A substantive correction or withdrawal needs an explicit public notice only after it is investigated and the evidence and editorial action can be stated responsibly. Keep unadjudicated private reports and sensitive material out of public data.

- Significant public releases should be appended to `data/editorial-revisions.json` using a `REV-...` identifier, affected pages and files, the **actual merged Git commit SHA**, pull request number, nature of the change and unresolved limitations. It is a curated log, not a substitute for the full Git history.
- Documented corrections require a `COR-...` notice linked to a merged revision and affected article, describing the old issue, action, date and evidence. Do not invent error reports or label unresolved private questions as completed corrections.
- A passing CI build is **automated-validation-only**. Independent approval requires an actual reviewer, scope, assessment note, review date and authorised attribution; a citation, external publication or internal code check is not that approval.
- Keep unappointed roles visibly **unassigned**. Never describe secure submission, signed consent storage, specialist staffing or response times as active before their systems and responsible people exist.
- Blank worksheets in `archive/governance/` are local planning aids, not a private intake system. Do not put sensitive reports, contact details or signed permissions into Git.

## Preservation and publication approvals

Build output from `python generate.py` includes a `preservation-manifest.json` checksum inventory. Verify it with `python scripts/validate.py` before release; export a checked recovery ZIP with `python scripts/export_archive.py --output ../assyria-site-backup.zip`. Do not edit a generated file after the manifest has been recorded. A manifest mismatch is a failure requiring investigation, not a reason to silently rewrite baseline hashes.

The public `/stewardship/` page and `docs/PRESERVATION.md` explain the limits: a SHA-256 match is not a digital signature, historical source assessment, rights clearance or offsite backup. CI tests mechanical integrity and selected live files, but a responsible custodian must independently maintain and periodically recover copies. An automated Pages deployment is not a substitute for real-device WCAG 2.2 checks, copyright and manuscript permissions review, or specialist verification.

Keep `allow_indexing: false` until a separate deliberate editorial launch approval. Never turn on indexing or describe unassigned custodians/reviewers as active just to pass a checklist. Maintain the Next Chapters milestone, and link a major published change to an actual merged revision commit once that SHA is known.

## Middle Assyrian social-history contributions

The nine original everyday-life studies are stored in `data/middle-assyrian-articles.json`, with source roles in `data/section-evidence.json` and unresolved statement-level verification in `data/claim-reviews.json`. A substantive new section needs a dated primary tablet edition, identified findspot and/or a named scholarly discussion. Explain which parts are law, administrative accounting, royal ideology, an excavation context or modern interpretation.

Avoid transferring Old Assyrian commercial letters or later Neo-Assyrian deportation records into a Middle Assyrian household without explicit period qualification. Biblical passages are primary for their own ancient narrative; do not represent their words as a direct transcript of a thirteenth-century Middle Assyrian archive. Respect the experiences of vulnerable and enslaved people without inventing reconstructed personal biographies. Only approved source metadata and original prose should be committed; do not copy museum photographs or modern translations without permission.

## Biblical and archaeological evidence dossiers

The eight object-level comparison guides are kept in `historical_evidence_content.py`, with section trails recorded in `data/section-evidence.json`, curated source records in `sources.json` and text-anchored review items in `data/claim-reviews.json`. New studies must distinguish the exact wording and genre of biblical passages from independent inscriptions, museum catalogues, archaeology or modern historical interpretation.

Always identify the physical object accession, edition or named source when possible, and explain whether a claim concerns a depicted scene, a translated royal inscription, a biblical narrative or a proposed chronological reconstruction. If ancient texts differ, describe the difference rather than declaring the entire story historically proven on the strength of one parallel. Maintain qualified status until a named specialist reviewer has checked the precise passage and inscription. Do not use third-party object imagery without case-specific rights clearance.

## Source health and accessibility audits

When adding or changing a source, retain its stable ID, publisher, type, actual consultation date and an HTTPS address that points to a genuinely public institutional resource. Do not automatically update the recorded `checked` date from a network probe. Review changes to an article's bibliography, section evidence, claim anchors and related routes at the same time.

Use `python scripts/audit_sources.py` for offline syntax/metadata checks. To see current network responses, use `python scripts/audit_sources.py --network --output .qa/source-health.json` or the separate monthly/manual GitHub Actions workflow. Status classes are observations requiring human investigation; a block, 404, timeout or redirect is not automatically evidence a historical record ceased to exist.

The representative HTML audit runs inside `python scripts/validate.py` and examines accessible labels, landmarks, navigation, headings and image alternatives on common user journeys. Passing is not a conformance certificate. For changes to user-visible controls, perform manual keyboard-only, mobile zoom, screen-reader and touch testing, particularly on the map and Syriac language pages. Preserve visible focus and reduced-motion alternatives. Record what was actually tested in the roadmap, not an assumed outcome.

## Implementation

Every significant feature or research milestone, including previously undocumented work, must also be recorded in `data/project-roadmap.json` with its accurate status, what has been delivered and what remains. The About page's Next Chapters section is generated directly from this file. Do not mark work complete because code was written if its validation or deployment is still pending.

Every new public hub page must be registered in `navigation.py` so it appears in both desktop and mobile menus. Keep short link descriptions, use native disclosure semantics and test generated links under both root and subpath deployments. Avoid putting essential pages only in another page's body or footer.


Edit maintained assets under `static/`. Keep browser features independent of a database or external service unless that change is explicitly scoped. Use Australian English and ordinary ASCII hyphens and dashes in authored prose. Preserve exact quotations, identifiers and third-party licence text where fidelity requires it.

Run the build and validator before proposing a change. A pull request should state the problem, the resulting behaviour, evidence for new content and the checks completed. GitHub CI validates structure and links, not historical truth or licence ownership.
