#!/usr/bin/env python3
"""verify_bib.py [bibfile]: every entry in paper/refs.bib must have an arXiv id (eprint, or matched in
journal/url) or a DOI; its title is fetched from export.arxiv.org or api.crossref.org (3 s between calls,
cached in .cache/bib.json) and must match the bib title (normalized, difflib ratio >= 0.85).
Exit 1 on any failure (docs/guards.md 3.4)."""
import difflib, json, pathlib, re, sys, time, urllib.request
import xml.etree.ElementTree as ET

root = pathlib.Path(__file__).resolve().parents[1]
bib = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else root / "paper" / "refs.bib"
cache_f = root / ".cache" / "bib.json"
cache = json.loads(cache_f.read_text()) if cache_f.exists() else {}
ARX = re.compile(r"(\d{4}\.\d{4,5})(v\d+)?")


def entries(text):
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        i, depth = m.end(), 1
        j = i
        while j < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            j += 1
        body = text[i:j - 1]
        fields = {}
        for fm in re.finditer(r"(\w+)\s*=\s*", body):
            k, p = fm.group(1).lower(), fm.end()
            if p < len(body) and body[p] == "{":
                d, q = 1, p + 1
                while q < len(body) and d:
                    d += {"{": 1, "}": -1}.get(body[q], 0)
                    q += 1
                fields.setdefault(k, body[p + 1:q - 1])
            elif p < len(body) and body[p] == '"':
                q = body.index('"', p + 1)
                fields.setdefault(k, body[p + 1:q])
        yield m.group(2), m.group(1).lower(), fields


def norm(t):
    t = re.sub(r"[{}\\]", "", t or "").lower()
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", t)).strip()


def fetch(key):
    if key in cache:
        return cache[key]
    time.sleep(3)
    kind, ident = key.split(":", 1)
    req = urllib.request.Request(
        f"http://export.arxiv.org/api/query?id_list={ident}" if kind == "arxiv" else f"https://api.crossref.org/works/{ident}",
        headers={"User-Agent": "verify_bib/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    if kind == "arxiv":
        ns = {"a": "http://www.w3.org/2005/Atom"}
        ent = ET.fromstring(data).findall("a:entry", ns)
        title = ent[0].findtext("a:title", default=None, namespaces=ns) if ent else None
        if title and ent[0].findtext("a:id", default="", namespaces=ns).endswith("/api/errors"):
            title = None
    else:
        title = (json.loads(data)["message"].get("title") or [None])[0]
    cache[key] = title
    cache_f.parent.mkdir(exist_ok=True)
    cache_f.write_text(json.dumps(cache, indent=1))
    return title


fails, n = [], 0
for key, kind, f in entries(bib.read_text()):
    n += 1
    m = ARX.search(f.get("eprint", "")) or ARX.search(f.get("journal", "")) or ARX.search(f.get("url", ""))
    look = f"arxiv:{m.group(1)}" if m else (f"doi:{f['doi'].strip()}" if f.get("doi") else None)
    if not look:
        fails.append(f"{key}: no arXiv id or DOI"); continue
    try:
        remote = fetch(look)
    except Exception as e:  # noqa: BLE001
        fails.append(f"{key}: lookup failed for {look}: {e!r}"[:300]); continue
    if not remote:
        fails.append(f"{key}: {look} not found"); continue
    r = difflib.SequenceMatcher(None, norm(f.get("title")), norm(remote)).ratio()
    if r < 0.85:
        fails.append(f"{key}: title mismatch (ratio {r:.2f}) bib='{f.get('title')}' source='{' '.join(remote.split())}'")
print("\n".join(fails) or f"verify_bib: ok ({n} entries)")
sys.exit(1 if fails or n == 0 else 0)
