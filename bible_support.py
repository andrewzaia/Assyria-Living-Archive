"""Offline Bible preservation, concordance and reference helpers."""
from collections import defaultdict
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent
ALIASES={
 'Assyria / Assyrians':r'\bAssyria(?:ns?|n)?\b',
 'Asshur / Assur':r'\b(?:Asshur|Assur)\b',
 'Asshurim / Asshurites (check identity)':r'\b(?:Asshurim|Asshurites)\b',
 'Nineveh / Ninevites':r'\b(?:Nineveh|Ninevah|Ninevites|Ninevite)\b',
 'Nimrod':r'\bNimrod\b',
 'Calah / Resen / Rehoboth Ir':r'\b(?:Calah|Resen|Rehoboth[ -]Ir)\b',
 'Pul':r'\bPul\b',
 'Tiglath Pileser / Tilgath Pilneser':r'\b(?:Tiglath[ -]?Pileser|Tilgath[ -]?Pilneser)\b',
 'Shalmaneser / Salmananser / Enemessar':r'\b(?:Shalmaneser|Salmananser|Enemessar)\b',
 'Shalman (identity uncertain)':r'\bShalman\b',
 'Sargon':r'\bSargon\b',
 'Sennacherib / Sennacherim':r'\b(?:Sennacherib|Sennacherim)\b',
 'Esar Haddon / Sarchedonus':r'\b(?:Esar[ -]?Haddon|Sarchedonus)\b',
 'Osnappar / Asnappar':r'\b(?:Osnappar|Asnappar)\b',
 'Rabshakeh / Tartan / Rab-saris (check context)':r'\b(?:Rabshakeh|Tartan|Rab[ -]?saris)\b',
 'Holofernes':r'\bHolofernes\b',
}

@lru_cache(maxsize=1)
def load_bible():
    folder=ROOT/'archive/bible'
    manifest=json.loads((folder/'manifest.json').read_text())
    verses={};chapters=defaultdict(list);matches=[];complete=hashlib.sha256()
    for book in manifest['books']:
        raw=(folder/book['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=book['sha256']:raise ValueError('Bible source hash changed: '+book['code'])
        complete.update(raw)
        for line in raw.decode('utf-8').splitlines():
            m=re.fullmatch(r'([A-Z0-9]+) (\d+):(\d+) (.*)',line)
            if not m:raise ValueError('Unexpected Bible verse')
            code,c,v,text=m[1],int(m[2]),int(m[3]),m[4]
            key=(code,c,v)
            if key in verses:raise ValueError('Duplicate Bible reference')
            item=dict(book=code,book_name=book['name'],chapter=c,verse=v,text=text,collection=book['collection'])
            verses[key]=item;chapters[(code,c)].append(item)
            terms=[name for name,pattern in ALIASES.items() if re.search(pattern,text,re.I)]
            if terms:matches.append(dict(item,terms=terms))
    if complete.hexdigest()!=manifest['complete_text_sha256']:raise ValueError('Bible text reconstruction hash differs')
    if len(verses)!=manifest['verses']:raise ValueError('Bible verse count differs')
    return dict(manifest=manifest,verses=verses,chapters=chapters,matches=matches,books={b['code']:b for b in manifest['books']})

def chapter_url(book,chapter):return f'/bible/read/{book.lower()}/{chapter}/'
def reference_url(ref):return chapter_url(ref[0],ref[1])+f'#v-{ref[2]}'
def reference_label(ref):
    book,chapter,first,last=ref
    return f'{load_bible()["books"][book]["name"]} {chapter}:{first}'+(f'-{last}' if last!=first else '')

def validate_passages(articles):
    bible=load_bible()
    for article in articles:
        for book,chapter,first,last in article.get('passages',[]):
            if first>last:raise ValueError('Reversed reference')
            for verse in range(first,last+1):
                if (book,chapter,verse) not in bible['verses']:raise ValueError(f'Missing verse {book} {chapter}:{verse} in {article["slug"]}')


def selected_chapters(articles):
    bible=load_bible();selected={(v['book'],v['chapter']) for v in bible['matches']}
    selected.update((p[0],p[1]) for a in articles for p in a.get('passages',[]))
    order={b['code']:i for i,b in enumerate(bible['manifest']['books'])}
    return sorted(selected,key=lambda k:(order[k[0]],k[1]))
