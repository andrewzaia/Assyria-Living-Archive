# Assyria | The Living Archive

An independent reference website for Assyrian history, language, culture, faith, places and diaspora communities.

The initial foundation edition contained 40 introductory articles and 51 source records. The collection has since expanded to 466 reading entries (94 original editorial introductions and Bible guides, plus 372 attributed preserved references), with six topic collections and a selected timeline. Search, filters and saved reading lists work in the browser. Contributions are prepared and downloaded locally as Markdown drafts. Email submissions are on hold until a project-specific sending method is authorised. The site has no database or account service.

## Quick start

Install Python 3.12 or newer. The website builder uses only the Python standard library; there are no pip or npm packages to install.

```sh
python scripts/preview.py
```

Open `http://127.0.0.1:8000`. Stop the server with Ctrl+C. The preview script builds with local URL settings without changing the tracked production configuration. Opening HTML directly from disk will prevent catalogue search from loading reliably; use the local server.

## Repository layout

| Path | Purpose |
| --- | --- |
| `content.py` | Original article introductions and timeline entries |
| `sources.json` | Reference metadata and public source URLs |
| `generate.py` | Static page and catalogue generator |
| `navigation.py` | Shared site-wide menu groups and destination registry |
| `data/claim-reviews.json`, `claim_review.py` | Claim-level evidence queue, direct references and review metadata |
| `data/project-roadmap.json`, `project_roadmap.py` | Single maintained source for the About page's Next Chapters roadmap |
| `site.config.json` | Site origin, base path and indexing choice |
| `site_config.py` | Validated settings and URL handling |
| `static/` | Maintained CSS, JavaScript, images, fonts and licences |
| `scripts/validate.py` | Source and generated-link checks |
| `scripts/preview.py` | Local build and HTTP preview |
| `.github/workflows/validate.yml` | Build checks on pushes and pull requests |
| `.github/workflows/pages.yml` | Validated deployment to GitHub Pages from `main` |
| `dist/` | Generated website, ignored by Git and rebuilt each time |

Edit `static/` rather than `dist/`. Every build recreates `dist/` from the maintained files, so stale generated pages are removed.

## Site settings

The tracked configuration targets this GitHub Pages project:

```json
{
  "site_url": "https://andrewzaia.github.io",
  "base_path": "/Assyria-Living-Archive",
  "allow_indexing": false
}
```

- `site_url`: the origin only, such as `https://example.com`, without a trailing path. Leave blank to omit canonical and Open Graph URL metadata during development.
- `base_path`: blank for a domain root; use a path such as `/Assyria-Living-Archive` for a GitHub Pages project site. Do not include the origin here.
- `allow_indexing`: keep `false` while reviewing the foundation edition. Set `true` deliberately for a public launch. A valid `site_url` is required before enabling it.

Environment variables `SITE_URL`, `BASE_PATH` and `ALLOW_INDEXING` override the corresponding settings. `ALLOW_INDEXING` accepts `true` or `false`. Builds generate the appropriate robots metadata and `robots.txt`; indexable builds also generate `sitemap.xml`.

Search-engine exclusion does not provide access control. The private ChatGPT-hosted edition's sign-in gate belongs to that hosting service and is not included in this export. A deployment elsewhere needs its own access controls if you want it to remain private.

## GitHub Pages hosting

Repository: [andrewzaia/Assyria-Living-Archive](https://github.com/andrewzaia/Assyria-Living-Archive).

The Pages deployment workflow builds the maintained source into `dist/`, validates it, uploads the generated website and deploys it. It runs on pushes to `main` and can be started manually from Actions. If GitHub's branch-based Pages publisher is still enabled, deployment waits for that publisher to finish before publishing the generated website. Live route and asset checks then verify the published result. Pull requests run validation only.

In the repository's **Settings > Pages > Build and deployment**, select **GitHub Actions** as the source. The workflow reads the configured Pages origin and base path, so it can also adapt to a future custom domain without rewriting asset links.

The current project URL is `https://andrewzaia.github.io/Assyria-Living-Archive/`. Search indexing remains disabled in `site.config.json` while the foundation edition is under review. Enable it deliberately when the content is ready for indexing.

Reference: [GitHub's custom Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Working with the repository

```sh
git clone https://github.com/andrewzaia/Assyria-Living-Archive.git
cd Assyria-Living-Archive
python scripts/preview.py
```

After editing, run the validation commands below, commit the source files and push to `main` to trigger deployment. Generated files under `dist/` remain ignored by Git. All maintained assets are under `static/`.

## Validation

```sh
python generate.py
python scripts/validate.py
node --check static/app.js
```

Node.js is optional for local JavaScript syntax checking, not required to build or serve the website. GitHub-hosted CI runs the checks with Python 3.12 and checks the project-path configuration too. Action versions are pinned to immutable commits. GitHub Pages deployment uses a separate workflow and validates its generated output before publication.

The validator checks article/source relationships, unique slugs and IDs, local navigation and fragment links, referenced assets, catalogue counts, indexing metadata and the ASCII dash convention. External source sites are not fetched by CI. Citation quality and historical accuracy still require editorial review.

## Editing and contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the article schema and evidence requirements. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for image and font attribution. No general open source licence has been selected for the original project files.

The articles are sourced introductions and have not received specialist peer review. Some references are public book descriptions with variable full-text access. Reading-list data remains in the visitor's browser. Contribution drafts can be downloaded locally; they are not currently submitted to the editor. Contact details entered into the form appear only in the local draft, unless the contributor later chooses to share it.

## Site-wide navigation

The header uses four concise menus, **Explore**, **Scripture**, **Research** and **Project**, with search and the locally saved reading list kept as header actions. The grouped menus expose every public site hub, including the interactive map, glossary, verse index, evidence register and expansion dashboard, on desktop and mobile. The footer provides a text-link alternative to the same hubs.

Update `NAV_GROUPS` in `navigation.py` when adding a new public hub rather than writing separate desktop and mobile menu lists. The generator uses native `<details>` disclosure elements, allowing keyboard and touch navigation even without JavaScript. The small JavaScript enhancement closes menus on Escape and outside clicks. `scripts/validate.py` checks that every generated page contains every registered destination with correct active link state and valid local paths.

## Interactive historical atlas

The `/map/` page adds eleven dated teaching sketches (1350-609 BCE), a draggable timeline, play/pause, chapter selection, modern borders, a comparison with 671 BCE, historical city context, and keyboard-accessible zoom/pan. Milestone 3 strengthens the historical interpretation of all 11 dates with named reconstruction limitations, explanations of sustained control versus vassalage, warfare and contestation, role-specific notes for each historical source, and cross-links into 21 original editorial or biblical guides. No new exact ancient border coordinates or area statistics are asserted. It uses plain JavaScript and self-hosted SVG geography, with no API keys, tile services or runtime libraries. Original schematic boundaries are explicitly interpretive; they are not province-level GIS evidence. All chronology, source notes, coordinate sketches and the Natural Earth land, country and selected river data are retained in `archive/maps/`. See [the map methodology](archive/maps/README.md).

`python scripts/validate_atlas.py` checks chronology, source references, geometry and the retained basemap hashes offline. The ordinary site validator runs these checks too. JavaScript syntax checks include `static/map.js`. Browser verification is still required for interaction and layout.

## Biblical primary sources

The `/bible/` collection begins with Scripture for biblical accounts and cites book, chapter and verse before commentary. It adds 26 original reading guides, a searchable named-reference index and complete local chapter readers. Relevant existing articles and map stages link to the primary passages. Translation choices, unnamed rulers, canonical differences and added historical interpretations are made explicit.

The complete public-domain World English Bible British Edition with Deuterocanon is preserved as 81 source book files, containing 38,058 verse lines. The original text can be reconstructed byte for byte in manifest order. `archive/bible/README.md` documents the edition, rights, scope, acquisition and search rules. This source edition includes additional books whose canonical status differs by tradition.

`python scripts/validate_bible.py` verifies source reconstruction, references, concordance and exact Scripture wording in the generated reader. It is also run by the ordinary site validator. `scripts/capture_bible.py` is an explicit acquisition tool, separate from offline builds. Original source punctuation is preserved in exact quotations; editorial prose retains the ASCII hyphen standard.

## Encyclopaedia expansion record

The second encyclopaedia expansion is measured against `data/encyclopaedia-round-two-baseline.json`. Article words exclude the Bible reader, retained Bible books and interface copy; retained reference notes and bibliography are included. `/about/expansion/` and `/encyclopaedia-growth.json` show comparable counts and the counting limits. `/glossary/` links short definitions to longer sourced entries.

The active reference manifest is `archive/encyclopaedia-references.json`, falling back to the original manifest when absent. Original API responses are preserved losslessly in deterministic gzip files, with checksums for both compressed and original bytes. The older source edition remains in Git history and its original files remain retained. Preserved external references are labelled as such, including shared regional context. Their inclusion does not imply independent scholarly review or an Assyrian identity for every subject. The acquisition tool never runs during ordinary builds.


## Encyclopaedia depth milestone - original historical studies

The next research expansion adds **14 original guides and 56 section-level evidence trails**, rather than importing another batch of preserved third-party articles. These guides cover Ashurnasirpal II, Shalmaneser III, Tiglath-pileser III, Shalmaneser V, Sargon II, Sennacherib, Esarhaddon, Ashurbanipal, imperial governance, state-directed population movements, ancient religion, multilingual administration, Nineveh's fall, and later regional history. The new original article sections contain approximately 3,776 additional words. Ten specifically named scholarly and museum records were added to `sources.json`; recorded checking dates reflect the date of actual source consultation.

New and old articles link to one another through related reading routes. The selected timeline now includes Assyrian reigns and events of 701, 671, 612 and 609 BCE, while keeping biblical claims distinct from historical dating. The additional 56 section reading trails live in `data/section-evidence.json` and are validated offline. **This is a documented editorial expansion, not specialist peer review or independent confirmation of each sentence.** In-depth inscription passage checks and independent subject-matter review remain future work.

## Evidence traceability and review

The `/about/evidence/` register is a measured, navigable index of editorial guides and the source records they cite. The source library now links referenced source records back to their editorial guides and displays each source's recorded check or retrieval date rather than a single hardcoded date. The register can be downloaded as `/evidence-index.json`.

The first section-level research pass now identifies **157 individually mapped sections across 55 guides**, including locally hosted Scripture links. The exact section-to-reference mappings live in `data/section-evidence.json` and are checked by `section_evidence.py`. Add a mapping only after verifying that the named source or passage is relevant to that specific section. Bible passages must already occur within the guide's primary passage list, and linked non-biblical sources must exist in its bibliography. The editor may leave a section unmapped rather than assign tenuous evidence.

The register exports the mapped and unmapped section counts, source IDs and book/chapter/verse coordinates in `/evidence-index.json`. The generator adds small "Section reading trail" boxes beneath mapped sections, without changing the full article bibliography. The source library also records the University of Pennsylvania's RINAP royal inscriptions collection as independent historical source material, separate from Scripture. The Sargon guide now retains the specialist note on the Assyrian official title Tartan while also citing a Sargon-specific historical study from Assyrian Empire Builders.

**These are selected reading trails, not a claim-by-claim fact check.** A mapped section is not thereby fully substantiated; neither a source link, a recent check date nor a high citation count proves historical accuracy. Original guides have no recorded specialist peer review, and preserved external texts remain credited, not locally endorsed. Next: sentence-level notes on contested claims, direct inscription/tablet identifications and documented expert review.

`scripts/validate.py` verifies the generated evidence index against article metadata, checks every section mapping and ensures the expected trail is present on the generated page. Both root and GitHub Pages subpath builds test local links and Bible verse targets.


## Language and cultural heritage milestone

The /languages/ reference room is generated from `data/syriac-letters.json` and `language_page.py`. It provides a compact research route to eight new specialist-sourced editorial guides and a static reference grid of **22 Unicode Syriac letter identities** (U+0710 through U+072C, excluding supplementary characters). The characters are Unicode identifiers, not a pronunciation model or facsimiles of Estrangela, Serto or East Syriac manuscript hands. Native right-to-left text rendering depends on the user's system shaping and fonts.

The milestone also adds **32 new mapped editorial sections**, eight additional institutional and academic source records, and direct external links to Cambridge NENA **Urmi, Alqosh and Ankawa** recording pages. Manuscript letterform comparisons link to HMML School without copying protected images. No generated audio, assumed accent, unlicensed text editions or unreviewed transliterations have been added. Linguistic peer review, permission-cleared audio, dialect-specific transliteration keys and real browser typography checks remain open. The generated hub is validated alongside the ordinary site paths by `scripts/validate.py`.

## Community testimony and heritage preservation milestone

The public `/heritage/` room presents **ten linked, already published records** as leads for research into migration, Assyrian community organisations, living languages, broadcasts and cultural practice. The curated external-source register is maintained in `data/heritage-records.json` and exported as `/heritage-records.json`. Each entry states its source role, the original custodian and the restriction that no media is locally copied. Categories are filtered in the browser without any account, network request or tracking.

Six original articles and **24 new section-level source trails** explain interviewing, village research, diaspora accounts, art and everyday culture, broadcast references and consent. The three original blank worksheets in `archive/heritage/` are downloadable Markdown: a story-planning sheet, open-ended interview prompts, and a permissions-review checklist. They are **not** participant consent forms, automatically collected submissions, or evidence of permission to publish. Do not commit completed sheets, recordings or private contact details into the public repository.

Editorial workflow: identify credible custodians, verify the record's source role and permitted access, obtain and document participation or reuse permission separately, offer narrator review where appropriate, and publish only approved versions and non-sensitive metadata. Guidance comes from Oral History Australia and the National Library of Australia; those institutions are cited, not affiliated with the project. No private recordings or media are collected or hosted, and the existing contribution form still only downloads a local draft. A secure intake service, verified individual permissions and a named curator are future requirements, not features already completed.

The automated validator checks the heritage dataset's source references, editorial routes, public-only status and download targets; both root and project-path builds validate the hub. The expanded archive has **213 curated section trails across 69 editorial guides**.

## Claim-level verification and the Next Chapters roadmap

The Evidence Register now includes an initial **15 individual, text-anchored claim review records** in `data/claim-reviews.json`. Each links to its exact editorial section, direct biblical passages or institutional records, sources included only for comparison, a qualification, and a review status. All initial records are **awaiting independent specialist review**. Neither a source link nor a structural validation establishes the claim's historical truth. Biblical citations support what the biblical narrative states, not automatic archaeological corroboration. The generated evidence index includes this machine-readable review queue.

`claim_review.py` rejects duplicate IDs, missing anchor text, unknown sections or references, Bible coordinates outside the article's cited passage range and unsubstantiated completed-review labels. Reviewer identity, date and a review note are mandatory before a record can be marked independently reviewed. Future inscription-level comparisons must cite exact royal inscription catalogue identifiers, lines or museum accession records rather than just a corpus homepage.

The About page's **Next Chapters** cards are generated from `data/project-roadmap.json`, which also publishes as `/project-roadmap.json`. This single registry tracks completed, in-progress, planned and on-hold work, including milestones previously scattered through commits and project discussions. **Every significant feature, research addition, newly discovered milestone or change in project status must update this file in the same pull request.** Keep delivered work separate from untested or pending tasks. `project_roadmap.py` validates the registry and `scripts/validate.py` verifies that all registered cards appear in the published About page.

## Contribution email delivery - on hold

**Current public behaviour:** The contribution page generates a Markdown file in the browser. No form contents, optional contact details or attachments are transmitted to a server. There is no email submission button or Turnstile widget while delivery is on hold.

The optional backend implementation is retained in `worker/` for future development, but it is not connected to the public website. The Worker must remain disabled on its public subdomain until an authorised sending arrangement is ready. Running the backend tests does not mean email delivery is enabled or verified.

The sole intended recipient is the project editor's verified personal Outlook mailbox. That recipient address belongs only in an encrypted Cloudflare Worker secret named `CONTRIBUTION_INBOX`, never in public repository files, frontend JavaScript or generated HTML.

Cloudflare's email service cannot send *from* a third-party Outlook address that the project does not control as an authorised sender domain. Do not use an unrelated project domain to work around this limitation. For a future project-specific domain, the sending service requires an authorised sender domain and a `CONTRIBUTION_FROM` secret. An alternative is a separately authorised Microsoft Graph integration with delegated `Mail.Send` permission for the project editor's Outlook account; this requires explicit OAuth consent and secure token management, and is not currently implemented.

Future reactivation requires confirming privacy wording, enabling Turnstile, restricting cross-origin requests, configuring rate limits and sender/recipient secrets, deploying the Worker and verifying a genuine email with the Markdown attachment. Until then, leave the contribution page as download-only and do not advertise email delivery.

Run `node --test worker/tests/*.test.mjs` to check the dormant backend contract. No secrets belong in the git repository.
