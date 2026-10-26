"""Explicit source acquisition; ordinary builds never use the network."""
import argparse
from collections import OrderedDict
from datetime import date
import hashlib
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
URL='https://ebible.org/Scriptures/eng-webbe_vpl.zip'
NAMES='GEN:Genesis|EXO:Exodus|LEV:Leviticus|NUM:Numbers|DEU:Deuteronomy|JOS:Joshua|JDG:Judges|RUT:Ruth|1SA:1 Samuel|2SA:2 Samuel|1KI:1 Kings|2KI:2 Kings|1CH:1 Chronicles|2CH:2 Chronicles|EZR:Ezra|NEH:Nehemiah|EST:Esther|JOB:Job|PSA:Psalms|PRO:Proverbs|ECC:Ecclesiastes|SOL:Song of Solomon|ISA:Isaiah|JER:Jeremiah|LAM:Lamentations|EZE:Ezekiel|DAN:Daniel|HOS:Hosea|JOE:Joel|AMO:Amos|OBA:Obadiah|JON:Jonah|MIC:Micah|NAH:Nahum|HAB:Habakkuk|ZEP:Zephaniah|HAG:Haggai|ZEC:Zechariah|MAL:Malachi|TOB:Tobit|JDT:Judith|ESG:Esther (Greek)|DNG:Daniel (Greek)|WIS:Wisdom|SIR:Sirach|BAR:Baruch|1MA:1 Maccabees|2MA:2 Maccabees|1ES:1 Esdras|PRM:Prayer of Manasses|PSX:Psalm 151|3MA:3 Maccabees|4ES:2 Esdras|4MA:4 Maccabees|MAT:Matthew|MAR:Mark|LUK:Luke|JOH:John|ACT:Acts|ROM:Romans|1CO:1 Corinthians|2CO:2 Corinthians|GAL:Galatians|EPH:Ephesians|PHI:Philippians|COL:Colossians|1TH:1 Thessalonians|2TH:2 Thessalonians|1TI:1 Timothy|2TI:2 Timothy|TIT:Titus|PHM:Philemon|HEB:Hebrews|JAM:James|1PE:1 Peter|2PE:2 Peter|1JO:1 John|2JO:2 John|3JO:3 John|JUD:Jude|REV:Revelation'
NAMES=dict(pair.split(':',1) for pair in NAMES.split('|'))
OT=set(list(NAMES)[:39]);NT=set(list(NAMES)[-27:])

def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--archive',type=Path);a=p.parse_args()
    if a.archive: archive=a.archive
    else:
        archive=ROOT.parent/'webbe-vpl.zip';archive.write_bytes(urlopen(Request(URL,headers={'User-Agent':'Mozilla/5.0'}),timeout=60).read())
    out=ROOT/'archive/bible';(out/'books').mkdir(parents=True,exist_ok=True)
    with ZipFile(archive) as z:
        raw=z.read('eng-webbe_vpl.txt');grouped=OrderedDict()
        for line in raw.splitlines(keepends=True):
            m=re.match(rb'([A-Z0-9]+) (\d+):(\d+) ',line)
            if not m:raise ValueError('Unexpected source verse format')
            grouped.setdefault(m[1].decode(),[]).append(line)
        books=[]
        for code,lines in grouped.items():
            b=b''.join(lines);path=out/'books'/f'{code}.txt';path.write_bytes(b)
            books.append(dict(code=code,name=NAMES[code],collection='Old Testament' if code in OT else 'New Testament' if code in NT else 'Deuterocanon / additional books',path='books/'+code+'.txt',sha256=sha(b),bytes=len(b),verses=len(lines)))
        for source,target in [('eng-webbe_about.htm','source-notice.htm'),('signature.txt.asc','source-signature.asc'),('haiola.css','haiola.css')]:
            (out/target).write_bytes(z.read(source))
    manifest=dict(edition='World English Bible British Edition with Deuterocanon',abbreviation='WEBBE',source=URL,source_page='https://ebible.org/bible/details.php?id=eng-webbe',retrieved='2026-10-26',licence='Public domain; World English Bible is a trademark identifying faithful copies',source_archive_sha256=sha(archive.read_bytes()),complete_text_sha256=sha(raw),complete_text_bytes=len(raw),verses=sum(b['verses'] for b in books),books=books,method='Complete verse-per-line text split by book without changing bytes. Concatenate books in manifest order to reconstruct eng-webbe_vpl.txt. Formatting, translator notes and introductions were already absent in the publisher VPL edition. The original ZIP also included equivalent XML and SQL serialisations; these redundant formats are not retained. The publisher stylesheet is retained with its notice.',signature_note='The publisher signature is retained for provenance. SHA-256 checks are performed locally; no OpenPGP signature verification is claimed.')
    manifest['supporting_files']=[dict(path=name,sha256=sha((out/name).read_bytes())) for name in ['source-notice.htm','source-signature.asc','haiola.css']]
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Retained',len(books),'books,',manifest['verses'],'verse lines and',len(raw),'source bytes')

if __name__=='__main__':main()
