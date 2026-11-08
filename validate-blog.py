#!/usr/bin/env python3
"""Validate the new article and its discovery entries. No third-party packages."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
import re
import sys
import xml.etree.ElementTree as ET

class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.elements=[]
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

def validate(root, slug):
    path=root/(slug+'.html')
    text=path.read_text()
    doc=Document(text)
    expected='https://www.valenapp.tech/'+slug+'.html'
    assert len([t for t,a in doc.elements if t=='h1'])==1, 'Exactly one H1 required'
    levels=[int(t[1]) for t,a in doc.elements if re.fullmatch('h[1-6]',t)]
    assert 2 in levels, 'Article needs H2 sections'
    assert all(b<=a+1 for a,b in zip(levels,levels[1:])), 'Skipped heading level'
    canonical=[a.get('href') for t,a in doc.elements if t=='link' and a.get('rel')=='canonical']
    assert canonical==[expected], 'Canonical must match the www article URL'
    meta={a.get('name',a.get('property')):a.get('content') for t,a in doc.elements if t=='meta'}
    assert 100<=len(meta.get('description',''))<=170, 'Description length outside 100–170 characters'
    for key in ['og:title','og:description','og:image','og:url','twitter:card','twitter:title','twitter:description','twitter:image']:
        assert meta.get(key), 'Missing '+key
    assert meta['og:url']==expected
    assert meta['description']==meta['og:description']==meta['twitter:description']
    schemas=[json.loads(s) for s in re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>',text,re.S)]
    posting=next(s for s in schemas if s.get('@type')=='BlogPosting')
    assert posting['url']==expected and posting['mainEntityOfPage']['@id']==expected
    assert posting['datePublished'] and posting['author']['name']=='Valen'
    article=re.search(r'<div class="article-content[^>]*>(.*?)\n            </div>',text,re.S).group(1)
    words=len(re.findall(r"\b[\w’-]+\b",re.sub('<[^>]+>',' ',article)))
    assert 1000<=words<=1500, f'Article length: {words}'
    for tag,attrs in doc.elements:
        for key in ('href','src'):
            value=attrs.get(key)
            if not value: continue
            link=urlsplit(value)
            if link.scheme in ('mailto','tel','data'): continue
            if link.netloc and link.netloc!='www.valenapp.tech':
                assert link.scheme=='https', 'External links must use HTTPS'
                continue
            if not link.path: continue
            target=root/unquote(link.path.lstrip('/'))
            assert target.exists(), f'Missing internal target: {value}'
            if link.fragment and target.suffix=='.html':
                ids={a.get('id') for t,a in Document(target.read_text()).elements}
                assert link.fragment in ids, f'Missing anchor: {value}'
    blog=(root/'blog.html').read_text()
    assert f'href="{slug}.html"' in blog, 'Missing blog card'
    blog_schema=json.loads(re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>',blog,re.S).group(1))
    assert sum(p['url']==expected for p in blog_schema['blogPost'])==1, 'Blog schema missing or duplicated'
    tree=ET.parse(root/'sitemap.xml')
    locations=[x.text for x in tree.findall('.//{*}loc')]
    assert locations.count(expected)==1, 'Sitemap missing or duplicated'
    history=json.loads((root/'publishing-history.json').read_text())
    entries=history['entries']
    assert len({e['slug'] for e in entries})==len(entries), 'Duplicate slug in history'
    daily=[e['date'] for e in entries if e['status'] not in ('failed','aborted')]
    assert len(set(daily))==len(daily), 'Multiple articles reserved on the same IST date'
    entry=next(e for e in entries if e['slug']==slug)
    assert entry['url']==expected and entry['title']==posting['headline']
    print(f'PASS: {slug}: {words} words; headings, SEO, JSON-LD, local links/anchors, blog index, sitemap and history')

if __name__=='__main__':
    validate(Path(__file__).resolve().parent,sys.argv[1])
