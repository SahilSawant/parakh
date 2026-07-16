# Parakh (परख) — Unbiased News for India

> "To assay." Reader-funded news-coverage transparency. **No ads. No grants. No owner.**

Parakh aggregates Indian news, clusters coverage of the same story across outlets, and
shows the **coverage distribution across a dual bias axis**, blindspots, factuality, and
ownership. Reading is free and anonymous forever; a single **Supporter** tier
(₹99/mo · ₹999/yr) unlocks the deep tools and cross-device sync.

We show **coverage patterns, not truth-claims.**

---

## Monorepo layout

| Path | What |
|---|---|
| `web/` | Next.js 15 (App Router, TS) PWA. Tailwind v4 mapped to the design tokens. |
| `web/styles/tokens.css` | **Design source of truth** — `--pk-*` variables, light + dark. Imported verbatim; do not hand-edit. |
| `db/migrations/` | Postgres + pgvector schema (core data model + billing). |
| `db/seed/` | Launch sources seed. |
| `worker/` | Python (FastAPI + scheduler) ingestion/ML worker skeleton. |
| `docs/` | Milestone notes. |

## Design contract (binding)

- Import `tokens.css` verbatim; map Tailwind theme to the `--pk-*` variables. **Never hardcode a hex that exists as a token.**
- Dark mode = `[data-theme="dark"]` attribute; default follows `prefers-color-scheme`, user-overridable in Settings.
- Fonts: Noto Sans, Noto Sans Devanagari, Noto Sans Mono (self-hosted, `font-display: swap`). Devanagari: same sizes, **line-height +0.15**, never letter-spaced.
- Bias bars render only at **≥5 rated outlets**; "lean" segments carry a diagonal hatch (colorblind rule); every rating chip has an ⓘ evidence popover with an always-visible dispute link.
- **Never:** saffron/orange or green semantics, red/sky-blue axis poles, tricolor adjacency, maps of India, flags. State selection is a text list grouped by zone.

## Quick start

```bash
# Web app
cd web
npm install
npm run dev        # http://localhost:3000  → /styleguide for the component gallery

# Type-check + production build
npm run typecheck
npm run build

# Database (needs a Postgres 15+ with pgvector)
psql "$DATABASE_URL" -f ../db/migrations/0001_core.sql
psql "$DATABASE_URL" -f ../db/migrations/0002_billing.sql
psql "$DATABASE_URL" -f ../db/seed/0001_sources.sql

# Ingestion worker (skeleton)
cd ../worker
python3 -m venv .venv && . .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload
```

## Status — M0 (skeleton)

- [x] Repo / CI / schema
- [x] `tokens.css` → Tailwind v4, dark mode
- [x] Font pipeline + mixed-script render test (`/mixed-script-test`)
- [x] Design-system primitives + gallery (`/styleguide`)
- [x] Core + billing schema, sources seed
- [x] Ingestion worker skeleton
- [ ] 20 sources ingesting live (M0→M1)
- [ ] `parakh.news` registration (see `docs/M0.md`)

See `docs/M0.md` for details and the roadmap to M1.
