"""One site-wide navigation catalogue for desktop, mobile and link validation."""
from html import escape

# Group, then (label, local path, short description). Add new public hub pages here.
NAV_GROUPS = (
    ('Explore', (
        ('Encyclopaedia', '/explore/', 'All articles and preserved references'),
        ('Historical timeline', '/timeline/', 'Key moments across the centuries'),
        ('Interactive map', '/map/', 'Assyria through time and geography'),
        ('Glossary', '/glossary/', 'Terms, names and reading routes'),
        ('Languages and scripts', '/languages/', 'Syriac letter reference, dialect recordings and manuscripts'),
    )),
    ('Scripture', (
        ('Assyria in the Bible', '/bible/', 'Biblical accounts and study guides'),
        ('Biblical verse index', '/bible/passages/', 'Search named references in Scripture'),
    )),
    ('Research', (
        ('Source library', '/sources/', 'Primary records and further reading'),
        ('Evidence register', '/about/evidence/', 'Sources linked to editorial guides'),
        ('Expansion dashboard', '/about/expansion/', 'Archive growth and coverage figures'),
    )),
    ('Project', (
        ('About the archive', '/about/', 'Purpose, editorial principles and roadmap'),
        ('Contribute', '/contribute/', 'Prepare a sourced correction or addition'),
        ('Credits and reuse', '/credits/', 'Attribution, permissions and licences'),
    )),
)

NAV_PATHS = tuple(path for _, destinations in NAV_GROUPS for _, path, _ in destinations)


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
    """Native details menus remain usable without JavaScript or pointer hovering."""
    active = current_group(path)
    groups = []
    for name, destinations in NAV_GROUPS:
        items = ''.join(
            '<a class="nav-destination" href="' + escape(destination, quote=True) + '"' +
            (' aria-current="page"' if path == destination else '') + '>' +
            '<span class="nav-title">' + escape(label) + '</span>' +
            '<span class="nav-note">' + escape(note) + '</span></a>'
            for label, destination, note in destinations
        )
        groups.append(
            '<details class="nav-group' + (' is-current' if active == name else '') + '">' +
            '<summary class="nav-trigger">' + escape(name) + '</summary>' +
            '<div class="nav-panel">' + items + '</div></details>'
        )
    return ''.join(groups)
