"""Turn YouTube auto-caption VTT (rolling, duplicated lines) into a readable transcript."""
import html, re, sys

def parse(path):
    out, last = [], ""
    ts = None
    for line in open(path, encoding="utf-8-sig"):
        line = line.rstrip("\n")
        m = re.match(r"(\d+):(\d\d):(\d\d)\.\d+ -->", line)
        if m:
            ts = int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3])
            continue
        if not line.strip() or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
            continue
        text = html.unescape(re.sub(r"<[^>]+>", "", line)).replace("\ufeff", "").strip()
        if not text or text == last:
            continue
        # rolling captions repeat the previous line as a prefix
        if last and text.startswith(last):
            text = text[len(last):].strip()
        last = html.unescape(re.sub(r"<[^>]+>", "", line)).strip()
        if text:
            out.append((ts, text))
    return out

def render(items, minutes=2):
    paras, cur, start = [], [], None
    for ts, text in items:
        if start is None:
            start = ts
        cur.append(text)
        if ts - start >= minutes * 60 and text.rstrip().endswith((".", "?", "!")) or ts - start >= minutes * 90:
            paras.append((start, " ".join(cur)))
            cur, start = [], None
    if cur:
        paras.append((start, " ".join(cur)))
    def clean(t):
        t = re.sub(r"\[(music|applause|laughter)\]", "", t, flags=re.I)
        t = re.sub(r"(\s*>>\s*)+", "\n\n>> ", t)  # >> marks a speaker change
        return re.sub(r" +", " ", t).strip()
    return "\n\n".join(f"[{s//3600}:{s%3600//60:02d}:{s%60:02d}] {clean(t)}" for s, t in paras)

if __name__ == "__main__":
    print(render(parse(sys.argv[1])))
