"""One site-wide navigation catalogue for desktop, mobile and link validation."""
from html import escape

# Group, then (label, local path, short description). Add new public hub pages here.
NAV_GROUPS = (
    ('Explore', (
        ('Encyclopaedia', '/explore/', 'All articles and preserved references'),
        ('Historical timeline', '/timeline/', 'Key moments across the centuries'),
        ('Middle Assyrian life', '/middle-assyrian/', 'Families, fields, law and everyday work'),
        ('Interactive map', '/map/', 'Assyria through time and geography'),
        ('Glossary', '/glossary/', 'Terms, names and reading routes'),
        ('Languages and scripts', '/languages/', 'Syriac letter reference, dialect recordings and manuscripts'),
        ('Community heritage', '/heritage/', 'Public oral-history leads and preservation tools'),
    )),
    ('Scripture', (
        ('Assyria in the Bible', '/bible/', 'Biblical accounts and study guides'),
        ('Biblical verse index', '/bible/passages/', 'Search named references in Scripture'),
    )),
    ('Research', (
        ('Source library', '/sources/', 'Primary records and further reading'),
        ('Historical evidence dossiers', '/dossiers/', 'Biblical passages and accessioned Assyrian records'),
        ('Royal inscriptions and Scripture', '/royal-witnesses/', 'Direct Assyrian edition lines and biblical comparisons'),
        ('Fall of Samaria and succession', '/samaria-succession/', 'Dated biblical and royal source comparisons from tribute to exile'),
        ('Individual tablet case files', '/case-files/', 'Accessioned objects, editions and archive provenance'),
        ('Text and translation comparisons', '/text-comparisons/', 'Cuneiform signs, editorial readings and uncertainties'),
        ('Ancient text concordance', '/concordance/', 'Cross-reference people, places, materials and Scripture'),
        ('Identity and name register', '/identity-register/', 'Case-by-case evidence limits for names and places'),
        ('Evidence register', '/about/evidence/', 'Sources linked to editorial guides'),
        ('Source and accessibility audit', '/audit/', 'Citation health, accessibility checks and limitations'),
        ('Editorial governance', '/governance/', 'Corrections, review standards and recorded revisions'),
        ('Publication and stewardship', '/stewardship/', 'Preservation checks, recovery and release readiness'),
        ('Expansion dashboard', '/about/expansion/', 'Archive growth and coverage figures'),
    )),
    ('Project', (
        ('About the archive', '/about/', 'Purpose, editorial principles and roadmap'),
        ('Contribute', '/contribute/', 'Prepare a sourced correction or addition'),
        ('Credits and reuse', '/credits/', 'Attribution, permissions and licences'),
    )),
)

# Named column groupings keep deep navigation discoverable without building a
# tall one-column desktop dropdown. Paths are the single source of link identity:
# the same named groups render on desktop and as stacked sections on mobile.
NAV_COLUMNS = {
    'Explore': (
        ('Discover', ('/explore/', '/timeline/', '/middle-assyrian/', '/map/')),
        ('Culture and language', ('/glossary/', '/languages/', '/heritage/')),
    ),
    'Research': (
        ('Sources and texts', ('/sources/', '/case-files/', '/text-comparisons/',
                               '/concordance/', '/identity-register/')),
        ('Historical comparisons', ('/dossiers/', '/royal-witnesses/',
                                    '/samaria-succession/', '/about/evidence/')),
        ('Review and stewardship', ('/audit/', '/governance/', '/stewardship/',
                                    '/about/expansion/')),
    ),
}

NAV_PATHS = tuple(path for _, destinations in NAV_GROUPS for _, path, _ in destinations)


def validate_nav_columns():
    """Require each desktop/mobile link to appear exactly once in its group."""
    for name, destinations in NAV_GROUPS:
        if name not in NAV_COLUMNS:
            continue
        paths = [path for _, members in NAV_COLUMNS[name] for path in members]
        original = [path for _, path, _ in destinations]
        if len(paths) != len(original) or len(set(paths)) != len(paths) or set(paths) != set(original):
            raise ValueError('Navigation columns do not cover group exactly once: ' + name)
    if set(NAV_COLUMNS) - {name for name, _ in NAV_GROUPS}:
        raise ValueError('Navigation columns reference an unknown group')


validate_nav_columns()


def current_group(path):
    """Highlight the group containing the current hub or generated content."""
    for name, destinations in NAV_GROUPS:
        if any(path == destination for _, destination, _ in destinations):
            return name
    if path.startswith('/bible/') or path.startswith('/articles/bible-'):
        return 'Scripture'
    if path.startswith('/articles/'):
        return 'Explore'
    return None


def render_navigation(path):
    """Native details remain accessible by keyboard/touch without JavaScript."""
    active = current_group(path)
    groups = []
    for name, destinations in NAV_GROUPS:
        links = {
            destination: (
                '<a class="nav-destination" href="' + escape(destination, quote=True) + '"' +
                (' aria-current="page"' if path == destination else '') + '>' +
                '<span class="nav-title">' + escape(label) + '</span>' +
                '<span class="nav-note">' + escape(note) + '</span></a>'
            )
            for label, destination, note in destinations
        }
        if name in NAV_COLUMNS:
            columns = ''.join(
                '<section class="nav-column" aria-label="' + escape(title, quote=True) + '">' +
                '<p class="nav-column-heading">' + escape(title) + '</p>' +
                ''.join(links[destination] for destination in members) + '</section>'
                for title, members in NAV_COLUMNS[name]
            )
            panel_class = 'nav-panel nav-panel--columns nav-panel--' + name.lower()
            items = columns
        else:
            panel_class = 'nav-panel'
            items = ''.join(links[destination] for _, destination, _ in destinations)
        groups.append(
            '<details class="nav-group' + (' is-current' if active == name else '') +
            '" data-nav-group="' + escape(name, quote=True) + '">' +
            '<summary class="nav-trigger">' + escape(name) + '</summary>' +
            '<div class="' + panel_class + '">' + items + '</div></details>'
        )
    return ''.join(groups)
