"""Offline Bible fidelity, reference and generated-reader verification."""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from bible_support import load_bible,validate_passages,selected_chapters,chapter_url,reference_url
from biblical_content import ARTICLES as BIBLICAL
from content import ARTICLES as FOUNDATION
from site_config import OUT,BASE_PATH


def validate():
    bible=load_bible();manifest=bible['manifest'];articles=FOUNDATION+BIBLICAL
    validate_passages(articles)
    for item in manifest['supporting_files']:
        raw=(ROOT/'archive/bible'/item['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==item['sha256'], 'Changed publisher notice or support file'
    assert len(bible['books'])==81 and len(bible['verses'])==38058, 'Changed retained edition requires review'
    matches=bible['matches'];keys={(v['book'],v['chapter'],v['verse']) for v in matches}
    assert len(keys)==len(matches), 'Duplicate verse index entries'
    # Representative names, variant spellings and different canons must remain searchable.
    for key in [('GEN',10,11),('2KI',15,19),('ISA',20,1),('ISA',19,25),('NAH',1,1),('TOB',1,21),('JDT',1,1),('MAT',12,41),('LUK',11,32),('3MA',6,5),('4ES',13,40),('ISA',66,19)]:
        assert key in keys, f'Missing named reference: {key}'
    assert ('HEB',11,1) not in keys, 'Assurance is not Assur'
    assert ('1KI',1,17) not in keys, 'Assuredly is not Assur'
    index=json.loads((OUT/'archive/bible/concordance.json').read_text())
    assert index['entries']==matches, 'Published concordance differs from retained Scripture'
    from html.parser import HTMLParser
    class QuotedVerses(HTMLParser):
        def __init__(self):
            super().__init__();self.quote=False;self.current=None;self.in_span=False;self.values={}
        def handle_starttag(self,tag,attrs):
            attrs=dict(attrs)
            if tag=='blockquote' and attrs.get('class')=='bible-chapter-text':self.quote=True
            if self.quote and tag=='p':self.current=attrs['id'];self.values[self.current]=''
            if self.quote and tag=='span':self.in_span=True
        def handle_endtag(self,tag):
            if tag=='span':self.in_span=False
            if tag=='blockquote':self.quote=False
        def handle_data(self,text):
            if self.quote and self.in_span:self.values[self.current]+=text
    for code,c in selected_chapters(articles):
        reader=OUT/chapter_url(code,c).lstrip('/')/'index.html'
        p=QuotedVerses();p.feed(reader.read_text())
        expected={f'v-{v["verse"]}':v['text'] for v in bible['chapters'][(code,c)]}
        assert p.values==expected, f'Scripture wording changed in {code} {c}'
    for a in articles:
        if not a.get('passages'):continue
        html=(OUT/'articles'/a['slug']/'index.html').read_text()
        assert 'Biblical primary' in html or 'BIBLICAL PRIMARY' in html
        for ref in a['passages']:assert BASE_PATH+reference_url(ref) in html, f'Missing passage link in {a["slug"]}'
    maps=json.loads((ROOT/'archive/maps/assyria-atlas.json').read_text())
    for stage in maps['snapshots']:
        for p in stage.get('biblical',{}).get('passages',[]):
            relative,fragment=p['url'].split('#')
            page=(OUT/relative.lstrip('/')/'index.html').read_text()
            assert f'id="{fragment}"' in page, 'Map biblical link is broken'
    print(f'Validated exact text in {len(selected_chapters(articles))} complete chapters, {len(matches)} index entries, {len(BIBLICAL)} guides and {len(bible["books"])} preserved source books.')

if __name__=='__main__':validate()
