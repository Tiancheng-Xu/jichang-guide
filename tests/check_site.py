from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,csv,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];SITE=ROOT/'site';data=json.loads((ROOT/'data/services.json').read_text())
class Document(HTMLParser):
 def __init__(self,text):
  super().__init__();self.links=[];self.ids=[];self.h1s=0;self.canonical=[];self.descriptions=[];self.label_names=[];self.scripts=[];self.current=None;self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if a.get('id'):self.ids.append(a['id'])
  if tag=='h1':self.h1s+=1
  if tag in ['a','link'] and a.get('href'):self.links.append(a['href'])
  if tag=='script' and a.get('src'):self.links.append(a['src'])
  if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a['href'])
  if tag=='meta' and a.get('name')=='description':self.descriptions.append(a.get('content'))
  if tag=='script':self.current={'type':a.get('type'),'text':''};self.scripts.append(self.current)
 def handle_data(self,s):
  if self.current is not None:self.current['text']+=s
 def handle_endtag(self,tag):
  if tag=='script':self.current=None
pages={p.relative_to(SITE).as_posix():Document(p.read_text()) for p in SITE.rglob('*.html')}
for name,doc in pages.items():
 assert doc.h1s==1,(name,doc.h1s)
 assert len(doc.ids)==len(set(doc.ids)),name
 assert len(doc.canonical)==1 and len(doc.descriptions)==1,name
 for script in doc.scripts:
  if script['type'] in ['application/ld+json','application/json']:json.loads(script['text'])
 for link in doc.links:
  u=urlsplit(link)
  if u.scheme or not u.path and not u.fragment:continue
  target=SITE/unquote(u.path.lstrip('/')) if u.path else SITE/name
  if target.is_dir():target=target/'index.html'
  assert target.is_file(),(name,link)
  if u.fragment:assert u.fragment in pages[target.relative_to(SITE).as_posix()].ids,(name,link)
source=(SITE/'index.html').read_text()
for s in data['services']:
 # HTML escapes query separators; parser recovers the exact original href.
 assert s['url'] in pages['index.html'].links,s['name']
 assert s['name'] in source
assert len(list(csv.DictReader((SITE/'data/plans.csv').open())))==53
assert json.loads((SITE/'data/services.json').read_text())==data
sitemap_urls={node.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text for node in ET.fromstring((SITE/'sitemap.xml').read_text())}
expected_urls={doc.canonical[0] for name,doc in pages.items() if name!='404.html'}
assert sitemap_urls==expected_urls,(sitemap_urls,expected_urls)
for p in SITE.rglob('*'):
 if p.is_file():
  s=p.read_text();assert not re.search(r'\b[0-9]{5,12}@qq\.com\b',s),p
  assert not any(x in s for x in ['\u9080\u8bf7','\u5f15\u6d41','\u63a8\u5e7f']),p
assert all(s['type'] in ['application/json','application/ld+json','module'] for s in pages['index.html'].scripts)
print(f'PASS: {len(pages)} HTML pages, canonical/description/JSON-LD, local routes, 8 exact outbound URLs, 53 CSV plans, sitemap and privacy checks.')
