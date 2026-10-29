# Publication, integrity and recovery runbook

**Status:** The site is publicly accessible through GitHub Pages, but its tracked `site.config.json` still sets `allow_indexing: false`. This runbook does not approve search indexing, independently certify historical content or establish an offsite backup service.

## 1. Build a fresh website copy

Use Python 3.12 or newer from the repository root:

```sh
python generate.py
python scripts/validate.py
```

This builds `dist/`, including `preservation-manifest.json`, and verifies the complete output against its file list and SHA-256 checksums. The manifest has one record per public output file (excluding itself), with relative path, length in bytes and digest; it also stores the effective deployment base path and indexing setting. It is deterministic for identical build bytes and configuration. No database, user credentials or private account export is needed.

This is a **fixity manifest**, not a cryptographic signature. It cannot tell whether a malicious party replaced both a document and its manifest, whether a source was credible, or whether an external link has gone dead. Retain a trusted copy of the source commit and the manifest through an independently controlled mechanism.

## 2. Export and independently restore a complete copy

```sh
python scripts/export_archive.py --output ../assyria-site-backup.zip
```

The tool rechecks `dist/`, writes a deterministic ZIP outside the generated website, extracts it into a temporary directory and recalculates every checksum. The resulting ZIP contains the complete published website and its manifest. A failed verification deletes the attempted ZIP.

Do not place completed interviews, personal files, API credentials, server tokens, consent documents or restricted images in the public project or the export. The live website is already a public collection and not secure storage.

The ZIP is a **recovery copy**, not by itself a backup policy. Independently preserve the exact corresponding Git commit or repository snapshot, the export, the manifest and rights/attribution records. If source code is available, rebuilding may produce different bytes under a different Python version, source revision or site URL setting; compare manifests only against the matching build.

## 3. Verify a transferred or restored copy

Extract a trusted ZIP into an empty directory. The command below is suitable for the ZIPs produced by this project's export script; do not blindly extract an untrusted archive.

```sh
mkdir -p ../assyria-restored
python -m zipfile -e ../assyria-site-backup.zip ../assyria-restored
python -c "from preservation import verify_manifest; print('Checked files:', verify_manifest('../assyria-restored')['file_count'])"
```

To investigate a mismatch, retain the original copy as evidence, identify the affected path, examine a trusted version and replace from a previously verified copy. Do **not** simply update the expected checksum to make the test pass.

## 4. Maintain multiple independent copies

A responsible long-term preservation programme needs a named custodian and repeated, recorded checks. Recommended next operational steps:

- Keep at least three managed copies on two distinct storage media or providers, including one offsite. Avoid treating GitHub source history, temporary GitHub Actions artifacts and a single cloud drive as three independent copies.
- Schedule at least quarterly integrity comparisons, and test extracting a complete copy at least annually. These are suggested future operating intervals, **not existing automated tasks**.
- Keep a dated log of the manifest digest, source revision, export destination, copy location, file count, verification result and responsible custodian, without publishing credentials or private storage paths.
- Review licence notices for third-party references, fonts, images, manuscripts and sound material. Public access alone does not permit unrestricted reuse.
- Periodically check outbound institutional source links. The local source register preserves citations, but live publishers can change or remove their URLs.
- Record unexpected file changes, loss events, restoration attempts and replacement decisions in a private operational audit trail, with appropriate public notices for material affecting readers.

This plan follows the Library of Congress's guidance on establishing, documenting and regularly comparing fixity metadata. It does not claim Library of Congress custody, approval or compliance.

## 5. Publication gates before enabling indexing

**Do not change `allow_indexing` merely to make a validator green.** The public site uses explicit `noindex,nofollow` until a separate editorial launch decision.

A responsible release assessment includes:

- Named accountable editor/custodian and governance authority.
- Specialist review of key historical and biblical interpretation, where required, and clear limitations for unreviewed content.
- Acknowledged script and pronunciation limitations, with real font and device checks for Syriac.
- Cross-browser manual review of the atlas, timeline, forms, keyboard access, visible focus, mobile reflow, screen-reader navigation and reduced motion, using WCAG 2.2 as a reference without claiming full conformance.
- Rights and consent verification for displayed media; confirm no private testimony or unapproved contact records are published.
- Recovery ZIP export and verification, plus a tested independent backup retention plan.
- Correct canonical and sitemap settings for the desired root domain, plus no conflicting GitHub Pages publishing mechanisms.
- Site-wide links, static generator and preservation manifest passing root and subpath tests.
- Public milestone and correction ledger statements matching the actual record.

Only after approval should site configuration change be proposed in its own reviewed release. Remember that GitHub Pages availability is separate from search-engine indexing.

## 6. Automation and live verification

The repository's `.github/workflows/validate.yml` builds both root and project-path configurations. The Pages workflow builds and validates the configured Pages location before deployment, then probes the resulting published site. These checks now include the preservation manifest and stewardship page, plus selected live-file hash comparisons.

The negative preservation tests include a tampered HTML file, an unexpected file, a removed file, a duplicated manifest entry and a ZIP restoration check. Their success shows the scripts reject these controlled changes, not that historic backups already exist.

### References

- Library of Congress, Data Integrity Management: https://www.loc.gov/programs/digital-collections-management/inventory-and-custody/data-integrity-management/
- W3C Web Accessibility Initiative, Understanding WCAG 2.2: https://www.w3.org/WAI/WCAG22/Understanding/
- Editorial corrections and review policy: https://andrewzaia.github.io/Assyria-Living-Archive/governance/

**Operational truth:** The manifest, tool and documentation are delivered here. Independent, geographically separate backups, scheduled fixity checks, live link monitoring, complete accessibility conformance tests and specialist scholarly approvals still require dedicated owners and future work.
