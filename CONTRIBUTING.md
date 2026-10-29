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

## Implementation

Every significant feature or research milestone, including previously undocumented work, must also be recorded in `data/project-roadmap.json` with its accurate status, what has been delivered and what remains. The About page's Next Chapters section is generated directly from this file. Do not mark work complete because code was written if its validation or deployment is still pending.

Every new public hub page must be registered in `navigation.py` so it appears in both desktop and mobile menus. Keep short link descriptions, use native disclosure semantics and test generated links under both root and subpath deployments. Avoid putting essential pages only in another page's body or footer.


Edit maintained assets under `static/`. Keep browser features independent of a database or external service unless that change is explicitly scoped. Use Australian English and ordinary ASCII hyphens and dashes in authored prose. Preserve exact quotations, identifiers and third-party licence text where fidelity requires it.

Run the build and validator before proposing a change. A pull request should state the problem, the resulting behaviour, evidence for new content and the checks completed. GitHub CI validates structure and links, not historical truth or licence ownership.
