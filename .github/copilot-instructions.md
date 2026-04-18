# Copilot Instructions — [PROJECT NAME]

## What this is
[One sentence describing the project and its audience.]

Hosted on GitHub Pages at https://[username].github.io/[repo-name]/.

**Audience:** [Who uses this? How? On what device?]

---

## Stack — keep it simple
- **Single file:** everything in `index.html` — CSS in `<style>`, JS in `<script>`
- **No build tools, no frameworks, no npm**
- **Google Fonts only** as external dependency
- **Unsplash** for open-source photography (free, no attribution required)
- **GitHub Pages** compatible — no server-side code, relative paths only

---

## Design system

### Colour tokens
```css
--bg:          [VALUE]   /* page background */
--ink:         [VALUE]   /* primary text */
--accent:      [VALUE]   /* primary action colour */
--accent-bg:   [VALUE]   /* tint of accent */
--hi:          [VALUE]   /* highlight / tag colour */
--card-bg:     [VALUE]   /* card surface */
--card-border: [VALUE]   /* card border */
--muted:       [VALUE]   /* metadata, labels */
```

### Typography
| Role | Font | Usage |
|------|------|-------|
| Display | [Font] | Hero title, section headings |
| Body | [Font] | Descriptions, notes |
| UI | [Font] | Card titles, buttons, nav |
| Mono | [Font] | Tags, dates, metadata |

### Card colour rails
Left-edge 4px bar signals category:
- `rail-accent`  → [category]
- `rail-green`   → [category]
- `rail-blue`    → [category]
- `rail-hi`      → [category]

### Badges
```html
<span class="badge badge-accent">[Label]</span>
<span class="badge badge-free">Free</span>
<span class="badge badge-warn">⚠️ Warning</span>
<span class="badge badge-book">Book ahead</span>
```

---

## Content structure

### Section IDs
| ID | Description |
|----|-------------|
| `#section-one` | [What this section covers] |
| `#section-two` | [What this section covers] |

### Adding a new card
```html
<article class="card fade-up">
  <div class="rail rail-accent"></div>
  <div class="card-inner">
    <span class="card-emoji" aria-hidden="true">🎯</span>
    <div class="card-body">
      <div class="card-row1">
        <h3 class="card-title">Title</h3>
        <div class="badges"><span class="badge badge-free">Free</span></div>
      </div>
      <p class="card-desc">Description.</p>
      <div class="card-meta"><span>🕐 Hours</span></div>
      <div class="card-actions">
        <a href="URL" target="_blank" rel="noopener" class="btn btn-primary">📍 Map</a>
      </div>
    </div>
  </div>
</article>
```

### Section chapter headers
Each section opens with a full-width photo header. Add a class to `.chapter-header`:
```css
.ch-section-one {
  background-color: #1A2030; /* fallback — always keep */
  background-image: url('https://images.unsplash.com/photo-{ID}?auto=format&fit=crop&w=1400&q=80');
}
```

---

## Conventions
- **Mobile-first:** 375px base, `@media (min-width: 640px)` for larger screens
- **Animations:** `.fade-up` class + `IntersectionObserver` adds `.in`
- **External links:** always `target="_blank" rel="noopener"`
- **Accessibility:** sections use `aria-labelledby` pointing to `h2`; backgrounds use `role="img" aria-label="..."`
- **No JS libraries** — vanilla only
- **No inline hex values** — all colours from CSS tokens

---

## PR workflow
- Branch: `feature/`, `fix/`, `content/`
- One logical change per PR
- Merge to `main` → auto-deploys (~60 seconds)
