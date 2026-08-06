# Demo film — shooting script, with each claim's proof

Advisor's 80-second script, checked line by line against production on
2026-08-06. Every beat below is marked with what was actually observed, so the
film only ever claims what a stranger could reproduce. One beat has to change;
it is marked and a true replacement is given.

## Messaging locked

**Cost:** say "under a quarter per build" or "unit economics under $0.25".
Never quote the raw fraction of a cent — it anchors the buyer to a science
experiment and destroys pricing power.

*Verified:* one combined build (site + automation) recorded **$0.004009** of
model spend, and the per-project ceiling is $0.25. The claim is true with about
sixty times of headroom, which is exactly why it is safe to say.

## The beats

### 0–12s — the order · VERIFIED
> "One prompt. A website, and the automation that runs it."

Type one sentence asking for both. The plan comes back naming the page sections
**and** "The automation it would add — When someone submits the form on your
page, it would email you", plus the promise "The automation is built and checked
with the page, not promised for later". This is before an account exists.

*Was broken until 2026-08-06:* the automation half vanished silently at this
screen. Fixed and verified live.

### 12–24s — the build · VERIFIED
> "Our HDIR factory routes this to DeepSeek. It doesn't let the AI run wild. It
> bounds it, builds the site, and prepares the workflow."

The build is bounded by a budget and a task graph, and a separate checker — not
the builder — judges the result. Film the real wait: the page lands in roughly
two to four minutes. Compress in the edit, never fake the clock.

### 24–46s — the refusal · VERIFIED END TO END, THE STRONGEST BEAT
> "It didn't have the business number. So it refused to guess. It asked,
> verified the fact, and shipped safely."

Proven live, in this order, on the same project:

1. The order never gave a phone number. The published page carried **no phone
   number at all** — and a working contact form in its place, so the page is
   still useful.
2. The number was then given in chat.
3. The rebuild published it as a real click-to-call link, and the contact form
   stayed.

Both halves matter on camera: it refuses to invent, **and** it accepts the truth
the moment you give it. Invented additions are still refused after that — an
unrequested "Closed Sundays" was caught in the same lane.

### 46–70s — the automation · VERIFIED
> "Same conversation. The automation is built alongside the site, ready to
> export."

One order; the site seals first, then the automation is built and announced in
the same chat. Note the wording the advisor chose — **"ready to export"** — is
exactly right, and the next beat must stay inside it.

### 70–80s — the close · MUST CHANGE
> ~~"And it runs. A full website and working automation…"~~

**Do not film this.** Every automation this system has produced is recorded as
*generated* — a file, correct and importable. None is hosted or provisioned:
no live workflow, no webhook, no email fires on its own. Filming a form
submission producing an email would be a promise that breaks on the first
stranger who tries it.

This is not a disagreement with the advisor — it is their own positioning:
*"Phase 1 generates the workflow safely. Phase 2 (Enterprise tier) includes
hosted auto-running with vault-integrated API keys."* Only the final line of the
script drifted out of that frame.

**True replacement, same power:**

> "A full website and its automation, generated autonomously, verified
> deterministically — and it refused to invent a single fact it wasn't given.
> All for under a quarter per build. That's Agent Execution Assurance.
> Hosted auto-running ships with Enterprise."

That closes on the two things nobody else can show — the refusal and the unit
economics — and names the roadmap instead of overclaiming it.

## If you want the "and it runs" shot

It needs the workflow to be provisioned into a hosted runner, which is
configuration this system does not currently carry. That is a real piece of
work, not a filming decision. Until it exists, the honest shot is the export.

## Known cosmetic issues, harmless on camera

- A successful delivery can leave a stale failure code on its record even
  though the page published correctly; it is not shown to the customer.
- A later revision may drop the line of page copy that advertises the
  automation. If that copy matters in frame, film the automation beat before
  making further edits to the page.
