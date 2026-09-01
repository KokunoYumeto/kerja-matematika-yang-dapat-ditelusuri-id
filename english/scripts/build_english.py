"""Build and check the additive English O017 reader without changing Indonesian files.

Run from the English edition root: python scripts/build_english.py [--pdf].
Only this English edition directory is written. The content build uses Quarto;
the two inherited standard-library mathematical witnesses are executed verbatim.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import ctypes
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'source'
HTML = ROOT / 'build/html'
QA = ROOT / 'qa'
PDF = ROOT / 'output/pdf/traceable-mathematical-work-en-2026.08.31.pdf'
NAMES = ['01-membaca-argumen','02-menelusuri-sumber','03-merekonstruksi-pembuktian',
         '04-sitasi-provenance-catatan-sumber','05-eksposisi-matematika',
         '06-komputasi-dapat-direproduksi','07-errata-koreksi-batas-kepastian',
         '08-seminar-penelaah-tanggapan-kritik','09-kontribusi-komunitas-portofolio']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

@contextmanager
def tex_mutex(timeout_ms=900_000):
    """Hold the machine-wide TeX slot for the complete captured build/log check."""
    if sys.platform != 'win32':
        raise RuntimeError('Global\\InterlanguageTeXSlotV1 requires Windows; refusing an unreserved TeX launch')
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.CreateMutexW(None, False, 'Global\\InterlanguageTeXSlotV1')
    if not handle:
        raise OSError(ctypes.get_last_error(), 'CreateMutexW failed')
    abandoned = False
    outcome = None
    try:
        outcome = kernel32.WaitForSingleObject(handle, timeout_ms)
        if outcome == 0x00000080:
            abandoned = True
        elif outcome != 0x00000000:
            if outcome == 0x00000102:
                raise TimeoutError('Timed out acquiring Global\\InterlanguageTeXSlotV1; no TeX process started')
            raise OSError(ctypes.get_last_error(), f'WaitForSingleObject failed: {outcome:#x}')
        yield abandoned
    finally:
        if outcome in (0x00000000, 0x00000080):
            kernel32.ReleaseMutex(handle)
        kernel32.CloseHandle(handle)

def run(command, logname, cwd=ROOT, tex=False):
    def execute():
        result = subprocess.run(command,cwd=cwd,capture_output=True,text=True,encoding='utf-8',errors='replace')
        (QA/logname).write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
        if result.returncode:
            raise RuntimeError(f'Command failed ({result.returncode}); inspect qa/{logname}')
        return result.stdout
    if not tex:
        return execute()
    error = None
    output = None
    status = 'FAIL'
    abandoned = False
    acquired = False
    started = datetime.now(timezone.utc).isoformat()
    try:
        with tex_mutex() as abandoned:
            acquired = True
            output = execute()
            status = 'PASS'
    except BaseException as caught:
        error = caught
    write_json(QA/'TEX_MUTEX_RECEIPT.json',{
        'status':status,'mutex':'Global\\InterlanguageTeXSlotV1',
        'bounded_timeout_ms':900000,'abandoned_mutex_recovered':abandoned,
        'command':command,'started_at_utc':started,
        'mutex_acquired':acquired,
        'released_after_process_tree_and_log_check':acquired,
        'error_type':type(error).__name__ if error is not None else None,
        'error':str(error) if error is not None else None})
    if error is not None:
        raise error.with_traceback(error.__traceback__)
    return output

def source_parity():
    baseline = json.loads((ROOT/'controls/INDONESIAN_BASELINE.json').read_text(encoding='utf-8'))
    baseline_checked = 0
    for row in baseline['files']:
        original = ROOT.parent / row['path']
        if original.exists():
            baseline_checked += 1
            if sha(original) != row['sha256']:
                raise RuntimeError(f'Indonesian baseline changed: {row["path"]}')
    details = []
    for number, name in enumerate(NAMES,1):
        en_path = SOURCE/'units'/f'{name}.qmd'
        if not en_path.is_file():
            raise RuntimeError(f'English unit missing: {name}')
        en = en_path.read_text(encoding='utf-8')
        original_path = ROOT.parent/'source/units'/f'{name}.qmd'
        original = original_path.read_text(encoding='utf-8') if original_path.is_file() else None
        anchors = re.findall(r'\{#([A-Za-z0-9_-]+)',en)
        if len(anchors)!=len(set(anchors)):
            raise RuntimeError(f'Duplicate English anchors: {name}')
        if original and anchors != re.findall(r'\{#([A-Za-z0-9_-]+)',original):
            raise RuntimeError(f'Anchor sequence differs: {name}')
        exercise_anchors = [a for a in anchors if re.fullmatch(fr'o017-u{number:02}-(?:x|e|ex)\d{{2}}',a)]
        guidance_anchors = [a for a in anchors if re.fullmatch(fr'o017-u{number:02}-h\d{{2}}',a)]
        if len(exercise_anchors)!=6 or len(guidance_anchors)!=6:
            raise RuntimeError(f'Exercise/guidance closure incomplete: {name}: {exercise_anchors}, {guidance_anchors}')
        details.append({'unit_id':f'O017-U{number:02}','path':en_path.relative_to(ROOT).as_posix(),
            'sha256':sha(en_path),'bytes':en_path.stat().st_size,'anchors':len(anchors),
            'exercises':6,'guidance_answers':6,'original_sha256':sha(original_path) if original else None})
    write_json(QA/'SOURCE_CLOSURE.json',{'status':'PASS','units':details,
        'unit_count':9,'exercise_count':54,'guidance_count':54,
        'indonesian_baseline_files_checked':baseline_checked,
        'indonesian_baseline_preserved':True if baseline_checked==len(baseline['files']) else None,
        'baseline_note':'External originals checked where available; standalone rebuild uses the frozen inventory, not an unperformed original-byte comparison.'})

class Document(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path=path; self.ids=set(); self.links=[]; self.lang=None
        self.math=0; self.images=[]; self.title=False; self.remote_runtime=[]
        self.feed(path.read_text(encoding='utf-8'))
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='html':self.lang=attrs.get('lang')
        if attrs.get('id'):self.ids.add(attrs['id'])
        if tag=='math':self.math+=1
        if tag=='img':self.images.append(attrs.get('alt',''))
        for field in ('href','src'):
            if attrs.get(field):
                target=attrs[field]
                self.links.append(target)
                if tag in ('script','link') and target.startswith(('http:','https:','//')):
                    self.remote_runtime.append(target)

def finish_html():
    from bs4 import BeautifulSoup
    for name in ['LICENSES.md','ENGLISH_EDITION_RIGHTS.md','THIRD_PARTY_NOTICES.md']:
        shutil.copyfile(ROOT/name,HTML/name)
    shutil.copytree(ROOT/'licenses',HTML/'licenses',dirs_exist_ok=True)
    if (ROOT/'delivery').is_dir():shutil.copytree(ROOT/'delivery',HTML/'delivery',dirs_exist_ok=True)
    style_version = sha(HTML/'styles.css')[:12]
    for path in HTML.rglob('*.html'):
        text=path.read_text(encoding='utf-8')
        text=re.sub(
            r'(href=["\'](?:\.\./)*styles\.css)(?:\?[^"\']*)?(["\'])',
            lambda match: f'{match.group(1)}?v={style_version}{match.group(2)}',
            text,
        )
        skip='<a class="o017-skip-link" href="#quarto-document-content">Skip to main content</a>'
        if skip not in text:text=re.sub(r'(<body\b[^>]*>)',lambda m:m.group(1)+'\n'+skip,text,count=1)
        text=text.replace('aria-controls="navbarCollapse" role="menu"','aria-controls="navbarCollapse"')
        text=text.replace('<nav id="TOC" role="doc-toc" class="toc-active">','<nav id="TOC" role="doc-toc" class="toc-active" aria-labelledby="toc-title">')
        text=re.sub(r'<h2 id="toc-title">([^<]+)</h2>',r'<div id="toc-title" class="h2">\1</div>',text,count=1)
        text=re.sub(r'<div class="(o017-(?:table|math)-scroll)"(?![^>]*\brole=)([^>]*)>',r'<div class="\1" role="region"\2>',text)
        text=re.sub(r'(<div class="o017-table-scroll"[^>]*aria-label="([^"]+)"[^>]*>\s*<table)(?![^>]*\baria-label=)([^>]*)>',r'\1 aria-label="\2"\3>',text)
        soup=BeautifulSoup(text,'html.parser')
        for number,table in enumerate(soup.select('main table'),1):
            heading=table.find_previous(['h1','h2','h3','h4'])
            label=f"Table {number}: {heading.get_text(' ',strip=True) if heading else 'course material'}"
            table['aria-label']=label
            for cell in table.select('thead th'):
                cell['scope']='col'
            if not table.find_parent(class_='o017-table-scroll'):
                wrapper=soup.new_tag('div',attrs={'class':'o017-table-scroll','role':'region',
                    'aria-label':label+'; horizontally scrollable','tabindex':'0'})
                table.wrap(wrapper)
        for number,math in enumerate(soup.select('main span.math.display'),1):
            if not math.find_parent(class_='o017-math-scroll'):
                wrapper=soup.new_tag('div',attrs={'class':'o017-math-scroll','role':'region',
                    'aria-label':f'Displayed mathematics {number}; horizontally scrollable','tabindex':'0'})
                math.wrap(wrapper)
        path.write_text(str(soup),encoding='utf-8')
    docs={p.resolve():Document(p) for p in HTML.rglob('*.html')}
    errors=[]; local=0; fragments=0
    for path,doc in docs.items():
        if doc.lang not in ('en','en-US','en-GB'):errors.append(f'{path.name}: language={doc.lang}')
        if doc.remote_runtime:errors.append(f'{path.name}: remote runtime {doc.remote_runtime}')
        for link in doc.links:
            url=urlsplit(link)
            if url.scheme or url.netloc or not (url.path or url.fragment):continue
            if url.path.startswith('/'):target=HTML/unquote(url.path.lstrip('/'))
            else:target=path.parent/unquote(url.path)
            target=target.resolve()
            if target.is_dir():target=target/'index.html'
            if not url.path:target=path
            local+=1
            if not target.is_file():errors.append(f'{path.relative_to(HTML)} -> missing {link}')
            elif url.fragment and target in docs:
                fragments+=1
                if unquote(url.fragment) not in docs[target].ids:errors.append(f'{path.name} -> missing fragment {link}')
        if any(not alt.strip() for alt in doc.images):errors.append(f'{path.name}: image without description')
    for css in HTML.rglob('*.css'):
        if re.search(r'(?:@import\s*|url\()["\']?https?://',css.read_text(encoding='utf-8'),re.I):
            errors.append(f'{css.name}: remote CSS runtime')
    if len(docs)!=11:errors.append(f'Expected 11 HTML pages, got {len(docs)}')
    if sum(d.math for d in docs.values())==0:errors.append('No native MathML')
    result={'status':'FAIL' if errors else 'PASS','html_pages':len(docs),
        'local_links_checked':local,'fragment_links_checked':fragments,
        'native_mathml_count':sum(d.math for d in docs.values()),'errors':errors,
        'pages':[{'path':p.relative_to(HTML).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p),
                  'language':d.lang,'mathml':d.math} for p,d in docs.items()]}
    write_json(QA/'HTML_QA.json',result)
    if errors:raise RuntimeError('HTML QA failed: '+'; '.join(errors[:8]))

def pdf_check():
    from pypdf import PdfReader
    reader=PdfReader(PDF)
    texts=[p.extract_text() or '' for p in reader.pages]
    joined='\n'.join(texts)
    errors=[]
    if any(char in joined for char in ('\ufffd','\uffff')):
        errors.append('Replacement or missing-glyph character in PDF text')
    if 'Traceable Mathematical Work' not in texts[0]:errors.append('Missing English title')
    if len(texts)<80:errors.append('Unexpectedly short complete reader')
    if any(len(t.strip())<20 for t in texts):errors.append('Nearly empty PDF page')
    for n in range(1,10):
        if f'O017-U{n:02}' not in joined:errors.append(f'Missing unit ID O017-U{n:02}')
    fonts={}
    for page in reader.pages:
        resource=page.get('/Resources',{})
        if hasattr(resource,'get_object'):resource=resource.get_object()
        for ref in resource.get('/Font',{}).values():
            font=ref.get_object();name=str(font.get('/BaseFont','unknown'))
            children=font.get('/DescendantFonts',[ref])
            child=children[0].get_object()
            desc=child.get('/FontDescriptor')
            desc=desc.get_object() if desc else {}
            fonts[name]={'embedded':any(k in desc for k in ['/FontFile','/FontFile2','/FontFile3']),
                         'to_unicode':'/ToUnicode' in font}
    if any(not x['embedded'] for x in fonts.values()):errors.append('Unembedded font')
    root=reader.trailer['/Root']
    tagged=bool(root.get('/StructTreeRoot'))
    result={'status':'FAIL' if errors else 'PASS','path':PDF.relative_to(ROOT).as_posix(),
        'bytes':PDF.stat().st_size,'sha256':sha(PDF),'pages':len(texts),'fonts':fonts,
        'tagged':tagged,'accessible_surface':'English semantic HTML',
        'page_sizes_pt':sorted({(round(float(p.mediabox.width),2),round(float(p.mediabox.height),2)) for p in reader.pages}),
        'errors':errors}
    write_json(QA/'PDF_QA.json',result)
    if errors:raise RuntimeError('PDF QA failed: '+'; '.join(errors))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pdf',action='store_true');parser.add_argument('--check-only',action='store_true')
    args=parser.parse_args();QA.mkdir(parents=True,exist_ok=True)
    source_parity()
    if not args.check_only:
        run([sys.executable,str(ROOT/'scripts/check_fonts.py'),'--write'],'font-check.log')
        mst=run([sys.executable,str(SOURCE/'code/verify_mst_uniqueness.py')],'mst-check.log')
        expected=(SOURCE/'code/expected-output.txt').read_text(encoding='utf-8').strip()
        if mst.strip()!=expected:raise RuntimeError('MST output differs from inherited witness')
        recurrence=run([sys.executable,str(SOURCE/'code/u06_recurrence_witness.py')],'recurrence-check.log')
        if recurrence.strip()!=(SOURCE/'code/u06-expected-output.txt').read_text(encoding='utf-8').strip():
            raise RuntimeError('Recurrence output differs from inherited witness')
        run(['quarto','render','--to','html'],'quarto-html.log',SOURCE)
    finish_html()
    if args.pdf:
        if not args.check_only:run(['quarto','render','--profile','pdf','--to','pdf'],'quarto-pdf.log',SOURCE,tex=True)
        pdf_check()
    print(json.dumps({'status':'PASS','units':9,'html_pages':11,'pdf_checked':args.pdf}))

if __name__=='__main__':main()
