# Assyria | The Living Archive

An independent reference website for Assyrian history, language, culture, faith, places and diaspora communities.

The foundation edition contains 40 introductory articles, 51 source records, six topic collections and a selected timeline. Search, filters, saved reading lists and contribution-draft downloads work in the browser. There is no database, account service or submission backend.

## Quick start

Install Python 3.12 or newer. The website builder uses only the Python standard library; there are no pip or npm packages to install.

```sh
python generate.py
python scripts/validate.py
python -m http.server 8000 --directory dist --bind 127.0.0.1
```

Open `http://127.0.0.1:8000`. Stop the server with Ctrl+C. Opening HTML directly from disk will prevent catalogue search from loading reliably; use the local server.

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
| `.github/workflows/validate.yml` | Build checks on pushes and pull requests |
| `dist/` | Generated website, ignored by Git and rebuilt each time |

Edit `static/` rather than `dist/`. Every build recreates `dist/` from the maintained files, so stale generated pages are removed.

## Site settings

The supplied configuration is suitable for local development:

```json
{
  "site_url": "",
  "base_path": "",
  "allow_indexing": false
}
```

- `site_url`: the origin only, such as `https://example.com`, without a trailing path. Leave blank to omit canonical and Open Graph URL metadata during development.
- `base_path`: blank for a domain root; use a path such as `/Assyria-Living-Archive` for a GitHub Pages project site. Do not include the origin here.
- `allow_indexing`: keep `false` while reviewing the foundation edition. Set `true` deliberately for a public launch. A valid `site_url` is required before enabling it.

Environment variables `SITE_URL`, `BASE_PATH` and `ALLOW_INDEXING` override the corresponding settings. `ALLOW_INDEXING` accepts `true` or `false`. Builds generate the appropriate robots metadata and `robots.txt`; indexable builds also generate `sitemap.xml`.

Search-engine exclusion does not provide access control. The private ChatGPT-hosted edition's sign-in gate belongs to that hosting service and is not included in this export. A deployment elsewhere needs its own access controls if you want it to remain private.

## Create your GitHub repository

Suggested name: **Assyria-Living-Archive**. Create an empty private repository first, without adding an initial README or licence in GitHub.

If you use the source folder from the ZIP:

```sh
git init -b main
git add .
git commit -m "Prepare Assyria Living Archive repository"
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

Replace `YOUR_REPOSITORY_URL` with the HTTPS or SSH URL of your actual repository. Run these commands from the extracted project folder. Set your Git author name and email first if Git requests them.

The package also includes a Git bundle with the prepared initial commit. See `IMPORT.md` beside the project folder for the clone command if you prefer that route.

## Deploy to Cloudflare Pages

Connect the GitHub repository using the Pages Git integration and use:

| Setting | Value |
| --- | --- |
| Framework preset | None |
| Production branch | `main` |
| Build command | `python3 generate.py` |
| Build output directory | `dist` |
| Root directory | Repository root |
| Python version | 3.12 or newer |

Use `SITE_URL` for the final origin. Keep `BASE_PATH` empty for the domain root. Set the build environment's `PYTHON_VERSION` to `3.12` if needed. These instructions prepare the build; they do not create a Cloudflare project or publish the export.

Reference: [Cloudflare Pages build configuration](https://developers.cloudflare.com/pages/configuration/build-configuration/).

## GitHub Pages project paths

The build supports a repository path, for example:

```json
{
  "site_url": "https://YOUR_USERNAME.github.io",
  "base_path": "/Assyria-Living-Archive",
  "allow_indexing": false
}
```

Publish the generated `dist/` directory using a Pages deployment workflow or a separate deployment branch. The included Actions workflow validates both root and project-path builds; it does not deploy. No hosting is enabled automatically by this package.

To preview a project-path build locally, place `dist/` beneath a folder whose name matches the configured base path and serve its parent. For ordinary local work, leave `base_path` blank.

## Validation

```sh
python generate.py
python scripts/validate.py
node --check static/app.js
```

Node.js is optional for local JavaScript syntax checking, not required to build or serve the website. GitHub-hosted CI runs the checks with Python 3.12 and checks the project-path configuration too. Action versions are pinned to immutable commits.

The validator checks article/source relationships, unique slugs and IDs, local navigation and fragment links, referenced assets, catalogue counts, indexing metadata and the ASCII dash convention. External source sites are not fetched by CI. Citation quality and historical accuracy still require editorial review.

## Editing and contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the article schema and evidence requirements. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for image and font attribution. No general open source licence has been selected for the original project files.

The articles are sourced introductions and have not received specialist peer review. Some references are public book descriptions with variable full-text access. Reading-list data remains in the visitor's browser. Contribution drafts are downloaded locally and are not submitted.
