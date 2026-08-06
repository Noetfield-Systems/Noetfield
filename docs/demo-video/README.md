# Noetfield demo film — canonical home

**Everything for the Noetfield demo commercial lives in this folder and nowhere else.**
Cuts, the recording pipeline, captions, per-prospect variants, source recordings.
Not in a factory output directory, not in a scratch build folder, not on the
Desktop, not in a chat thread. One folder, versioned, on the machine and on
GitHub. If a future session produces a Noetfield film asset anywhere else, that
copy is the mistake and gets deleted — this one is the original.

This rule is written down before the first frame exists, because the cheapest
time to decide where something lives is before there are three copies of it.

## What the film shows

The **combined** client journey, which is the thing no competitor can show:
one person orders a website **and** the automation behind it in the same
session, and gets both.

The spine, in order:

1. **The order.** One sentence, typed into the front door, asking for both.
2. **The plan answers both halves.** The page *and* the automation, before an
   account exists.
3. **The page is built** from the client's own words.
4. **The refusal.** It declines to publish a phone number it was never given.
5. **The automation is built** and announced.
6. **The email arrives.**

Beats 4 and 6 carry the film. Everything else is setup.

## Verified live, 2026-08-05

Filming was blocked until the flow genuinely worked end to end. It now does,
and each beat below was confirmed against production, not a mockup:

- **Beat 1–2 (front door).** A combined sentence for a Hamilton plumbing
  business returns a plan naming the page sections *and* a section headed
  "The automation it would add — When someone submits the form on your page, it
  would email you", plus the check "The automation is built and checked with the
  page, not promised for later". This was broken until today: the automation
  half vanished silently, and the fix, though merged, was invisible in
  production because the page still pointed at the previous cached script.
- **Beats 3, 5, 6 (signed in).** One combined order produced a real landing
  page for the business, sealed it, then fired the automation at the seal and
  announced both in chat. The generated page even tells visitors their enquiry
  is emailed with an instant confirmation — the site and the automation
  describe the same promise.
- **Beat 4 (the refusal).** The fact gate refuses to publish contact details
  the client never stated, and still refuses invented additions (an
  unrequested "Closed Sundays") even when the client's other facts are
  accepted.

## Shooting notes

- Real screen recording of the live app. No mockups, no re-creations.
- Captions only. No voiceover, no synthetic voice. Music bed.
- 60–90s master cut. Derive: square with oversized captions for LinkedIn, wide
  silent loop for the homepage, wide long-form for one-to-one outreach.
- Use a business that is obviously not a real client, and a mailbox that can be
  shown on screen.
- Timing to expect: the page lands in roughly two to four minutes and the
  automation follows after the page seals. Both are cut down in the edit — but
  film the real wait, so the cut is honest about what is compressed.
- The refusal beat needs an order that deliberately omits a phone number, so
  the page can be seen choosing a contact form over an invented number.

## Re-rendering and variants

Whatever pipeline produces the cuts is committed here alongside them, with the
command to re-render written in this file when it exists. A per-prospect
variant is a re-render from committed sources, never a hand edit of a delivered
file.
