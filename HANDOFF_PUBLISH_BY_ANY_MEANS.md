# HANDOFF: Publish "By Any Means" to davidkirsch.me/writing

## TASK
Publish the essay "By Any Means — On hollow wills and sharp receipts" to David's personal website. Three phases: hero photo selection, HTML page creation, and deploy.

## PHASE 1 — HERO PHOTO

Discuss with David what the hero image should evoke. The essay covers: suffragist violence (Occoquan), civil rights cost-imposition (boycotts as economic warfare), the New Deal as emergency concession, voting rights gutted, global resets (France 1793, Romania 1989, Sri Lanka 2022, Bangladesh 2024, Nepal 2025), and ends with the guillotine as receipt/promise.

Photo APIs available via Oktyv vault (vault: `apis`):
- `unsplash-access-key` → Unsplash API (default image source per David's standing rule)
- `pexels-api-key` → Pexels API

Search approach: use `Oktyv:api_request` with the vault credentials. Unsplash endpoint: `https://api.unsplash.com/search/photos?query=...&per_page=20` with header `Authorization: Client-ID {key}`. Pexels endpoint: `https://api.pexels.com/v1/search?query=...&per_page=20` with header `Authorization: {key}`.

Download the chosen image, resize/crop to ~1280x853 (matching existing essays), save as `writing/img-by-any-means.jpg`. Also need an OG image (1200x630) saved as `og-by-any-means.png`.

Existing hero images for reference (examine for crop/style consistency):
- `writing/img-crazy-in-tents.jpg` — Pexels, credited
- `writing/img-through-the-overton-glass.jpg`
- Others in writing/ directory

## PHASE 2 — HTML PAGE

Create `writing/by-any-means.html` matching the EXACT template of existing essays.

### Template structure (from crazy-in-tents.html):

```
HEAD:
- <title>By Any Means — David Kirsch</title>
- meta description = subtitle
- canonical URL: https://davidkirsch.me/writing/by-any-means
- OG tags (title, description, url, image → og-by-any-means.png, 1200x630)
- Twitter card tags
- Google Fonts: JetBrains Mono
- Inline <style> block (copy from existing essay — has .essay-tags, .essay-rec, .essay-section, .sources, etc.)
- <link rel="stylesheet" href="/style.css">

BODY:
- nav (name + builds/research/writing/play links)
- back-link ← writing
- essay-tags: <a href="/writing#power">power</a> · <a href="/writing#economics">economics</a> (and possibly #investigation)
- essay-title div
- essay-subtitle div
- essay-hero div with img + credit link
- Essay body: sections use <div class="essay-section">VIII.</div> format
- Section subheading: <div class="essay-subsection">On hollow wills and sharp receipts</div>

CITATIONS — CRITICAL FORMAT:
- Inline: <sup><a href="#fn1" id="ref1" target="_self">[1]</a></sup>
- Source list at bottom in <div class="sources">:
  - <div class="sources-label">sources</div>
  - <ol class="source-list"> with <li id="fn1">...text... <a href="#ref1" target="_self">↑</a></li>
- NOTE: the existing essays use &uarr; for the up-arrow, NOT ↑ literal
- All source <li> items use <em> for book titles, &ldquo;/&rdquo; for quotes
- Links in sources use <a> tags

SHARE BLOCK:
- share-label + X (Twitter) link + LinkedIn link + copy button
- URL-encoded title and URL in share hrefs

RECOMMENDED NEXT:
- <div class="essay-rec">
- rec-label: "if this held your attention"
- Link to the previous trilogy essay: Crazy In Tents
- rec-title + rec-sub

FOOTER:
- github link + email
- Vercel analytics script
```

### Content source
The final essay markdown is at `D:\Projects\SCRVNR\by-any-means-v5.md`. Convert markdown to HTML following the exact patterns above. Key conversions:
- `### VIII.` → `<div class="essay-section">VIII.</div>` (plus subsection div for the one with a subtitle)
- `[1]` inline references → `<sup><a>` footnote links
- Straight quotes in sources → curly quotes (&ldquo; &rdquo;)
- Hyphens in essay body stay as hyphens (David's style — NOT em-dashes)
- Source list: each `[N]` becomes an `<li id="fnN">` with up-arrow back-link

### Also update:
1. **writing.html** — add new entry FIRST (newest on top), matching the exact structure:
   ```html
   <a href="/writing/by-any-means" target="_self" class="writing-item" data-tags="power economics" id="by-any-means">
     <div class="writing-title">By Any Means</div>
     <div class="writing-subtitle">On hollow wills and sharp receipts</div>
     <div class="writing-tags"><span class="writing-tag" data-tag="power">power</span> &middot; <span class="writing-tag" data-tag="economics">economics</span></div>
   </a>
   ```
2. **writing.html** — update filter counts (power, economics, all) and add subtab entries
3. **sitemap.xml** — add `<url><loc>https://davidkirsch.me/writing/by-any-means</loc></url>`

## PHASE 3 — DEPLOY

Project: `D:\Projects\davidkirsch-me`
Git: git.exe at `d:\Program Files\Git\cmd\git.exe` (lowercase d:)
Deploy: git push to GitHub → Vercel auto-deploys (no Vercel CLI)
Production URL: https://davidkirsch.me

1. Commit: `feat(writing): publish By Any Means — On hollow wills and sharp receipts`
2. Push via KERNL:git_push (project=davidkirsch-me) — NEVER shell for git push
3. Verify deployment via Vercel API
4. Check live page at https://davidkirsch.me/writing/by-any-means

## REFERENCE FILES
- Essay source: `D:\Projects\SCRVNR\by-any-means-v5.md`
- Template to copy: `D:\Projects\davidkirsch-me\writing\crazy-in-tents.html`
- Index page: `D:\Projects\davidkirsch-me\writing.html`
- Stylesheet: `D:\Projects\davidkirsch-me\style.css`
- Existing essays for pattern-matching: through-the-overton-glass.html, what-lies-beneath.html
