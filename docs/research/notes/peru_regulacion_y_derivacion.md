# Peru: legal, institutional and referral context for a digital mental-health support app

Research date: 2026-10-16. Method: web search plus fetches of law-firm and press pages. Most gob.pe pages could not be fetched directly (gob.pe/10942 returned HTTP 418), so several "official" claims rest on search-result snippets of gob.pe or on secondary sources that cite MINSA. Each item says which kind of source it rests on.

## Official crisis and mental-health lines in Peru

### Takeaway
MINSA's Línea 113, option 5 is the national free mental-health line. Several press sources say it runs 24/7 and offers listening, orientation and referral to health facilities and CSMCs. For emergencies the main numbers are SAMU 106, PNP 105, Bomberos 116 and Línea 100 (MIMP, violence). A unified 911 is being piloted in Lima/Callao in 2026. I found no separate official national suicide-prevention hotline other than 113 option 5.

### Cited Findings
- Línea 113, option 5: mental-health professionals give free care to Peruvian and foreign callers, 24 hours a day, every day of the year. It can be dialled from a landline or mobile anywhere in the country — [Panamericana (MINSA reminder)](https://panamericana.pe/salud/463661-minsa-recuerda-linea-113-brinda-orientacion-apoyo-psicologico-gratuito-24-horas)
- Scope of 113-5: listening and orientation for people with symptoms such as persistent sadness, loss of interest, tiredness, and sleep or appetite changes. It can refer callers to health facilities or Centros de Salud Mental Comunitarios. It is orientation, not treatment — [Andina](https://andina.pe/agencia/noticia-linea-113-recibio-mas-135000-llamadas-relacionadas-orientacion-salud-mental-1013087.aspx); [Andina 2025](https://andina.pe/agencia/noticia-linea-113-del-minsa-mas-60000-personas-recibieron-orientacion-psicologica-gratuita-1048068.aspx)
- Demand: Línea 113 handled 135,066 mental-health-related calls in 2024 — [Andina](https://andina.pe/agencia/noticia-linea-113-recibio-mas-135000-llamadas-relacionadas-orientacion-salud-mental-1013087.aspx). More than 45,000 mental-health teleorientations in 2023 — [ConsultorSalud](https://consultorsalud.com/minsa-brinda-mas-de-45-000-teleorientaciones). These two figures measure different things (calls vs. teleorientations), so they should not be compared directly.
- Línea 113 also covers obstetrics guidance and women affected by violence (other options) — [Panamericana](https://panamericana.pe/locales/397067-linea-113-ofrece-orientacion-gratuita-salud-mental-obstetricia-mujeres-victimas-violencia)
- Emergency numbers listed in a June 2026 article: 105 Policía Nacional del Perú, 116 Bomberos, 106 SAMU (mobile emergency medical care), and Línea 100 of the Ministerio de la Mujer y Poblaciones Vulnerables (family and sexual violence). The same article says 911 has started operating in a test phase as a single emergency number in Lima Metropolitana and Callao — [Infobae, 26 Jun 2026](https://www.infobae.com/peru/2026/06/26/numeros-de-emergencia-en-peru-cuando-llamar-a-la-policia-bomberos-samu-linea-100-y-911/)
- The 911 project is planned to unify 105, 116, 100 and 106 — [Panamericana](https://panamericana.pe/24horas/nacionales/397941-linea-911-central-unica-emergencias-integrada-pnp-bomberos-samu); [DPL News](https://dplnews.com/?p=88379)
- Línea 100 is described as free, 24/7 and confidential — [TherapyRoute](https://www.therapyroute.com/article/suicide-hotlines-and-crisis-lines-in-peru-by-therapyroute) (secondary aggregator)
- WhatsApp and "Teleatiendo" channels are mentioned only by a third-party site — [tramitesperu.com](https://tramitesperu.com/minsa/salud-mental/). Not verified officially.

### Inferences
- In the app, 113 option 5 should be the main "talk to someone now" referral. 106 (SAMU), or 105/911 where 911 is live, should be the imminent-risk route. Línea 100 should be offered when violence is disclosed.
- 911 is still a pilot, so the app should not rely on it alone. Show 106 and 105 alongside it.

### Gaps
- I could not fetch an official gob.pe or minsa.gob.pe page confirming the current hours of 113-5 in 2026. The 24/7 claim comes from press items quoting MINSA.
- I found no official, current MINSA WhatsApp or chat channel for mental health.
- I found no dedicated national suicide-prevention hotline beyond 113-5. NGO lines (if any) were not verified.
- SAMU 106 coverage by region (it is not nationwide in all areas) was not verified.

## Data protection: Ley 29733 and the new Reglamento (D.S. 016-2024-JUS)

### Takeaway
D.S. 016-2024-JUS is confirmed as the new Reglamento of Ley 29733. It was published on 30 Nov 2024, came into force on 30 Mar 2025 and replaced the 2013 regulation. Health data is sensitive data and needs express consent given in writing or by an equivalent verifiable means. The new rules add extraterritorial reach (with a local representative), a 48-hour breach notification, a mandatory DPO when sensitive data is processed, a security document with "fecha cierta", and adequacy criteria for international transfers.

### Cited Findings
- D.S. 016-2024-JUS approves the new Reglamento of Ley 29733, published 30 Nov 2024 — [IAPP](https://iapp.org/news/a/se-publica-el-nuevo-reglamento-de-protecci-n-de-datos-personales-en-per-); official text in the El Peruano special edition hosted by Congress — [congreso.gob.pe PDF](https://www.congreso.gob.pe/Docs/DGP/DIDP/files/ds_016-2024-jus.pdf); MINJUSDH PDF — [gob.pe](https://cdn.www.gob.pe/uploads/document/file/7886737/93001-nuevo-reglamento-de-la-ley-de-proteccion-de-datos-personales.pdf)
- In force since 30 March 2025, replacing the 2013 regulation — [CMS Grau](https://cms.law/en/per/publication/nuevo-reglamento-de-proteccion-de-datos-personales); [La Ley](https://laley.pe/todo-sobre-el-nuevo-marco-legal-de-proteccion-de-datos-personales-en-peru/)
- Extraterritorial scope: applies to foreign companies that offer goods or services to people in Peru or profile people located in Peru. These companies must designate a representative in Peru as contact with the ANPD — [CMS Grau](https://cms.law/en/per/publication/nuevo-reglamento-de-proteccion-de-datos-personales)
- Health data is sensitive data under Ley 29733 (with biometric data, political or religious beliefs, sexual life, and others) — [IUS360](https://ius360.com/tratamiento-de-datos-en-tiempos-de-cuarentena-sobre-los-datos-personales-referidos-a-la-salud-de-las-personas-alexandra-espinoza-montero/)
- Sensitive-data processing needs express consent given in writing or by an equivalent means that allows proof (Art. 13 of the Law, per a model-clause site) — [modelo.pe](https://modelo.pe/clausula-de-consentimiento-para-tratamiento-de-datos-sensibles-y-biometricos/). The regulation accepts a handwritten or digital signature or another authentication mechanism that guarantees unequivocal will — [IUS360](https://ius360.com/tratamiento-de-datos-en-tiempos-de-cuarentena-sobre-los-datos-personales-referidos-a-la-salud-de-las-personas-alexandra-espinoza-montero/) (this analysis predates 2024, so the article numbering refers to the 2013 regulation)
- Security: a formal security document with "fecha cierta" covering access controls, privileges, audits and periodic verification of systems — [CMS Grau](https://cms.law/en/per/publication/nuevo-reglamento-de-proteccion-de-datos-personales)
- Breach notification: report to the ANPD within 48 hours of detection, even if the breach is contained. Digital incidents also go to the Centro Nacional de Seguridad Digital. Affected data subjects must be informed within the same period in clear language — [CMS Grau](https://cms.law/en/per/publication/nuevo-reglamento-de-proteccion-de-datos-personales); [PPU Legal](https://ppulegal.com/?p=3988)
- International transfers: the regulation sets minimum criteria for assessing whether the destination country offers adequate protection (legal framework, principles, rights, supervisory authority). If it does not, additional safeguards are required — [CMS Grau](https://cms.law/en/per/publication/nuevo-reglamento-de-proteccion-de-datos-personales); [La Cámara](https://lacamara.pe/nuevo-reglamento-refuerza-la-proteccion-de-datos-personales/)
- DPO (oficial de datos personales): mandatory for public entities, large-scale processing, or processing involving sensitive data. The designation must be communicated to the Authority within 15 days, and the DPO must be easy for data subjects to identify — [CMS Grau](https://cms.law/en/per/publication/nuevo-reglamento-de-proteccion-de-datos-personales)
- Impact assessments are optional but recommended, especially for sensitive data, minors, disability and profiling — [Diario Correo](https://diariocorreo.pe/politica/ejecutivo-aprueba-nuevo-reglamento-de-la-ley-de-proteccion-de-datos-personales-inseguridad-extorsionadores-noticia/) (secondary summary)
- The right to object must be resolved within at most 10 days — [CMS Grau](https://cms.law/en/per/publication/nuevo-reglamento-de-proteccion-de-datos-personales)

### Inferences
- A depression chatbot that stores conversations or screening scores processes health (sensitive) data. It therefore needs express, provable consent (a checkbox plus a logged record is the usual practice), a DPO, a security document, and 48-hour breach procedures.
- Using AWS regions or US-based LLM APIs is an international transfer. The team should document the adequacy assessment or added safeguards (contractual clauses) and disclose the recipients and countries in the privacy notice.
- A voluntary impact assessment is advisable, since the app combines sensitive data with possible minors and profiling.

### Gaps
- Databank registration with the ANPD (Registro Nacional de Protección de Datos Personales): I did not verify whether the 2024 Reglamento keeps the registration duty or how it works. It existed under the 2013 framework, which is my background knowledge, not verified in this session.
- Minors: I did not verify the age threshold. The 2013 regulation required parental consent under 14; whether the 2024 text keeps this is unverified.
- Sanction amounts (UIT ranges) and the deadline for appointing a DPO under the transitional provisions were not verified.
- I did not read the exact article numbers of the 2024 regulation on sensitive data or transfers; I relied on law-firm summaries.

## Regulation of digital health, mental health and AI

### Takeaway
Relevant frameworks:
- Mental health: Ley 30947 (Ley de Salud Mental) and its Reglamento D.S. 007-2020-SA, amended by Ley 31627 and D.S. 011-2025-SA.
- Telehealth: Ley Marco de Telesalud 30421, modified by D.Leg. 1490, with Reglamento D.S. 005-2021-SA.
- AI: Ley 31814 (2023) and its Reglamento D.S. 115-2025-PCM (Sep 2025). The first adequacy deadline for private health-sector developers and implementers fell on 10 Sep 2026, and it has passed.

I found no MINSA norm specific to mental-health apps, and no DIGEMID guidance specific to software as a medical device.

### Cited Findings
- D.S. 007-2020-SA approved the Reglamento of Ley 30947 (Ley de Salud Mental) and created CONASAME, the national mental-health council — [gob.pe MINSA norma](https://www.gob.pe/institucion/minsa/normas-legales/455147-007-2020-sa); [Andina](https://andina.pe/ingles/noticia-poder-ejecutivo-promulga-reglamento-ley-salud-mental-787204.aspx)
- Ley 31627 amended Ley 30947 to strengthen prevention and promotion of mental health for children, adolescents and vulnerable groups, and suicide prevention. D.S. 011-2025-SA amended the Reglamento accordingly (e.g., Art. 13, on schools) — [El Peruano](https://busquedas.elperuano.pe/dispositivo/NL/2415136-1); [iuslatin](https://iuslatin.pe/?p=95751)
- D.S. 005-2021-SA, published 23 Jan 2021, is the Reglamento of Ley 30421 (Ley Marco de Telesalud) and D.Leg. 1490. It applies to the whole health sector — [El Peruano](https://busquedas.elperuano.pe/normaslegales/decreto-supremo-que-aprueba-el-reglamentode-la-ley-n-30421-decreto-supremo-n-005-2021-sa-1922320-2/); [LP Derecho](https://lpderecho.pe/reglamento-ley-marco-telesalud-ley-30421-decreto-supremo-005-2021-sa/)
- Telehealth services it defines include teleorientation, telemonitoring and telemanagement, which IPRESS must provide during national emergencies according to their capacity — [UNEP LEAP summary](https://leap.unep.org/en/countries/pe/national-legislation/decreto-supremo-no-005-2021-sa-reglamento-de-la-ley-no-30421-ley)
- AI: D.S. 115-2025-PCM approved the Reglamento of Ley 31814 (published around 9 Sep 2025). It recognizes two categories, misuse and high-risk use, and requires impact assessments for high-risk systems — [DPL News](https://dplnews.com/?p=288242); [El Peruano](https://elperuano.pe/noticia/278569-peru-establece-regulacion-sobre-inteligencia-artificial); [CMS](https://cms.law/es/per/publication/se-aprueba-el-reglamento-de-la-ley-que-promueve-el-uso-de-la-inteligencia-artificial-ia)
- High-risk examples include systems affecting access to health services. Obligations for high-risk systems include algorithmic transparency (informing users of the purpose, functions and decisions supported), security, privacy, explainability, accountability, human oversight and training. The first progressive adequacy deadline was 10 Sep 2026 for private developers and implementers in health, education, justice, security, economy and finance — [CMS alert, Sep 2026](https://cms.law/en/per/publication/inteligencia-artificial-el-10-de-setiembre-vence-el-primer-plazo-de-adecuacion-a-la-ley-n.-31814-para-los-sectores-de-salud-educacion-justicia)
- Health institutions are already issuing internal AI directives that cite D.S. 115-2025-PCM, for example Hospital Lima Este-Vitarte Directiva 001-OETI-HLEV-2026 — [gob.pe PDF](https://cdn.www.gob.pe/uploads/document/file/9481932/7763561-directiva-administrativa-n-001-oeti-hlev-2026-directiva-administrativa-para-la-adecuada-implementacion-y-uso-de-los-sistemas-de-inteligencia-artificial-en-el-hlev.pdf)
- Medical devices: DIGEMID grants sanitary registration for medical devices under Ley 29459 and its framework. Peru uses risk classes I–IV, and foreign manufacturers need a local registration holder — [PRCP "ABC" PDF](https://blog.prcp.com.pe/wp-content/uploads/2024/04/Sobre-el-ABC-de-la-regulación-de-Dispositivos-Médicos-en-Perú-.pdf); [Pure Global](https://www.pureglobal.com/es/markets/peru) (secondary)
- Psychology practice: membership (colegiación) and professional habilitación with the Colegio de Psicólogos del Perú are indispensable to practise as a psychologist (Art. 2 of the CPsP creation law, cited in a CPsP resolution) — [CPsP RD 124-2022](https://cpsplimaycallao.org.pe/wp-content/uploads/2023/06/2022-RD-124-2022-CDN-CPSP.pdf)
- Telepsychology is used in Peru: INSM reports using it to reach remote patients — [El Peruano](https://elperuano.pe/noticia/119852-instituto-nacional-de-salud-mental-brindo-mas-de-15-000-atenciones-en-psicologia). A UPC qualitative study found it viable for building a therapeutic bond — [UPC repository](https://repositorioacademico.upc.edu.pe/handle/10757/667732)

### Inferences
- A non-clinical "first barrier" chatbot that does not diagnose or treat probably sits outside telehealth regulation, which governs services by health personnel and IPRESS. It also probably does not need DIGEMID registration, provided it makes no diagnostic or therapeutic claims. Both points are inferences, not verified rulings.
- If the app screens or triages users toward health services, it may fall into the AI Reglamento's "high-risk" category ("access to health services"). In that case transparency, human-oversight and impact-assessment duties apply, and the 10 Sep 2026 adequacy deadline has already passed for private health actors.
- Any psychologist the app connects users to must be colegiado and habilitado with the CPsP. The app could verify CPsP registration.
- The app should state clearly that it is not a psychologist or medical service, so it is not mistaken for unlicensed practice or telemedicine.

### Gaps
- I found no DIGEMID guidance on software as a medical device or mental-health apps. Whether software falls under the device definition is unverified.
- I found no CPsP code-of-ethics provisions or guidelines on online or virtual psychology.
- I found no MINSA norm specifically on mental-health apps or AI chatbots in health.
- I did not verify the exact list of high-risk uses or prohibited uses in D.S. 115-2025-PCM from the official text.
- I did not verify a consolidated text of the Ley 30947 Reglamento after D.S. 011-2025-SA, or its specific rights provisions (e.g., informed consent, confidentiality).

## Public referral pathway (CSMC and others)

### Takeaway
Peru has a network of roughly 290–305 Centros de Salud Mental Comunitaria (CSMC). The figure varies by source and date. The official gob.pe service page (gob.pe/10942) lists addresses and phones. According to that page, people at risk of suicide or self-harm can go directly to a CSMC without a referral. Others go first to their nearest health facility, which refers them on.

### Cited Findings
- The official gob.pe service "Solicitar atención en Centros de Salud Mental Comunitaria en el Perú" lists addresses and phones of 305 CSMCs nationwide. It says that with self-harm or suicide risk, people can go directly to the nearest CSMC without a referral; otherwise they first attend the nearest health facility, which can refer them — [gob.pe/10942](https://www.gob.pe/10942) (from a search snippet; a direct fetch failed with HTTP 418)
- Counts over time: 277 CSMCs in mid-2024, with 16 more planned — [Andina](https://andina.pe/agencia/noticia-ministerio-salud-cuenta-277-centros-salud-mental-comunitaria-el-pais-991596.aspx). 288 CSMCs and 52 mental-health and addiction hospitalization units — [Peru21](https://peru21.pe/lima/salud-mental-en-crisis-minsa-reporta-735-suicidios-en-el-peru-en-2024-minsa-salud-mental/). Openings described as CSMC No. 298 (Surco) — [Panamericana](https://panamericana.pe/locales/458374-minsa-inaugura-nuevo-centro-salud-mental-comunitaria-viktor-frankl-surco) and No. 301 (Comas) — [Panamericana](https://panamericana.pe/salud/462616-minsa-inaugura-nuevo-centro-salud-mental-comunitaria-comas-beneficiar-600-000-habitantes). New CSMC in Lince, Sep 2025, offering free care for depression, anxiety and addictions — [Infobae](https://www.infobae.com/peru/2025/09/20/minsa-inaugura-centro-de-salud-mental-comunitaria-en-lince-servicios-gratuitos-para-depresion-ansiedad-y-adicciones/)
- CSMCs provide specialized ambulatory care — [Andina](https://andina.pe/ingles/noticia-centros-salud-mental-comunitaria-brindan-atencion-especializada-y-ambulatoria-972221.aspx)
- A 2025 MINSA document evaluates 217 CSMCs run by regional governments and Lima Metropolitana, which is a subset of the network — [gob.pe PDF](https://cdn.www.gob.pe/uploads/document/file/7868921/6631081-resultados-csmc.pdf)
- 113 option 5 can refer callers to CSMCs — [Andina](https://andina.pe/agencia/noticia-linea-113-recibio-mas-135000-llamadas-relacionadas-orientacion-salud-mental-1013087.aspx)

### Inferences
- The app can use gob.pe/10942 as the authoritative directory. If a geolocated "nearest CSMC" feature is built, its data should be refreshed periodically, because the network grows every year.
- The referral flow could look like this:
  - risk detected → 113-5, 106 or a direct CSMC visit (no referral needed);
  - moderate symptoms → primary care facility (centro or puesto de salud) → CSMC;
  - the user prefers private care → a colegiado psychologist.

### Gaps
- I found no official interactive map or open dataset of CSMCs. RENIPRESS/SUSALUD is a likely source but was not verified.
- Requirements and cost were not verified from the official page: DNI, SIS affiliation, whether care is free for non-SIS users.
- I did not research private options (EsSalud mental-health services, clinics, NGOs) or university counselling services.

## Peru mental-health statistics (problem statement)

### Takeaway
INSM epidemiological studies (Lima Metropolitana 2002/2012 and regional studies) report a lifetime prevalence of depressive episodes of about 16–21% by region. Only about 13–25% of people with disorders receive treatment. Registered suicides (SINADEF) were 735 in 2024, almost double 2023's 391. The 2025 count ran ahead of 2024 for January–April.

### Cited Findings
- Lifetime prevalence of major depression: 18.3% in Lima, 16.2% in the highlands (sierra) and 21.4% in the Amazon region (selva), per INSM studies cited in academic work. Treatment coverage: about 25% in Lima and 13% in the sierra and selva — [Redalyc](https://www.redalyc.org/pdf/3720/372044762004.pdf); [Rev. Neuropsiquiatría (UPCH)](https://revistas.upch.edu.pe/index.php/RNP/article/download/1674/1702/2754) (secondary citations of INSM studies; years differ between sources, 2002 vs. 2008/2012)
- In INSM data, 2 in 10 adults in Lima suffer some psychiatric disorder, with depressive and anxiety disorders the most frequent. About 1 in 12 adolescents has a depressive disorder — [Rev. Neuropsiquiatría (UPCH)](https://revistas.upch.edu.pe/index.php/RNP/article/download/1674/1702/2754)
- Peru has 0.76 psychiatrists per 100,000 inhabitants (WHO Mental Health Atlas 2014, as cited) — [Redalyc](https://www.redalyc.org/pdf/3720/372051876003.pdf)
- Suicides (SINADEF): 735 in 2024 vs. 391 in 2023. Arequipa had 120 (another source says 119), Lima 115 and Cusco 70 — [Peru21](https://peru21.pe/lima/salud-mental-en-crisis-minsa-reporta-735-suicidios-en-el-peru-en-2024-minsa-salud-mental/); [Infobae Jan 2025](https://www.infobae.com/peru/2025/01/30/peru-registra-alarmante-aumento-de-suicidios-en-el-inicio-del-2025-arequipa-y-lima-son-las-ciudades-que-registraron-mayor-numero-de-casos/)
- 253 suicides in January–April 2025 vs. 207 in the same period of 2024, mainly among people aged 15–34 — [Infobae Apr 2025](https://www.infobae.com/peru/2025/04/25/peru-registra-253-suicidios-en-lo-que-va-del-2025-cifra-ya-sobrepasa-casos-de-enero-a-abril-de-2024/)
- MINSA facilities attended 6,910 cases of self-inflicted injury in 2024 (5,042 women, 1,868 men) — [Peru21](https://peru21.pe/lima/salud-mental-en-crisis-minsa-reporta-735-suicidios-en-el-peru-en-2024-minsa-salud-mental/). More than 5,500 suicide attempts were reported, mostly by women — [ConsultorSalud](https://consultorsalud.com/salud-mental-peru-5500-intentos-suicidio-mujere/)
- MINSA states that 90% of suicides are related to depression, anxiety and other psychiatric disorders — [Panamericana](https://panamericana.pe/salud/435399-90-casos-suicidio-relacionados-depresion-ansiedad-trastornos-salud-mental)

### Inferences
- The combination of high prevalence, a low treatment rate and few specialists supports the "first barrier plus referral" framing of the app.
- The jump from 391 to 735 registered suicides may partly reflect changes in registration (SINADEF coverage), not only a real increase. Present it with that caveat.

### Gaps
- I did not obtain the primary INSM reports (Estudios Epidemiológicos de Salud Mental) or ENDES depression-screening (PHQ-9) figures. Use INSM or INEI primary sources before publication.
- I found no full-year 2025 suicide total, and no national suicide rate per 100,000 from an official source.
- I found no recent official treatment-gap figure (post-2020).
