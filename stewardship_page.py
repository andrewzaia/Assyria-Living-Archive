"""Static public explanation of the archive's built-site preservation limits."""
from html import escape as h
from site_config import ALLOW_INDEXING, BASE_PATH

def render(heading):
    indexing = (
        '<strong>Indexing enabled by release configuration.</strong> Canonical URLs and sitemap checks remain separate from editorial approval.'
        if ALLOW_INDEXING else
        '<strong>Search indexing deliberately disabled.</strong> The build sets noindex metadata and disallows indexing in robots.txt pending publication approval.'
    )
    return (
        '<main id="main" class="wrap section narrow-page stewardship-room">' +
        heading('PRESERVATION / PUBLICATION', 'Make the archive recoverable.',
                'A transparent guide to generated-site integrity, publication safeguards and work still requiring human stewardship.') +
        '<div class="stewardship-lead"><h2>Keep an auditable copy.</h2>' +
        '<p>The archive is generated from versioned source files and locally preserved reference records. ' +
        'A new SHA-256 manifest describes the exact bytes and names of the generated website. ' +
        'It allows later copies to be checked for unexpected changes, but it does not by itself create an offsite backup, ' +
        'certify the truth of a text, or prove that a separate historical manuscript is authentic.</p>' +
        '<a href="/preservation-manifest.json">Inspect the build integrity manifest (JSON)</a></div>' +
        '<section class="stewardship-section" id="integrity"><span class="eyebrow">BUILT-SITE FIXITY</span>' +
        '<h2>What the manifest actually verifies.</h2><ol class="stewardship-steps">' +
        '<li><strong>Inventory.</strong> Record each generated public file with its relative path and byte length, from pages and scripts to licensed assets, archive copies and data exports.</li>' +
        '<li><strong>Digest.</strong> Calculate a SHA-256 checksum for each file after the build is complete. The manifest excludes only itself to avoid a self-referential checksum.</li>' +
        '<li><strong>Compare.</strong> After an export, transfer or restoration, reject missing, additional and altered files. Keep a trusted manifest and independent copies; a hostile actor able to rewrite both file and checksum is not detected by fixity alone.</li>' +
        '<li><strong>Restore.</strong> A tested ZIP export recreates the site in an isolated directory and checks the entire extracted collection against the manifest. The export is created by a local tool, not downloaded automatically from this public page.</li>' +
        '</ol><p class="stewardship-citation">Method informed by the ' +
        '<a href="https://www.loc.gov/programs/digital-collections-management/inventory-and-custody/data-integrity-management/" target="_blank" rel="noopener">Library of Congress data integrity management guidance</a>. ' +
        'A checksum proves file equivalence to a baseline, not institutional custody or external-source accessibility.</p></section>' +
        '<section class="stewardship-section" id="publication"><span class="eyebrow">RELEASE READINESS</span>' +
        '<h2>Publication is a separate decision.</h2>' +
        '<p>' + indexing + '</p>' +
        '<ul class="stewardship-status">' +
        '<li><strong>Automated site checks:</strong> navigation, source links, Bible and atlas fixtures, data integrity, and two URL-path builds. Continuous integration checks can fail a release but cannot certify every historical claim.</li>' +
        '<li><strong>Editorial governance:</strong> <a href="/governance/">review roles, corrections and the public revision record</a> are documented. Independent specialist sign-offs are not yet recorded.</li>' +
        '<li><strong>Language and accessibility:</strong> Syriac font shaping, keyboard-only use, screen-reader checks, reduced-motion paths and representative desktop/mobile browser testing still require real-device review.</li>' +
        '<li><strong>External references and media:</strong> provider availability, licensing and changing live URLs require periodic human review; the reference library and public heritage catalogue do not licence third-party audio or images.</li>' +
        '<li><strong>Offsite backups:</strong> multiple independently stored and periodically restored copies are a future operational task. GitHub source history and a website ZIP alone are not a documented multi-location backup programme.</li>' +
        '</ul><p class="stewardship-citation">Accessibility review is organised against the ' +
        '<a href="https://www.w3.org/WAI/WCAG22/Understanding/" target="_blank" rel="noopener">W3C WCAG 2.2 explanatory guidance</a>. ' +
        'The archive makes no full WCAG conformance claim.</p></section>' +
        '<section class="stewardship-section" id="recovery"><span class="eyebrow">RECOVERY PROCEDURE</span>' +
        '<h2>Restore without inventing a new source.</h2>' +
        '<p>Use the maintained Python generator, offline validator and archive export script. ' +
        'The repository <a href="https://github.com/andrewzaia/Assyria-Living-Archive/blob/main/docs/PRESERVATION.md" target="_blank" rel="noopener">preservation and recovery runbook</a> describes ' +
        'how to rebuild, verify, export, restore, retain independent copies and resolve discrepancies. ' +
        'The generated public data and preserved references are intentionally readable without a private database.</p>' +
        '<pre class="stewardship-command"><code>python generate.py\npython scripts/validate.py\npython scripts/export_archive.py --output ../assyria-site-backup.zip</code></pre>' +
        '<p>Keep a separate copy of the matching source commit, the ZIP, its manifest and rights documentation. ' +
        'If a checksum does not match, investigate and restore a trusted copy rather than silently replacing the expected digest.</p></section>' +
        '<section class="stewardship-section" id="human-review"><span class="eyebrow">HUMAN STEWARDSHIP</span>' +
        '<h2>Preservation is more than files.</h2><p>Scripture remains the starting primary text for biblical accounts. ' +
        'Archaeological records, textual scholarship, local history and community testimony require correctly labelled source roles. ' +
        'Permissions, independent review, correction decisions and the treatment of living people must be revisited by qualified humans. ' +
        'A preserved copy keeps a record available; it cannot resolve disagreement about the historical account.</p>' +
        '<p>See <a href="/about/#next-chapters">Next Chapters</a> for the outstanding release gates, ' +
        '<a href="/about/evidence/">Evidence Register</a> for editorial reference coverage and ' +
        '<a href="/heritage/">Community Heritage</a> for narrator consent and rights guidance.</p></section></main>'
    )
