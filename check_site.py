"""Check the built site for broken local destinations, incomplete metadata and leaked draft material."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re
ROOT=Path(__file__).resolve().parent
DIST=ROOT/'dist'
class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.ids=[];self.headings=0;self.title=False;self.description=False;self.images=[];self.text=[]
    def handle_data(self,data):self.text.append(data)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):self.ids.append(a['id'])
        if tag=='h1':self.headings+=1
        if tag=='title':self.title=True
        if tag=='meta' and a.get('name')=='description':self.description=bool(a.get('content'))
        if tag in ['a','link'] and 'href' in a:self.links.append(a['href'])
        if tag in ['script','img'] and 'src' in a:self.links.append(a['src'])
        if tag=='img':self.images.append(a)
issues=[];count=0
for file in DIST.rglob('*.html'):
    p=Page();text=file.read_text();p.feed(text);count+=1
    if p.headings!=1:issues.append(f'{file}: {p.headings} H1 headings')
    if not p.title or not p.description:issues.append(f'{file}: missing metadata')
    if len(set(p.ids))!=len(p.ids):issues.append(f'{file}: duplicate ids')
    for img in p.images:
        if not img.get('alt'):issues.append(f'{file}: image without alt')
    for url in p.links:
        parts=urlsplit(url)
        if parts.scheme or parts.netloc:continue
        if not parts.path:
            if parts.fragment and parts.fragment not in p.ids:issues.append(f'{file}: broken anchor {url}')
            if url=='#':issues.append(f'{file}: placeholder link')
            continue
        dest=DIST/unquote(parts.path).lstrip('/')
        if not dest.suffix:dest=dest/'index.html'
        if not dest.exists():issues.append(f'{file}: missing {url}')
    for token in ['Harshal','harshal@','Lumos','Acre Bigha','₹10k','TODO','PLACEHOLDER','Section D','GO_LIVE','internal note']:
        if token.lower() in ' '.join(p.text).lower():issues.append(f'{file}: forbidden/draft token {token}')
manifest=json.loads((ROOT/'page-manifest.json').read_text())
assert len(manifest)==53
assert len(list(DIST.glob('industries/*/index.html')))==20
assert len(list(DIST.glob('services/*/index.html')))==7
assert len(list(DIST.glob('case-studies/*/index.html')))==6
assert len(list(DIST.glob('resources/*/index.html')))==7
if issues:
    print('\n'.join(issues));raise SystemExit(1)
print(f'PASS: {count} HTML files, 52 content pages + 404, all local links/assets, heading and metadata structure, no draft/private-name leakage.')
