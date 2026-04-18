# Recipe: GitHub Pages Static Site

How to go from a brief to a live, iterable site — using this template.

---

## The skills in play

| Role | What it does on this project |
|------|------------------------------|
| **Product Manager** | Reads the brief. Defines audience, goals, content structure. Decides what *not* to build. |
| **UI Designer** | Defines the design system (colours, type, spacing). Picks photos. Designs for the primary device (mobile). |
| **Engineer** | Writes the HTML/CSS/JS. Sets up Git, GitHub, Pages, branch workflow, Copilot instructions. |

One person can wear all three hats — but they should be worn *in that order*.

---

## Phase 0 — Brief

Before touching code, answer these four questions in writing:

1. **Who is the audience?** (age, device, context — e.g. "parents on their phones, showing kids")
2. **What is the one job of this page?** (inform / sell / delight / guide)
3. **What sections does it need?** (list them — these become your `#anchor` IDs)
4. **What aesthetic direction?** (one reference + palette + font pairing)

Save the answers in `SPEC.md`. This is what Copilot and future-you read first.

---

## Phase 1 — GitHub setup (15 min)

```bash
# 1. Init repo
git init && git add . && git commit -m "Initial commit"

# 2. Create GitHub repo + push
gh repo create {repo-name} --public --source=. --remote=origin --push

# 3. Enable GitHub Pages from main branch root
gh api repos/{owner}/{repo}/pages --method POST \
  --field 'source[branch]=main' \
  --field 'source[path]=/'
```

Site is live at `https://{username}.github.io/{repo-name}/` within ~60 seconds of each push to `main`.

---

## Phase 2 — Design system (define before coding)

Lock these down in `:root` CSS variables before writing a single component:

```css
:root {
  /* Palette — 4 values max */
  --bg:          ;   /* page background */
  --ink:         ;   /* primary text */
  --accent:      ;   /* primary action colour */
  --accent-bg:   ;   /* tint of accent for backgrounds */
  --card-bg:     ;   /* card surface */
  --card-border: ;   /* card border */
  --muted:       ;   /* secondary text / metadata */

  /* Typography — 3 fonts max */
  --f-display: ;   /* headings / hero */
  --f-body:    ;   /* readable prose */
  --f-mono:    ;   /* labels / metadata / dates */

  /* Shadows */
  --shadow-sm: 0 1px 4px rgba(0,0,0,.07);
  --shadow-md: 0 4px 18px rgba(0,0,0,.11);

  /* Radii */
  --r-sm:   6px;
  --r-md:   14px;
  --r-pill: 999px;
}
```

**Rule:** every colour in the site comes from these tokens. No hex codes in components.

---

## Phase 3 — Architecture (single-file static site)

Everything in one `index.html`:

```
<head>
  Google Fonts <link>
  <style> ← entire CSS: reset → tokens → layout → components → utilities </style>
</head>
<body>
  Navigation (desktop top / mobile bottom)
  Hero section
  Content sections (one per major topic/day/chapter)
  Footer
  <script> ← IntersectionObserver animations, active nav state, image loading </script>
</body>
```

**Why single file?** Zero build tools. GitHub Pages serves it instantly. Anyone can edit it.

### Mobile-first rule
Write base CSS for 375px. Add `@media (min-width: 640px)` only where needed.
Never write desktop-first and try to undo it for mobile.

### Navigation pattern
- **Mobile:** fixed bottom tab bar (thumb-reachable, emoji + label)
- **Desktop:** sticky top bar (frosted glass, `backdrop-filter: blur()`)
- Active state: `IntersectionObserver` on sections → adds `.active` class to matching nav link

### Photos (Unsplash)
Free, no attribution required. Format:
```
https://images.unsplash.com/photo-{ID}?auto=format&fit=crop&w=1400&q=80
```
Always pair with a `background-color` fallback — the site must look good if images fail.

### Scroll animations
```js
const observer = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (!e.isIntersecting) return;
    const i = [...e.target.parentElement.children]
      .filter(el => el.classList.contains('fade-up'))
      .indexOf(e.target);
    setTimeout(() => e.target.classList.add('in'), i * 75);
    observer.unobserve(e.target);
  });
}, { threshold: 0.08, rootMargin: '0px 0px -30px 0px' });

document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));
```
Add `class="fade-up"` to any element. CSS handles the animation:
```css
.fade-up            { opacity: 0; transform: translateY(20px); transition: opacity .45s ease, transform .45s ease; }
.fade-up.in         { opacity: 1; transform: none; }
```

---

## Phase 4 — GitHub Copilot instructions

Create `.github/copilot-instructions.md`. GitHub Copilot reads this automatically in VS Code and on github.com. It should contain:

- What the project is and who it's for
- The tech stack constraints ("no frameworks, single file")
- The full design system (colour tokens, type scale, component patterns)
- Copy-pasteable HTML for repeating components (cards, badges, etc.)
- PR and branch naming conventions

Wire it up in `.vscode/settings.json`:
```json
{
  "github.copilot.chat.codeGeneration.useInstructionFiles": true,
  "github.copilot.chat.codeGeneration.instructions": [
    { "file": ".github/copilot-instructions.md" }
  ]
}
```

**What this unlocks:** any future session — human or AI — can ask "add an activity card for X" and Copilot will produce code that matches the existing design system exactly.

---

## Phase 5 — PR workflow

Every change after the initial commit goes through a branch + PR:

```bash
git checkout -b feature/my-change   # or fix/ or content/
# make changes
git add . && git commit -m "describe what and why"
git push -u origin feature/my-change
gh pr create --title "..." --body "..."
```

Merge to `main` → GitHub Pages auto-deploys. ~60 seconds.

`.github/PULL_REQUEST_TEMPLATE.md` pre-fills the PR body with a checklist.
Edit the template to match your project's specific concerns.

---

## What to fork and change per project

| File | What to update |
|------|---------------|
| `SPEC.md` | Audience, goals, sections, aesthetic direction |
| `index.html` | Design tokens, fonts, section IDs, content |
| `.github/copilot-instructions.md` | Project name, audience, design system values, component patterns |
| `.github/PULL_REQUEST_TEMPLATE.md` | Checklist items relevant to your project |

Everything structural (Git workflow, navigation pattern, animation code, Unsplash photo pattern, mobile-first CSS, Copilot wiring) stays the same.

---

## Checklist for a new project

- [ ] Brief written in `SPEC.md` — audience, job, sections, aesthetic
- [ ] GitHub repo created + Pages enabled
- [ ] Design tokens locked in `:root` before any component code
- [ ] Google Fonts chosen (≤3 families)
- [ ] Section IDs decided — match nav anchors
- [ ] Mobile bottom nav + desktop top nav wired up
- [ ] Copilot instructions written with component patterns
- [ ] PR template customised for this project
- [ ] First PR merged to main — site live

---

## Time estimates (solo, with AI assistance)

| Phase | Time |
|-------|------|
| Brief + spec | 20–30 min |
| GitHub setup | 10 min |
| Design system decisions | 20–30 min |
| First full build | 60–90 min |
| Copilot instructions | 20 min |
| First round of iteration PRs | 15 min each |
