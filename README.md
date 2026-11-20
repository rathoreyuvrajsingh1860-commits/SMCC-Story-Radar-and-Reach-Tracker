# SMCC Story Radar and Reach Tracker

A prototype decision-support tool for the Science Media Communication Cell (SMCC) at CSIR-NIScPR. It suggests which lab outputs deserve a story and tracks what happens after a story goes out.

Status: early prototype for discussion. It is not an official NIScPR or CSIR tool.

## What is here

| File | Purpose |
|---|---|
| `index.html` | The whole prototype: overview, Story Radar and Reach Tracker. One file, no build step. |
| `fetch_snapshot.py` | Reads a CSIR News portal page and writes an `items.js` snapshot to paste over `var ITEMS=[...]` in `index.html`. Standard library only. |

## What the prototype does

- Ranks items by a weighted newsworthiness score (public benefit, novelty, visual potential, timeliness, regional relevance). Editors set the weights and can edit each rating.
- Drafts a template brief with a suggested format, with a source link where one is available.
- Optionally drafts a fuller brief with Claude, using only the item's summary and any source text pasted in. Drafts mark gaps as `[CHECK: ...]` and list claims to verify.
- Optionally translates a brief into Hindi, Bengali, Marathi, Tamil or Telugu. Translations are machine output and need a fluent editor's check.
- Moves approved stories to a Reach Tracker where mentions and enquiries are entered by hand.
- Saves choices in the browser's local storage only.

## Running it

Open `index.html` in a browser. Everything works except the Claude drafting and translation buttons, which depend on the Claude artifact runtime (`claude.use("sample")`). Outside claude.ai those buttons show a "not available" message and the template brief still works.

To refresh the sample items:

    python fetch_snapshot.py            # default: https://csirnews.niscpr.res.in/home/lab/1
    python fetch_snapshot.py URL --max 12
    python fetch_snapshot.py --file saved.html   # if the site blocks the script

Then paste the contents of `items.js` over the `ITEMS` array in `index.html`.

## Known limits

- The six items in `index.html` are a one-time snapshot of the CSIR News portal feed, read on 20 November 2026. Ratings are provisional guesses from each blurb.
- `fetch_snapshot.py` was tested only on a small made-up page, not against the live site. It assumes article links contain `/home/article/`. Ratings it produces are keyword guesses, and timeliness stays neutral because the feed shows no dates.
- Coverage tracking is manual. Nothing finds mentions automatically yet.
- AI drafts and translations have not been evaluated for accuracy. The proposal calls for measuring faithfulness, gap flagging and edit effort before any real use.
- I found no public sign of an equivalent tool at SMCC, but internal tools are invisible from outside. Confirm with SMCC before calling this new.
- Check NIScPR's rules on ownership and approvals before sharing or publishing this work.
