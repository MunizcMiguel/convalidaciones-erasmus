# Xamk: discovery notes (Phase 1, partial)

**Status: `parcial`.** The stop rule applies: the host that serves the syllabi blocks automated access. There are no course rows and there is no Phase 2.

## Degree chosen

- Xamk **does not offer Insinööri (AMK), konetekniikka** (Mechanical Engineering). It is missing from the official programme sitemaps (`sitemap-education.xml` in FI and `sitemap-education-en.xml` in EN), which list 15 Insinööri (AMK) degrees. The URL `/koulutukset/insinoori-amk-konetekniikka/` returns 404. `discover_xamk.py` checks this on every run and stops if a konetekniikka programme appears.
- The closest first-cycle degree is **Insinööri (AMK), energiatekniikka** (Energy Technology, 240 op). Its programme page lists konetekniikka, kunnossapito (maintenance) and prosessitekniikka among the subject areas, and its first years cover the basics of mechanical and electrical engineering. The other options are a worse fit. Merenkulku/laivatekniikka (marine engineering) is 270 op and tied to the maritime officer qualification. The other AMK degrees are electrical, ICT, construction or bio.
- Programme page: https://www.xamk.fi/koulutukset/insinoori-amk-energiatekniikka/. The total of 240 op is parsed from "laajuus on 240 opintopistettä".

## Sources and robots.txt

| Host | Role | robots.txt | Verdict |
|---|---|---|---|
| www.xamk.fi | Programme pages (WordPress) and sitemaps | Only `/wp-admin/` is disallowed | Allowed. Used. |
| opinto-opas.xamk.fi | Peppi study guide: curricula and course units (opintojaksot), a JS SPA with a JSON API | **403** | **Blocked.** Every path, including `/`, `/api/` and the curriculum deep links, returns a JavaScript browser check ("Tarkistetaan selainta"). The page computes a `_pk_ses` cookie in JS and then reloads. |
| opiskelija.peppi.xamk.csc.fi | Student Peppi | not checked | Requires login. Out of scope. |

The challenge is an anti-bot filter. Getting past it would mean computing the cookie or running a browser that pretends to be a person, and that would be circumventing it. The brief forbids this, so nothing beyond the challenge page was requested. The script records the verdict for each URL in `meta.notas`.

## URL patterns (for when access is allowed)

- The programme page links the curriculum in the opinto-opas as `https://opinto-opas.xamk.fi/{curriculumId}/fi/52/{programmeId}`. For energiatekniikka these are `/28/fi/52/6740` and `/30/fi/52/6740`, which are probably two curriculum years. The script strips the `_ga`/`_gl` tracking parameters.
- Peppi opinto-opas installations usually serve the course-unit structure and descriptions as JSON behind the SPA. This was not verified here because of the block.

## Traps

- PoliteClient treats a 403 on robots.txt as "no robots.txt", so the challenge itself is the signal. The script detects it and stops: it raises an error if the opinto-opas ever starts serving content, so that Phase 1 gets redone.
- The 403 answer to robots.txt is never cached, so each re-run makes that single request again. Everything else comes from `raw_cache/`.
- `curso_academico` (2026-2027) is the current year. It could not be read from the curriculum.

## Next step (for a human)

Ask Xamk for an export or for whitelisting of the study guide, for example the Peppi opinto-opas JSON or a PDF of the energiatekniikka curriculum. Alternatively, a person could download the curriculum manually through a browser.
