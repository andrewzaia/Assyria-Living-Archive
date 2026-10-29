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

The published editorial guides currently use article-level bibliography links. The evidence register at `/about/evidence/` and `evidence-index.json` exposes this relationship in both directions; it does not claim that every statement is individually verified. Do not describe an unreviewed source as peer reviewed or a consultation date as independent validation. The foundation template displays a compilation date and article-level reference groups. If substantively updating an entry, review the displayed dates and make the relevant evidence trail clear. Section-level source attribution and individual revision metadata are planned improvements.

## Evidence and identity

- Distinguish primary records, scholarly interpretation, oral testimony, community advocacy and institutional self-description.
- Respect individual and institutional self-designations. Language, ethnicity and church membership are distinct categories.
- Separate ancient Akkadian, Aramaic, Classical Syriac and living Neo-Aramaic varieties accurately.
- Give contested claims named sources and acknowledge important alternative interpretations.
- Avoid unsupported population totals, casualty totals and claims of unchanged practices across millennia.
- Mark personal recollections as testimony. Check consent before publishing interviews, family details or contributed photographs.
- Use original summaries and check reuse rights for every imported asset.

## Implementation

Edit maintained assets under `static/`. Keep browser features independent of a database or external service unless that change is explicitly scoped. Use Australian English and ordinary ASCII hyphens and dashes in authored prose. Preserve exact quotations, identifiers and third-party licence text where fidelity requires it.

Run the build and validator before proposing a change. A pull request should state the problem, the resulting behaviour, evidence for new content and the checks completed. GitHub CI validates structure and links, not historical truth or licence ownership.
