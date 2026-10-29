"""Public audit methodology and current offline validation coverage, no fake live status."""
from collections import Counter
from html import escape as h
from scripts.audit_sources import audit, load_records
from site_config import ALLOW_INDEXING

AUDIT = audit(load_records(), network=False)
MANUAL = (
    ("Keyboard-only journeys", "Not manually tested", "Traverse every menu, search, map, Bible reader, downloads and local draft controls using Tab, Shift+Tab, Enter, Space and Escape."),
    ("Screen readers and focus order", "Not manually tested", "Check VoiceOver on Safari and NVDA or another desktop screen reader, including live region announcements and Syriac language names."),
    ("Mobile reflow and text zoom", "Not manually tested", "Check 320 CSS pixel layout and 200% to 400% browser zoom without content or function loss."),
    ("Contrast and pointer target sizing", "Not manually tested", "Measure real rendered colours and tap target spacing in all interactive states, including dark atlas panels."),
    ("Syriac shaping and mixed direction", "Not manually tested", "Check right-to-left script joining, Unicode letter forms, font fallbacks and punctuation on actual devices."),
)

def render(heading):
    n = AUDIT["source_count"]
    standards = (
        '<li><strong>Generated HTML:</strong> checked for document language, a skip-to-content link, '
        'one main landmark and heading, labels for interactive controls, button names, image alternatives and '
        'search/mobile navigation semantics across representative routes.</li>'
        '<li><strong>Local navigation:</strong> the existing site generator checks hundreds of '
        'generated local links, destination menus, reading trails and page fragments under root and '
        'GitHub Pages subpaths.</li>'
        '<li><strong>Remote source health:</strong> curated external citations are structurally validated in CI. '
        'Periodic network probing runs separately; a HEAD response may be rechecked with GET, and access '
        'blocks, rate limits, redirects and timeouts are not silently treated as broken references.</li>'
    )
    pending = ''.join(
        '<li><strong>' + h(title) + '</strong><small>' + h(status) + '</small><p>' + h(desc) + '</p></li>'
        for title, status, desc in MANUAL
    )
    indexing = ('Indexing has been enabled by an explicit publication configuration.'
                if ALLOW_INDEXING else 'Search indexing is still intentionally disabled pending publication approval.')
    return (
        '<main id="main" class="wrap section audit-room">' +
        heading('RESEARCH AUDIT / ACCESSIBILITY', 'Show what was checked.',
                'Source-health methods, automated accessibility checks and human testing still outstanding. A linked URL is not verified evidence.') +
        '<div class="audit-metrics"><div><strong>' + str(n) + '</strong><span>Curated source records checked for metadata structure</span></div>' +
        '<div><strong>0</strong><span>Live URL checks claimed by this offline build</span></div>' +
        '<div><strong>' + str(len(MANUAL)) + '</strong><span>Manual accessibility review areas pending</span></div></div>' +
        '<section class="audit-section" id="sources"><span class="eyebrow">SOURCE INTEGRITY</span>' +
        '<h2>Trust the evidence trail, not just a green HTTP status.</h2>' +
        '<p>The local source register has ' + str(n) + ' curated records whose IDs, public URL syntax, citation labels and consultation dates are now validated. ' +
        'The <a href="/sources/">Source Library</a> identifies publishers and source roles; the ' +
        '<a href="/about/evidence/">Evidence Register</a> maps citations to editorial material. ' +
        'Neither an HTTP 200 response nor a working page proves what an ancient inscription says. ' +
        'Preserved external reference articles and links embedded in their full texts are a separate corpus not remotely checked here.</p>' +
        '<p>The <a href="/source-integrity-index.json">machine-readable source metadata audit</a> explicitly labels each item <strong>not-probed</strong>. ' +
        'An authorised repository maintainer can run the external source audit locally, or view the ' +
        '<a href="https://github.com/andrewzaia/Assyria-Living-Archive/actions/workflows/source-audit.yml" rel="noopener" target="_blank">manual or scheduled source audit workflow</a>. ' +
        'Results require human assessment before updating citations: redirects can be appropriate, while some institutional sites block automated probes.</p>' +
        '<ol class="audit-method">' + standards + '</ol></section>' +
        '<section class="audit-section" id="accessibility"><span class="eyebrow">ACCESSIBILITY REVIEW</span>' +
        '<h2>Automated markup tests are only the beginning.</h2>' +
        '<p>WCAG 2.2 includes keyboard operability, clear focus indicators, focus visibility, sensible target sizes and reflow. ' +
        'The archive now runs repeatable representative-page HTML checks and improves disclosure-menu keyboard behaviour and map announcements. ' +
        'A green automated test does not claim full WCAG 2.2 conformance.</p>' +
        '<ul class="audit-pending">' + pending + '</ul>' +
        '<p>Reference: <a href="https://www.w3.org/TR/WCAG22/" target="_blank" rel="noopener">W3C WCAG 2.2 standard</a>. ' +
        'The <a href="/stewardship/">publication checklist</a> keeps human sign-off separate from passing code.</p></section>' +
        '<section class="audit-section" id="method-and-limitations"><span class="eyebrow">PUBLICATION LIMITS</span>' +
        '<h2>Remaining questions stay visible.</h2><p>' + h(indexing) + '</p>' +
        '<p>External link status can change without a new site release. Source rights and participant permissions must be reviewed at the individual work level. ' +
        'Any corrected URL should retain the source record ID and a documented reason for revision. Independent specialist historians, linguists and reviewers ' +
        'are not replaced by an automated citation checker.</p>' +
        '<p>See <a href="/governance/">editorial corrections and review policy</a>, the ' +
        '<a href="/about/#next-chapters">Next Chapters roadmap</a> and ' +
        '<a href="https://github.com/andrewzaia/Assyria-Living-Archive/blob/main/docs/AUDIT-RUNBOOK.md" target="_blank" rel="noopener">the audit runbook</a> for procedures and outstanding responsibilities.</p></section></main>'
    )
