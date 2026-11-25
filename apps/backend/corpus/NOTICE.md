# Corpus notice

`chunks/who-dwm-2020-es.jsonl` holds text extracted and split from:

> En tiempos de estrés, haz lo que importa: una guía ilustrada [Doing what matters in times of
> stress: an illustrated guide]. Ginebra: Organización Mundial de la Salud; 2020. Licencia:
> CC BY-NC-SA 3.0 IGO.

Source PDF: <https://www.who.int/docs/default-source/mental-health/sh-2020-spa-3-web.pdf>
(SHA-256 `db06ef3a89220f15e9431d66a35b8754b871092fbd5415b719e00465601f5df8`).

- Licence: [CC BY-NC-SA 3.0 IGO](https://creativecommons.org/licenses/by-nc-sa/3.0/igo/deed.es).
  Non-commercial use only. Any freemium or paid use of Puente needs written permission from WHO.
- The chunks are the original text, split by page windows and cleaned of page numbers, running
  headers and illustration fragments. They are not a translation and add no content.
- This use does not imply that WHO endorses Puente or any organization, product or service. The
  WHO logo is not used.
- The raw PDF is not committed: `uv run puente-knowledge fetch` downloads it and checks its hash.

Excluded on purpose (see `docs/research/notes/fuentes_clinicas_rag.md`): the PAHO adaptation for
Latin America ("Todos los derechos reservados"), NICE NG222 (AI use not covered by its licence) and
any clinician material (dosing, diagnostic criteria), which must never reach users.
