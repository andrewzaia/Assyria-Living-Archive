# Assyria | The Living Archive

An independent reference website for Assyrian history, language, culture, faith, places and diaspora communities.

The foundation edition contains 40 introductory articles, 51 source records, six topic collections and a selected timeline. Search, filters, saved reading lists and contribution-draft downloads work in the browser. There is no database, account service or submission backend.

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

The articles are sourced introductions and have not received specialist peer review. Some references are public book descriptions with variable full-text access. Reading-list data remains in the visitor's browser. Contribution drafts are downloaded locally and are not submitted.

## Interactive historical atlas

The `/map/` page adds eleven dated teaching sketches (1350-609 BCE), a draggable timeline, play/pause, chapter selection, modern borders, a comparison with 671 BCE, historical city context, and keyboard-accessible zoom/pan. It uses plain JavaScript and self-hosted SVG geography, with no API keys, tile services or runtime libraries. Original schematic boundaries are explicitly interpretive; they are not province-level GIS evidence. All chronology, source notes, coordinate sketches and the Natural Earth land, country and selected river data are retained in `archive/maps/`. See [the map methodology](archive/maps/README.md).

`python scripts/validate_atlas.py` checks chronology, source references, geometry and the retained basemap hashes offline. The ordinary site validator runs these checks too. JavaScript syntax checks include `static/map.js`. Browser verification is still required for interaction and layout.

## Biblical primary sources

The `/bible/` collection begins with Scripture for biblical accounts and cites book, chapter and verse before commentary. It adds 26 original reading guides, a searchable named-reference index and complete local chapter readers. Relevant existing articles and map stages link to the primary passages. Translation choices, unnamed rulers, canonical differences and added historical interpretations are made explicit.

The complete public-domain World English Bible British Edition with Deuterocanon is preserved as 81 source book files, containing 38,058 verse lines. The original text can be reconstructed byte for byte in manifest order. `archive/bible/README.md` documents the edition, rights, scope, acquisition and search rules. This source edition includes additional books whose canonical status differs by tradition.

`python scripts/validate_bible.py` verifies source reconstruction, references, concordance and exact Scripture wording in the generated reader. It is also run by the ordinary site validator. `scripts/capture_bible.py` is an explicit acquisition tool, separate from offline builds. Original source punctuation is preserved in exact quotations; editorial prose retains the ASCII hyphen standard.

## Encyclopaedia expansion record

The second encyclopaedia expansion is measured against `data/encyclopaedia-round-two-baseline.json`. Article words exclude the Bible reader, retained Bible books and interface copy; retained reference notes and bibliography are included. `/about/expansion/` and `/encyclopaedia-growth.json` show comparable counts and the counting limits. `/glossary/` links short definitions to longer sourced entries.

The active reference manifest is `archive/encyclopaedia-references.json`, falling back to the original manifest when absent. Original API responses are preserved losslessly in deterministic gzip files, with checksums for both compressed and original bytes. The older source edition remains in Git history and its original files remain retained. Preserved external references are labelled as such, including shared regional context. Their inclusion does not imply independent scholarly review or an Assyrian identity for every subject. The acquisition tool never runs during ordinary builds.
