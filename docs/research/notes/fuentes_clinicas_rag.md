# Authoritative psychological/clinical sources for a Spanish (Peru) depression-support RAG corpus

Scope: candidate knowledge-base sources for a non-clinical depression support chatbot in Spanish (Peru). For each source the notes cover content, audience, license, Spanish availability and suitability for "how to act" guidance. Research date: 2026-10-16. Licensing statements were checked on publisher pages where they could be reached. Anything not confirmed on a primary page is flagged as UNCERTAIN.

General licensing note: CC BY-NC-SA 3.0 IGO (WHO's standard licence since about 2016) permits copying, redistribution and adaptation (which plausibly covers chunking, paraphrasing and translating for a RAG) for NON-COMMERCIAL purposes only. It requires attribution and the WHO disclaimer, adaptations must carry the same licence, and you may not suggest WHO endorsement. Whether a given app counts as "commercial" is a legal judgement this research could not settle; see Gaps.

## WHO mhGAP Intervention Guide v2.0 and mhGAP Community Toolkit (Spanish OPS versions, license)

### Takeaway
mhGAP-IG 2.0 exists in Spanish through PAHO, but it is a clinician-facing set of decision algorithms (assessment, medication, referral) aimed at non-specialist health workers. Its reuse terms are unclear: the 2016 English and 2017 PAHO Spanish editions show "All rights reserved", while only the related training manuals clearly carry CC BY-NC-SA 3.0 IGO. Treat it as clinician-only reference material and get permission before ingesting it.

### Cited Findings
- mhGAP-IG 2.0 is the second version (2016) of the guide. It covers "integrated management of priority MNS conditions" in non-specialist settings using clinical decision-making algorithms, and adds modules on Essential Care and Practice and on Implementation. The stated audience is doctors, nurses, other health workers and health planners/managers. Languages include Spanish. — [WHO publication page](https://www.who.int/publications/i/item/9789241549790)
- The WHO publication page shows no licence; it links to the general "Permissions and licensing" pages instead. — [WHO publication page](https://www.who.int/publications/i/item/9789241549790)
- The PAHO Spanish version 2.0 is at iris.paho.org/handle/10665.2/34071, as cited in a Colombian Ministry of Health document. — [MinSalud Colombia, guia-mhgap.pdf](https://www.minsalud.gov.co/sites/rid/Lists/BibliotecaDigital/RIDE/INEC/INTOR/guia-mhgap.pdf)
- The Spanish PAHO edition (as reproduced) reads "© Organización Panamericana de la Salud 2017. Todos los derechos reservados", and requests to reproduce or translate go to PAHO's permissions process. — [MinSalud Colombia, guia-mhgap.pdf](https://www.minsalud.gov.co/sites/rid/Lists/BibliotecaDigital/RIDE/INEC/INTOR/guia-mhgap.pdf). The iris.paho.org item page returned HTTP 403, so the licence field could not be checked directly.
- The English 2016 copyright page reportedly reads "© World Health Organization 2016. All rights reserved." — [AFRO-hosted PDF](https://www.afro.who.int/sites/default/files/2017-06/9789241549790-eng.pdf) (seen via search snippet, not opened in full)
- The WHO IRIS record for the 2017 mhGAP-IG 2.0 *training manuals* (field-test version) lists the licence as CC BY-NC-SA 3.0 IGO. — [WHO IRIS item](https://iris.who.int/items/948cf4d1-b591-4259-86b6-a759a8df743a)
- PAHO still runs mhGAP 2.0 update training in the Americas in 2026. — [PAHO news, 23-7-2026](https://www.paho.org/es/noticias/23-7-2026-jornada-actualizacion-sobre-salud-mental-mhgap-20)

### Inferences
- mhGAP-IG content such as the depression module's antidepressant dosing tables, the differential diagnosis and the self-harm assessment algorithms is clinician material. It should not be surfaced to lay users. If ingested at all, tag it `audience=clinician` and use it only for internal guardrails, for example to recognise red flags that need referral.
- The parts of mhGAP that are useful for lay guidance (psychoeducation, the "psychosocial interventions" key messages, reducing stress, staying socially active, regular activity) are better taken from the openly licensed WHO self-help products below, which say much the same thing to lay readers.

### Gaps
- mhGAP Community Toolkit (WHO, 2022, field-test version): the WHO page tried (ISBN 9789240039513) returned 404. Its licence, Spanish availability and content could not be confirmed. From prior knowledge (unverified) it targets community workers and is CC BY-NC-SA 3.0 IGO. Verify on iris.who.int.
- The exact licence field on the iris.paho.org record 10665.2/34071 is unconfirmed (403).

## WHO Doing What Matters (DWM), Self-Help Plus (SH+), Problem Management Plus (PM+), Step-by-Step: licences, Spanish availability, evidence

### Takeaway
DWM and SH+ are the strongest candidates. They are lay or facilitator self-help, ACT-based, CC BY-NC-SA 3.0 IGO on WHO's pages, and have official Spanish versions (DWM also has a PAHO Latin America adaptation with audios). PM+ has a Spanish translation and openly published WHO manuals, but it is a helper-delivered protocol. Step-by-Step has good RCT evidence for depression, but its materials are only available on request from WHO, and no Spanish version or licence was found.

### Cited Findings
**Doing What Matters in Times of Stress / "En tiempos de estrés, haz lo que importa"**
- WHO, 2020 (29 April 2020). An illustrated stress-management guide for coping with adversity, with self-help skills that take a few minutes a day. It can be used alone or with audio exercises and is for anyone experiencing stress. Licence: CC BY-NC-SA 3.0 IGO. A Spanish PDF and Spanish audio are available. — [WHO publication page](https://www.who.int/publications/i/item/9789240003927)
- Spanish WHO PDF (ISBN 9789240009561) — [copy hosted by INEE](https://inee.org/sites/default/files/resources/9789240009561-spa_0.pdf)
- PAHO "Versión adaptada para América Latina" (17 March 2022). It has eight Spanish audio files ("Prestar atención", "Poner los pies en la tierra" 1–3, "Desengancharte de pensamientos poco amables", "Ser amable con uno mismo", "Darse cuenta y poner nombre", "Dejar espacio"), with IRIS record iris.paho.org/handle/10665.2/55829. LICENCE CONFLICT: the PAHO page itself shows only "© Organización Panamericana de la Salud. Todos los derechos reservados", while a search summary claimed CC BY-NC-SA 3.0 IGO. — [PAHO page, LatAm adaptation](https://www.paho.org/es/documentos/tiempos-estres-haz-lo-que-importa-guia-ilustrada-version-adaptada-para-america-latina). The PDF's copyright page needs checking; the page footer may be a generic site notice.
- Original Spanish PAHO page — [PAHO](https://www.paho.org/es/documentos/tiempos-estres-haz-lo-que-importa-guia-ilustrada)

**Self-Help Plus (SH+)**
- WHO, 2021 (23 Sept 2021). A five-session group stress-management course for up to 30 adults, delivered by trained, supervised non-specialist facilitators with pre-recorded audio plus the DWM guide. It can be used as a first step in stepped care. Licence: CC BY-NC-SA 3.0 IGO. Spanish is available (facilitator manual and audio). WHO says it reduces psychological distress and helps prevent the onset of mental disorders. — [WHO SH+ page](https://www.who.int/publications/i/item/9789240035119)
- A Spanish SH+ is published by PAHO at iris.paho.org/handle/10665.2/57797 (seen in a search result; not opened). — [WHO IRIS SH+ item](https://iris.who.int/items/f17819a9-724f-4129-90f9-d489010fa9d5)

**Problem Management Plus (PM+)**
- The WHO generic PM+ manual for individual adults impaired by distress in communities exposed to adversity is WHO-MSD-MER-18.5. — [WHO publication page](https://www.who.int/publications/i/item/WHO-MSD-MER-18.5); [IRIS PDF](https://iris.who.int/server/api/core/bitstreams/b3f85b53-94f4-41ac-a7dc-9596d19c1b57/content)
- Spanish is listed among the PM+ manual translations, and a Spanish protocol is referenced at iris.who.int/handle/10665/259696. A Colombian team adapted the illustrations of the Spanish manual. — search summary of [Elrha blog](https://www.elrha.org/news-blogs/providing-problem-management-plus-pm-through-volunteers) and [MHPSS toolkit PM+](https://www.mhpss.net/toolkit/curated-space-for-psychological-interventions/resource/problem-management-plus-pm1) (not opened directly)
- A Group PM+ manual exists. — [WHO Group PM+](https://wkc.who.int/resources/publications/i/item/9789240008106)
- A PM+ pilot RCT in Chilean primary care is registered (NCT06988332), which matters as Latin American Spanish-language evidence. — [ClinicalTrials.gov](https://clinicaltrials.gov/study/NCT06988332)
- PM+ licence: not confirmed on a primary page in this session (see Gaps).

**Step-by-Step (WHO guided digital intervention)**
- Content: guided digital behavioural activation for depression, delivered through an illustrated story, plus slow breathing, relapse prevention and similar techniques. It was designed for cultural adaptation by changing characters while keeping the narrative generic. — [mHealth case report (Carswell et al. 2018)](https://mhealth.amegroups.org/article/view/20772/html)
- Access: the manual and training are obtained by contacting WHO at Psych_interventions@who.int, so they are not openly downloadable. — [MHPSS toolkit: Step-by-Step](https://www.mhpss.net/toolkit/curated-space-for-psychological-interventions/resource/step-by-step)
- Evidence: an RCT (PLOS Medicine 2022) of 569 Syrian refugees in Lebanon found that guided Step-by-Step lowered depression and improved functioning compared with enhanced usual care, with secondary gains in anxiety, PTSD, well-being and personal problems maintained at 3 months. Attrition at 3 months was 54% in the intervention arm and 38% in control. A parallel trial in Lebanese and other residents showed similar results, and Lebanon's National Mental Health Programme scaled it up. — [WHO EMRO news](https://www.emro.who.int/mnh/news/who-digital-mental-health-intervention-effective-in-reducing-depression-among-syrian-refugees-in-lebanon.html); [Elrha summary](https://elrha.org/researchdatabase/step-by-step-who-digital-mental-health-intervention-effective-in-reducing-depression-among-syrian-refugees-in-lebanon); [Mental Elf critique](https://www.nationalelfservice.net/populations-and-settings/refugee/step-by-step-promising-digital-app-for-syrian-refugees-with-depression/); [PMC article](https://pmc.ncbi.nlm.nih.gov/articles/PMC11170045)

### Inferences
- DWM (lay-facing, short skills: grounding, unhooking, acting on values, being kind, making room) is the best fit for "how to act" chunks. Its tone is non-clinical and non-diagnostic. Use the WHO Spanish edition (clearly CC BY-NC-SA 3.0 IGO) as the primary text. Use the PAHO LatAm adaptation only once its licence is confirmed, because its "todos los derechos reservados" page notice conflicts with the claim.
- DWM and SH+ target stress and distress, not depression specifically. Step-by-Step's behavioural activation content is the most depression-specific but is not openly licensed or available in Spanish. Behavioural activation guidance in Spanish may have to be written in-house, based on cited evidence, or come from the PM+ "Behavioural activation / Get going, keep doing" module once its licence is confirmed.
- PM+ manuals are written for helpers (scripts, sessions, risk assessment steps). Lay "how to act" chunks can be adapted from them (managing stress through slow breathing, problem solving, behavioural activation, strengthening social support), but the helper-instructions and risk-assessment sections should be tagged `audience=helper`.
- All of these are NC licences. A commercial or freemium deployment would need written permission from WHO/PAHO.

### Gaps
- PM+ licence: the WHO page tried (WHO-MSD-MER-16.2) gave 404. The licence of WHO-MSD-MER-18.5 and of the Spanish edition was not seen on a primary page. It is likely CC BY-NC-SA 3.0 IGO (WHO standard), but this is UNCERTAIN.
- Step-by-Step: no Spanish version, no public licence, and no independent replication in Latin America was found.
- The licence on the PDF of the PAHO DWM LatAm adaptation is unresolved.
- The Step-by-Step cost-effectiveness results were not retrieved.

## WHO/PAHO Psychological First Aid (Spanish), WHO "Preventing suicide: a resource" series, LIVE LIFE

### Takeaway
The WHO PFA field-worker guide exists in Spanish, but it is marked "all rights reserved" (2011/2012) and is aimed at crisis helpers, so it fits guardrail and escalation logic better than lay self-help chunks. LIVE LIFE has an official PAHO Spanish edition under CC BY-NC-SA 3.0 IGO, but it is a policy and implementation guide for countries, not user-facing.

### Cited Findings
- "Primera ayuda psicológica: guía para trabajadores de campo" (WHO, War Trauma Foundation, World Vision; 2011/2012; Spanish edition 62 pp.) covers humane, supportive, practical help for people in serious crisis. Search results indicate all rights reserved, with no open licence. — [WHO Spanish page](https://www.who.int/es/publications/i/item/9789241548205); [PAHO page](https://www.paho.org/es/node/44399) (licence wording UNCERTAIN; not opened directly)
- LIVE LIFE (WHO 2021, 142 pp., ISBN 9789240026629) covers four interventions: limiting access to means, responsible media reporting, socio-emotional life skills for youth, and early identification, assessment, management and follow-up of people affected by suicidal behaviour. It also has six cross-cutting pillars. — [WHO LIVE LIFE](https://www.who.int/publications/i/item/9789240026629)
- Spanish edition: "Vivir la vida. Guía de aplicación para la prevención del suicidio en los países", PAHO 2021, DOI 10.37774/9789275324240, CC BY-NC-SA 3.0 IGO, with a disclaimer that PAHO is not responsible for translation accuracy. — [medbox copy](https://www.medbox.org/document/live-life-an-implementation-guide-for-suicide-prevention-in-countries); [PAHO page (EN)](https://www.paho.org/en/documents/live-life-implementation-guide-suicide-prevention-countries) (taken from a search summary; verify on iris.paho.org)

### Inferences
- PFA's "Look, Listen, Link" (Observar, Escuchar, Conectar) principles are a good basis for the chatbot's own conversational behaviour policy, such as how to respond to someone in acute distress. Without a licence, though, paraphrase the principles in your own words with citation rather than ingesting the verbatim text. Peru's MINSA PFA guide (below) may be a cleaner source legally.
- LIVE LIFE suits a design or safety-policy reference (for example safe-messaging principles) more than RAG chunks for users.

### Gaps
- WHO "Preventing suicide: a resource for…" series (media professionals, primary health care workers, etc.): Spanish availability and licences were not checked in this session. From memory, several older editions (2000s) exist in Spanish as "Prevención del suicidio: un instrumento para…". UNCERTAIN.
- The PFA licence was not confirmed on a primary page.

## NICE NG222, behavioural activation and CBT self-help (NHS/Every Mind Matters, CCI Australia, MoodGYM)

### Takeaway
NICE explicitly excludes AI use from its open content licence, requires written permission and a signed licence (with a fee for international use), so NG222 should not be ingested without a NICE agreement. CCI worksheets are copyright Government of Western Australia, with personal use only and no reproduction without express permission. Both are unsuitable for ingestion without permission and can at most inform in-house writing.

### Cited Findings
- "Requests to use our content for artificial intelligence (AI) purposes in the United Kingdom and internationally are not covered by the terms of this licence." — [NICE UK Open Content Licence](https://www.nice.org.uk/reusing-our-content/nice-uk-open-content-licence)
- NICE content cannot be used for AI purposes without written permission from NICE backed by a signed licence agreement. Requests go through an approval process, licensing arrangement and fee (international). — [NICE: Use of our content for AI purposes](https://www.nice.org.uk/reusing-our-content/use-of-our-content-for-ai-purposes); [AI permission form](https://nice.org.uk/forms/permission-to-use-nice-content-for-artificial-intelligence-ai-purposes)
- Outside the UK, non-AI reuse is generally subject to a fee and licensing agreement, except for personal research and study. — [NICE: Use internationally](https://www.nice.org.uk/reusing-our-content/use-of-our-content-internationally)
- CCI: copyright resides with the State of Western Australia. Download is allowed solely for personal use. Materials "may not be published, or reproduced in any material form whatsoever, without the express permission of the Centre for Clinical Interventions". Apps, AI, adaptation and translation are not addressed separately. — [CCI Copyright & Disclaimer](https://www.cci.health.wa.gov.au/Utilities/Copyright-and-Disclaimer)

### Inferences
- NG222 is also clinician-oriented (stepped care, drug choice, severity thresholds). Even with a licence, most of it would be tagged `audience=clinician`.
- CCI "Back from the Bluez" and similar modules are excellent lay CBT and behavioural activation content, but they need a written permission request to CCI. They are English only, so translation would also need permission.

### Gaps
- NHS / Every Mind Matters: licence terms were not checked. NHS.UK content is often under the Open Government Licence with syndication terms, but Every Mind Matters (OHID) terms and any AI clauses are UNCERTAIN.
- MoodGYM (ANU / e-hub Health): not checked. It is believed to be a proprietary, subscription-based product, so it is likely not licensable for a RAG corpus. UNCERTAIN.
- No openly licensed Spanish behavioural activation self-help workbook was found in this session.

## Peruvian MINSA materials (GPC depresión, self-care, Guía técnica de PAP): availability and reuse terms

### Takeaway
MINSA has a 2023 depression GPC (RM 136-2023/MINSA) for adults at the first level of care, plus a "friendly" plain-language version, and a Technical Guide for PFA (RM 476-2020-MINSA). Peruvian copyright law (DL 822, art. 9) excludes official legislative, administrative and judicial texts from protection, with a duty to respect the text and cite the source. Whether ministerial technical guides count as "textos oficiales" is legally arguable rather than settled.

### Cited Findings
- "Guía de práctica clínica para el tamizaje, diagnóstico y tratamiento de la depresión en personas mayores de 18 años desde el primer nivel de atención", approved by RM N° 136-2023/MINSA. Its application is mandatory in MINSA facilities and it is a reference for EsSalud and others. — [ConsultorSalud](https://consultorsalud.com/minsa-publica-guia-clinica-depresion-en-peru/); [PDF copy](https://consultorsalud.com/wp-content/uploads/2024/01/Guia-clinica-para-el-diagnostico-y-tratamiento-de-la-depresion-.pdf); [El Peruano](https://busquedas.elperuano.pe/dispositivo/NL/2560638-1) (which El Peruano entry matches the RM was not confirmed)
- MINSA also published a "versión amigable" of the depression GPC, described as easy to read for health staff and the general public. — [Andina](https://andina.pe/agencia/noticia-minsa-publica-version-amigable-de-guia-practica-clinica-depresion-970295.aspx)
- "Guía Técnica de Primeros Auxilios Psicológicos", approved by RM N° 476-2020-MINSA and published in El Peruano on 9 July 2020. — [LP Derecho](https://lpderecho.pe/ministerio-salud-aprueban-guia-tecnica-primeros-auxilios-psicologicos-resolucion-ministerial-476-2020-minsa/); [El Peruano](https://busquedas.elperuano.pe/dispositivo/NL/1870362-3)
- DL 822 art. 9(b): official legislative, administrative or judicial texts, and their official translations, are not protected, "sin perjuicio de la obligación de respetar los textos y citar la fuente". — [LP Derecho, DL 822 updated](https://lpderecho.pe/ley-sobre-derecho-autor-decreto-legislativo-822-actualizada/); [WIPO Lex](https://www.wipo.int/wipolex/en/legislation/details/18762)
- In Res. 0294-2009/TPI-INDECOPI, INDECOPI held that an APCI work was NOT an official text because it contained no information binding on the public. That suggests the test is whether the content is normative and binding. — [CERLALC jurisprudence PDF](https://cerlalc.org/wp-content/uploads/dar/jurisprudencia/2188.pdf)

### Inferences
- A GPC or technical guide approved by Resolución Ministerial and binding on facilities plausibly qualifies as an official administrative text, which supports reuse with citation and verbatim fidelity. A MINSA brochure or "versión amigable" with no binding force might not qualify. Legal confirmation is recommended.
- The GPC is clinician-facing (PHQ-9 screening thresholds, diagnosis, pharmacotherapy). Only its patient-information or psychoeducation parts, and the "versión amigable", are lay-suitable. The PFA technical guide is a strong Peru-specific source for crisis-response behaviour and local referral pathways (Línea 113 opción 5, Centros de Salud Mental Comunitarios), but those details must be verified against current MINSA sources.

### Gaps
- Whether INSM "Honorio Delgado – Hideyo Noguchi" took part in the GPC was not confirmed.
- MINSA self-care materials (cartillas de autocuidado, bvs.minsa.gob.pe) were not catalogued in this session.
- The friendly version's URL on gob.pe was not retrieved.

## Risks: content that should NOT be in a lay RAG, and audience tagging

### Takeaway
Separate the corpus by audience at ingestion time. Lay self-help (DWM, SH+ participant content, MINSA "versión amigable") is retrievable for users. Helper and clinician material (mhGAP-IG, GPC, PM+ helper scripts, NG222) is either excluded or kept in a guardrail-only index that never surfaces verbatim to users.

### Cited Findings
- mhGAP-IG is built on clinical decision algorithms for health workers. — [WHO mhGAP-IG 2.0](https://www.who.int/publications/i/item/9789241549790)
- The MINSA GPC covers screening, diagnosis and treatment at the first level of care. — [ConsultorSalud](https://consultorsalud.com/minsa-publica-guia-clinica-depresion-en-peru/)
- SH+ and DWM target adults experiencing stress and are explicitly designed for non-specialist delivery or self-use. — [WHO SH+](https://www.who.int/publications/i/item/9789240035119); [WHO DWM](https://www.who.int/publications/i/item/9789240003927)

### Inferences
- Exclude from user-facing retrieval:
  - medication names, doses, titration and switching
  - diagnostic criteria and algorithms, and severity cut-offs used to label users
  - helper scripts for suicide risk assessment
  - lethality or method information (in line with LIVE LIFE means-restriction and media guidance)
  - contraindications and differential diagnosis
- Suggested chunk metadata:
  - `audience` (lay / helper / clinician)
  - `source_id`
  - `licence` (e.g. CC-BY-NC-SA-3.0-IGO, all-rights-reserved, official-text-PE)
  - `language_variant` (es-419, es-PE, es-ES)
  - `content_type` (skill / psychoeducation / crisis / referral / dosing / diagnostic)
  - `risk_level`
  - `requires_attribution_text`
  - `adaptation_flag` (a translated or adapted chunk must carry the "not created by WHO" disclaimer under CC BY-NC-SA IGO)
- Retrieval should filter to `audience=lay` and exclude `content_type in {dosing, diagnostic}` before generation. Crisis and referral chunks should come from Peru-specific, verified sources.

### Gaps
- No published standard for audience-tagging mental-health RAG corpora was found in this session.
