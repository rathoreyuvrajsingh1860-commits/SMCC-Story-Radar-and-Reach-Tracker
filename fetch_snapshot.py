#!/usr/bin/env python3
"""Read a CSIR News portal page and write an ITEMS snapshot for the Story Radar prototype.

Usage:
    python fetch_snapshot.py                       # default: https://csirnews.niscpr.res.in/home/lab/1
    python fetch_snapshot.py URL [--max 12]        # another lab page
    python fetch_snapshot.py --file saved.html     # parse a page you saved by hand

Output: items.js, a JavaScript array you paste over `var ITEMS=[...]` in the prototype.
Ratings are keyword guesses. An editor should review them in the prototype ("Edit ratings").
Standard library only.
"""
import argparse, json, re, sys, urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin

DEFAULT = "https://csirnews.niscpr.res.in/home/lab/1"

class Feed(HTMLParser):
    """Collect article links (hrefs containing /home/article/) and the text that follows each."""
    def __init__(self, base):
        super().__init__()
        self.base, self.items, self.cur, self.in_a = base, [], None, False
    def handle_starttag(self, tag, attrs):
        href = dict(attrs).get("href") or ""
        if tag == "a" and "/home/article/" in href:
            self.cur = {"link": urljoin(self.base, href), "title": "", "blurb": ""}
            self.items.append(self.cur)
            self.in_a = True
    def handle_endtag(self, tag):
        if tag == "a":
            self.in_a = False
    def handle_data(self, data):
        t = " ".join(data.split())
        if not t or self.cur is None:
            return
        if self.in_a:
            self.cur["title"] = (self.cur["title"] + " " + t).strip()
        elif not self.cur["blurb"]:
            self.cur["blurb"] = t[:240]

EVENT = re.compile(r"\b(mou|award|prize|webinar|celebrat|foundation day|participat|conclave|lecture|"
                   r"inaugurat|calls? for|nominations?|exhibition|expo|campaign|festival)\b", re.I)
OUTPUT = re.compile(r"\b(develop|indigenous|patent|transfer|technology|first|launch|unveil|new)\w*", re.I)
VISUAL = re.compile(r"\b(tractor|aircraft|drone|launch|unveil|flag(s)? off|machine|vehicle|plant)\w*", re.I)
BENEFIT = re.compile(r"\b(farmer|water|health|air|drug|affordable|rural|clean|disease|food)\w*", re.I)
REGION = re.compile(r"\b(assam|andaman|lucknow|kashmir|north[- ]east|hill|rural|village|state|district)\w*", re.I)

def rate(text):
    """Return [benefit, novelty, visual, timeliness, regional], each 1 to 5."""
    if EVENT.search(text) and not OUTPUT.search(text):
        return [1, 1, 3, 3, 1]
    novelty = 5 if re.search(r"\bfirst\b|indigenous", text, re.I) else 4 if OUTPUT.search(text) else 2
    return [4 if BENEFIT.search(text) else 3, novelty, 4 if VISUAL.search(text) else 2,
            3,  # no dates in the feed, so timeliness stays neutral until an editor sets it
            4 if REGION.search(text) else 2]

def kind(text):
    if re.search(r"transfer|licen", text, re.I): return "Technology transfer"
    if re.search(r"patent", text, re.I): return "Patent"
    if EVENT.search(text): return "Event news"
    return "Announcement"

def build(html, base, limit):
    p = Feed(base); p.feed(html)
    seen, out = set(), []
    for it in p.items:
        title = it["title"]
        if not title or title.lower() in seen:
            continue
        seen.add(title.lower())
        text = title + " " + it["blurb"]
        lab = (re.search(r"CSIR-[A-Z][A-Za-z]+", text) or [None])[0] or "CSIR"
        out.append({"id": "i%d" % (len(out) + 1), "lab": lab, "kind": kind(text), "title": title,
                    "sum": it["blurb"] or "No summary on the page.", "s": rate(text), "link": it["link"]})
        if len(out) >= limit:
            break
    return out

def main():
    a = argparse.ArgumentParser()
    a.add_argument("url", nargs="?", default=DEFAULT)
    a.add_argument("--file"); a.add_argument("--max", type=int, default=12); a.add_argument("--out", default="items.js")
    args = a.parse_args()
    if args.file:
        html = open(args.file, encoding="utf-8").read()
    else:
        req = urllib.request.Request(args.url, headers={"User-Agent": "Mozilla/5.0 (story-radar prototype)"})
        html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    items = build(html, args.url, args.max)
    if not items:
        sys.exit("No article links found. Save the page from your browser and try --file saved.html.")
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("var ITEMS=[\n" + ",\n".join(json.dumps(i, ensure_ascii=False) for i in items) + "\n];\n")
    print("Wrote %d items to %s" % (len(items), args.out))

if __name__ == "__main__":
    main()
