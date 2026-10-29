"""Public editorial governance and change ledger. No fabricated reviewers or open intake."""
import json
import re
from datetime import date
from html import escape as h
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / 'data/editorial-revisions.json').read_text(encoding='utf-8'))
REVIEW_LEVELS = {'automated-validation-only', 'editorial-review', 'independent-specialist-review'}
CHANGE_KINDS = {'feature-release', 'correction', 'clarification', 'withdrawal'}
CHECKLISTS = (
    ('Correction planning worksheet', '/archive/governance/correction-planning-template.md',
     'Describe the exact published claim, contradictory evidence, requested action and outstanding questions.'),
    ('Editorial release review checklist', '/archive/governance/editorial-release-checklist.md',
     'Test source trails, citation roles, permissions, specialist review status, and build validation.'),
)

def check_review(review, identifier):
    if review.get('level') not in REVIEW_LEVELS:
        raise ValueError('Unknown editorial review level: ' + identifier)
    who, when = review.get('independent_reviewer'), review.get('reviewed_on')
    if review['level'] == 'independent-specialist-review':
        if not who or not when or not review.get('review_note'):
            raise ValueError('Independent review needs name, date and scoped note: ' + identifier)
        date.fromisoformat(when)
    elif who or when or review.get('review_note'):
        raise ValueError('Non-independent review must not imply specialist sign-off: ' + identifier)

def validate():
    if DATA.get('schema_version') != 1 or DATA.get('project') != 'andrewzaia/Assyria-Living-Archive':
        raise ValueError('Invalid or mismatched editorial register')
    date.fromisoformat(DATA['updated_on'])
    if not DATA.get('method') or not DATA.get('correction_policy'):
        raise ValueError('Editorial method or correction policy missing')
    roles = DATA.get('roles', [])
    if len(roles) < 3 or len({role['id'] for role in roles}) != len(roles):
        raise ValueError('Editorial governance roles not specified')
    for role in roles:
        if not role.get('description') or role.get('assignment') not in ('unassigned','project-maintainer'):
            raise ValueError('Unsupported editor/reviewer role assignment: ' + role.get('id', '?'))
    if not any(role['id'] == 'independent-reviewer' and role['assignment'] == 'unassigned' for role in roles):
        raise ValueError('Do not invent an assigned independent reviewer')
    changes = DATA.get('changes', [])
    if not changes:
        raise ValueError('No published revision entries recorded')
    ids, pairs = [], []
    for event in changes:
        key = event['id']
        if not re.fullmatch(r'REV-[0-9]{4,}', key):
            raise ValueError('Bad revision ID ' + key)
        ids.append(key)
        date.fromisoformat(event['date'])
        if event['kind'] not in CHANGE_KINDS or event['status'] != 'merged':
            raise ValueError('Only historically merged changes are in the release log: ' + key)
        if not re.fullmatch(r'[0-9a-f]{40}', event['commit']) or type(event['pr']) is not int or event['pr'] < 1:
            raise ValueError('Missing immutable merged commit or PR number: ' + key)
        if not all(isinstance(event.get(field), str) and len(event[field].strip()) > 12 for field in ('title', 'summary', 'impact')):
            raise ValueError('Unqualified revision entry: ' + key)
        if not event.get('sections') or not all(s.startswith('/') and ('..' not in s) for s in event['sections']):
            raise ValueError('Invalid article routes: ' + key)
        if not event.get('affected_files') or not all((ROOT / filename).is_file() for filename in event['affected_files']):
            raise ValueError('Revision references missing source files: ' + key)
        check_review(event['review'], key)
        pairs.append((event['date'],key))
    if len(ids) != len(set(ids)) or len({item['commit'] for item in changes}) != len(changes):
        raise ValueError('Repeated revision IDs or merged commits')
    if pairs != sorted(pairs, reverse=True):
        raise ValueError('Revisions must be newest first')
    corrections = DATA.get('corrections', [])
    if not isinstance(corrections, list):
        raise ValueError('Corrections must be an explicit public list, even when empty')
    known = set(ids)
    correction_ids = []
    for correction in corrections:
        ident = correction['id']
        if not re.fullmatch(r'COR-[0-9]{4,}', ident):
            raise ValueError('Invalid correction ID')
        correction_ids.append(ident)
        if correction['revision_id'] not in known:
            raise ValueError('Correction must reference documented published change')
        if correction['status'] not in ('corrected', 'clarified', 'withdrawn'):
            raise ValueError('Pending reports must not appear as completed corrections')
        if not correction.get('article_slug') or not correction.get('original_problem') or not correction.get('editorial_action') or not correction.get('evidence_note'):
            raise ValueError('Correction requires article, issue, action and source assessment')
        date.fromisoformat(correction['date'])
        check_review(correction['review'],ident)
    if len(correction_ids) != len(set(correction_ids)):
        raise ValueError('Duplicate correction ID')
    for _, filename, _ in CHECKLISTS:
        if not (ROOT / filename.lstrip('/')).is_file():
            raise ValueError('Missing governance worksheet: ' + filename)
    return len(changes), len(corrections)

def render(heading):
    releases, corrections = validate()
    role_cards = ''.join(
        '<li><h3>' + h(role['label']) + '</h3><p>' + h(role['description']) + '</p><small>' +
        ('Project maintenance role; individual not identified in this register' if role['assignment'] == 'project-maintainer'
         else 'Not assigned or verified') + '</small></li>'
        for role in DATA['roles']
    )
    rows=[]
    for item in DATA['changes']:
        github = 'https://github.com/' + DATA['project']
        routes = ', '.join('<a href="' + h(url, quote=True) + '">' + h(url) + '</a>' for url in item['sections'])
        rows.append(
            '<li id="revision-' + h(item['id'].lower()) + '" class="governance-entry">' +
            '<details><summary><span class="governance-rev-id">' + h(item['id']) + '</span><span class="governance-rev-title"><strong>' +
            h(item['title']) + '</strong><small>' + h(item['date']) + ' / merged feature release / automated checks only</small>' +
            '</span></summary><div class="governance-rev-content"><p>' + h(item['summary']) + '</p>' +
            '<p><strong>Limits:</strong> ' + h(item['impact']) + '</p><p><strong>Related pages:</strong> ' + routes + '</p>' +
            '<p><a href="' + h(github + '/commit/' + item['commit'], quote=True) +
            '" target="_blank" rel="noopener">Inspect merged commit ' + h(item['commit'][:9]) + '</a> ' +
            '<a href="' + h(github + '/pull/' + str(item['pr']), quote=True) +
            '" target="_blank" rel="noopener">View pull request #' + str(item['pr']) + '</a></p>' +
            '<p class="governance-limitation">Independent specialist review: not recorded.</p></div></details></li>'
        )
    logged = []
    for correction in DATA['corrections']:
        logged.append(
            '<li id="correction-' + h(correction['id'].lower()) + '"><strong>' +
            h(correction['id']) + ' / ' + h(correction['status']) + '</strong> <a href="/articles/' +
            h(correction['article_slug']) + '/">Affected article</a><p>' + h(correction['original_problem']) +
            '</p><p>' + h(correction['editorial_action']) + '</p><p>' + h(correction['evidence_note']) +
            '</p><a href="#revision-' + h(correction['revision_id'].lower()) + '">See revision</a></li>'
        )
    worksheets = ''.join(
        '<li><strong>' + h(label) + '</strong><p>' + h(desc) + '</p><a href="' +
        h(filename, quote=True) + '" download>Download blank Markdown worksheet</a></li>'
        for label, filename, desc in CHECKLISTS
    )
    correction_label = str(corrections) + ' public correction record' + ('s' if corrections != 1 else '')
    return (
        '<main id="main" class="wrap section governance-hub">' +
        heading('EDITORIAL STANDARDS / PUBLIC RECORD', 'Show the work. Correct the record.',
                'Read the archive\'s correction policy, review roles and verifiable changes. A successful build is not historical peer review.') +
        '<div class="governance-intro"><p>' + h(DATA['method']) + '</p>' +
        '<div class="governance-stats"><div><strong>' + str(releases) + '</strong><span>Documented merged milestones</span></div>' +
        '<div><strong>' + str(corrections) + '</strong><span>Public correction entries</span></div></div></div>' +
        '<section class="governance-section" id="corrections" aria-labelledby="governance-corrections-title">' +
        '<span class="eyebrow">AFTER PUBLICATION</span><h2 id="governance-corrections-title">Corrections and withdrawals.</h2>' +
        '<p>A correction is logged when a specific, documented issue in published material is addressed. A clarification adds qualification; a withdrawal warns that material should not be relied upon. An ordinary new feature is not a correction. ' +
        'Reports that are still private, unidentified or under examination do not appear here as confirmed problems.</p>' +
        '<p><strong id="governance-correction-count">' + correction_label + '.</strong> ' +
        'This does not establish that no mistakes exist. No submitted public correction case has been independently verified or closed in this record.</p>' +
        ('<ol class="governance-corrections">' + ''.join(logged) + '</ol>' if logged else '') +
        '<a class="governance-action" href="/contribute/?type=correction">Prepare a local correction draft</a></section>' +
        '<section class="governance-section" id="review-policy"><span class="eyebrow">THE EDITORIAL PROCESS</span>' +
        '<h2>How a reported issue is handled.</h2><ol class="governance-steps">' +
        '<li><strong>Identify.</strong> Point to the exact article, section and statement, and distinguish a factual error from an alternative interpretation or a rights/privacy concern.</li>' +
        '<li><strong>Assess.</strong> Check primary evidence, Scripture for biblical accounts, relevant specialist scholarship, source versions and any living participant\'s consent. Record differing interpretations and unresolved gaps.</li>' +
        '<li><strong>Decide.</strong> Document a reasoned editorial action: correct, clarify, withdraw, retain with explanation or seek a qualified reviewer. Never mark a claim independently reviewed without an identified reviewer, date and scope.</li>' +
        '<li><strong>Publish and trace.</strong> When a public correction is warranted, link the article, evidence, change notice and immutable repository commit, without exposing private correspondence or personal data.</li>' +
        '</ol><p>The submission channel is not currently operational. A draft downloaded from this site is not a submitted report. ' +
        'There is no promised response time or private case-management service.</p></section>' +
        '<section class="governance-section" id="review-roles"><span class="eyebrow">TRANSPARENT ATTRIBUTION</span>' +
        '<h2>Roles and independent verification.</h2><ul class="governance-roles">' + role_cards + '</ul>' +
        '<p>Review roles are defined here, but unassigned positions are not represented as staffed. The ' +
        '<a href="/about/evidence/#claim-register-title">claim-level evidence queue</a> retains separate, stricter criteria for independent review. ' +
        'The <a href="/about/evidence/">Evidence Register</a> documents references, not editorial sign-off.</p></section>' +
        '<section class="governance-section" id="revision-history"><span class="eyebrow">VERIFIABLE RELEASE HISTORY</span>' +
        '<h2>Selected published changes.</h2><p>This is a curated record of four previously merged major milestones, not a complete Git log. ' +
        'Dates and commit IDs refer to existing repository changes; some prior and minor changes are not individually catalogued here. ' +
        'Automated tests support reproducibility, not the historical truth of every editorial statement.</p>' +
        '<ol class="governance-revisions">' + ''.join(rows) + '</ol></section>' +
        '<section class="governance-section" id="editorial-templates"><span class="eyebrow">BLANK PLANNING DOCUMENTS</span>' +
        '<h2>Prepare a traceable editorial change.</h2>' +
        '<ul class="governance-downloads">' + worksheets + '</ul>' +
        '<p>These downloads do not submit material, appoint reviewers or create a legal or privacy agreement. ' +
        'Do not commit private reports, unpublished consent records or identifying family data to a public repository.</p></section>' +
        '<div class="governance-method"><h2>Principles we use.</h2><p>For post-publication editorial integrity, see the ' +
        '<a href="https://doi.org/10.24318/cope.2019.1.4" target="_blank" rel="noopener">COPE retraction guidelines</a> ' +
        'and <a href="https://members.publicationethics.org/sites/default/files/cope-ethics-toolkit-journal-editors-publishers.pdf" target="_blank" rel="noopener">editorial corrections toolkit</a>. ' +
        'These documents inform this independent archive\'s process; the project is not a COPE member, accredited journal or peer-reviewed publisher. ' +
        'Living testimony requires its own rights review, for which the ' +
        '<a href="/heritage/">Heritage Room</a> provides source-led planning guidance.</p>' +
        '</div></main>'
    )
