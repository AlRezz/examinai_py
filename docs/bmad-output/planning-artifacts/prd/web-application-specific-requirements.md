# Web Application Specific Requirements

## Project-type overview

Examinai is a **multi-page, server-rendered web application** (FastAPI + Jinja2 target): authenticated users move between pages via **GET** and **POST** forms with **CSRF** on mutating requests, aligned with `docs/api-contracts.md`. The product is **not** a public marketing site or a JSON-first SPA; the browser is the client for role-specific workflows.

## Technical architecture considerations

- **MPA vs SPA:** **MPA** (full page loads / redirects, form posts). No requirement for client-side routing or a separate frontend repo in MVP.
- **Sessions & security:** Form login, session cookie, role-based URL authorization; static assets under `/css/**`, `/js/**`, `/webjars/**` as documented.

## Browser matrix

| Tier | Browsers | Notes |
|------|----------|--------|
| **Primary** | Latest **Chrome**, **Firefox**, **Safari**, **Edge** (current −1) | Pilot and local dev |
| **Baseline** | Exact “must support” list may be tightened by program IT | Document when procurement requires |

## Responsive design

- Layouts should be **usable on common laptop widths** first; **tablet/mobile** readability is desirable for coordinator/intern quick checks but **not** a native-app replacement. Bootstrap-aligned patterns per `docs/component-inventory.md` and Jinja parity.

## Performance targets

- **Page-level:** Interactive tasks (list → detail → submit) should avoid unnecessary round-trips; Git fetch and LLM calls are **explicit actions** with user-visible progress or failure (no silent long hangs without feedback).
- **Integrations:** Timeouts and retries for **Git** and **Ollama** owned by integration modules; degrade gracefully per mentor journey.

## SEO strategy

- **Minimal:** Most value is **behind login**. No reliance on public indexing for core workflows. Public/static pages (e.g. landing) may exist but are not the MVP differentiator.

## Accessibility level

- **Target:** Progress toward **WCAG 2.x** alignment on core flows (login, tasks, submission, feedback), consistent with [Domain-Specific Requirements](#domain-specific-requirements). Formal audit tier **TBD** by procurement.

## Implementation considerations

- **Templates & static files:** Mirror template names and URL structure from product docs where “same UI” is required; mount static files for CSS/JS/WebJars paths.
- **Health:** `GET /actuator/health` for operators (JSON shape agreed with ops).
- **Testing:** Per [Delivery and testing strategy](#delivery-and-testing-strategy)—**no automated browser suite** required during initial implementation; manual passes for primary browsers; automated tests in a later phase per PRD.
