# RemotEMR — Project Brief

Source: the CMO's project brief (Claude Docs, October 2026) and the analysis of the current system's screenshots. Specific patient records, staff names and the medication-loss investigation are deliberately left out of this repository.

## Definition of "ready"

Ready to plug in, not already plugged in. All modules, workflows and the device integration layer are built and tested against simulators. IT then hosts it on approved servers in Kazakhstan, runs penetration testing, and connects real devices on site with the vendors.

## Legal and regulatory framework

Legal sign-off from a Kazakh law firm or KAZ Minerals legal is required before go-live.

| Rule | What it means for the system |
|---|---|
| Personal data law (localisation) | Data on Kazakh citizens stored on servers inside Kazakhstan; cross-border transfer only with legal grounds |
| Health Code (medical secrecy) | Encryption, role-based access, full audit trail, named users only |
| Law No. 230-VIII on Artificial Intelligence (in force 18 Jan 2026) | Owner classifies the risk level, manages and documents risk, ensures transparency and explainability |
| Digital Code (in force 11 Jul 2026) | Further digital rules; secondary acts under the AI law still being adopted through 2026 |
| Order ҚР ДСМ-175/2020 | Official medical forms (e.g. 026/у medical advisory commission conclusion) must match the template |
| Order ҚР ДСМ-47 (2021) | Sanitary rules, including scarlet fever and chickenpox contact management (infection control) |
| Clinical decision support | Alerts that influence decisions may count as medical-device software; keep AI as drafts signed by a clinician |

AI hosting tiers, cleanest first: open-source models on company servers in Kazakhstan; a provider hosted in Kazakhstan approved by IT and legal; international cloud AI for de-identified data only.

## Architecture layers

1. User interface: web and mobile, one language per user, role-based screens.
2. Clinical core: single person registry, encounters, periodic medical examinations, sick leave, emergencies, pharmacy, medical advisory commission (MAC), reports.
3. Integration layer: HL7 and ASTM for lab analysers; DICOM with Modality Worklist for imaging; ECG files; HR feed.
4. AI layer (pluggable provider): speech-to-text, note drafting, summaries, alerts, plain-language analytics.
5. Security and audit: encryption, named accounts, electronic signatures, full audit log, backups.

Planned AI features: ambient consultation scribe producing a structured note with suggested ICD-10 codes; patient summary card (allergies, conditions, medicines, last abnormal result, work restrictions, overdue medicals); CMO dashboard with plain-language questions and pattern alerts (heat illness, respiratory clusters, low stock). Kazakh speech recognition must be tested with volunteer staff recordings before it is promised.

## Gaps in the current system

The current 1C:Medicine system covers the right processes but lacks guardrails. Most gaps are configuration and validation failures, not missing modules.

| Module | What works | Key gaps |
|---|---|---|
| Patients and employees | Employee list linked to company, department, position | Placeholder ID "0000-9999" on most records; missing IINs, names, departments; test record in live data; two separate person registries; company names in both Cyrillic and Latin |
| Doctor's visit | Tabs for history, ICD-10 diagnoses, medications | Vitals at the bottom, default 0, not mandatory; visit type mixes encounter with outcome; default time 12:00; free-text history; no allergy field; prescribing has no dose, route, frequency or duration; warehouse picked manually every visit; mixed English/Russian labels |
| Pharmacy and stock | Receipts, write-offs, stock reports | Receipts largely unrecorded since 2024; no responsible person per warehouse; no sub-locations; batch write-offs instead of point-of-use; no batch or expiry tracking; duplicate and clinically wrong item names (wrong strengths, wrong units, a knee brace under antibacterials); INN and Item ID fields empty; folders named after single drugs instead of therapeutic classes |
| Periodic medical examinations | Eligible list, specialist sub-forms, functional diagnostics, hazard class, dispensary group, visit history | Fitness expiry miscalculated; BP and pulse can be 0; specialist diagnoses not consolidated; "Healthy" can be ticked alongside a diagnosis; no structured restrictions; audiometry and ECG stored as PDF or JPEG; generic "Administrator" author; eligible list imported from Excel yearly; thousands of exams created in minutes so dates are creation stamps |
| Sick leave | List with ICD-10 diagnosis, doctor, dates | Entered weeks late; free-text eGov number; no alerts for long or repeated absence, notifiable disease or return-to-work review |
| Referrals | Per-specialist referral printouts | Open loop: outcome not tracked before a fitness decision |
| PACS | DICOM query by modality | Manual batch import and manual attachment to patients |
| Medical advisory commission | Document list and printable 026/у | Printed number and date differ from the record; diagnosis, conclusion and signatures can be blank; template header error; US date format on a state form; unposted documents with no alert |
| Reports | PME coverage, impaired health, sick leave, diagnoses | Broken references ("Object not found"); no dashboard or KPIs |
| Lab | Manual result documents | No analyser integration |
| Master data and access | ICD-10, warehouses, positions | Accounting leftovers (bank accounts, signatories); no visible role administration; no formulary or hazard catalogue |

## Requirements for the new system

Every requirement comes from a gap above. The principle: the system prevents errors instead of relying on user discipline.

1. **Single person registry**: mandatory unique IIN, live HR integration, roles for employee, contractor and family member, no placeholder IDs, no test data in production.
2. **Structured medicine catalogue**: INN + strength + form + pack chosen from fixed lists; duplicate warning before saving; creation restricted to a pharmacist or responsible nurse; active / inactive / archived status (archived items keep their history but leave selection lists); mandatory batch and expiry; therapeutic-class grouping.
3. **Accountable stock**: sub-locations (emergency bag, ambulance, safe, cabinet); a named responsible person per location, required at setup; receipt required before issue; real-time write-off linked to the encounter; shift-handover count with double signature for controlled drugs; discrepancy and expiry alerts; warehouse defaults to the clinician's site.
4. **Safety-first visit form**: vitals at the top and mandatory, with shock index; real event time captured automatically; allergies on every screen; encounter type separate from disposition; structured trauma fields (mechanism, time, body map, PPE, HSE incident link).
5. **Proper prescribing**: dose, route, frequency and duration all mandatory; allergy and interaction checks; administration recorded against stock.
6. **Periodic exam validation**: automatic fitness expiry; mandatory BP, pulse and BMI with auto-coding; specialist diagnoses flow into the final result; "Healthy" blocked when a diagnosis exists; structured restrictions (corrective lenses, no heights, no night shifts); real examination date kept separate from creation date.
7. **Safety-critical alerts for operators and drivers**: G45, epilepsy, syncope, arrhythmias, uncontrolled hypertension, insulin-treated diabetes and end-stage kidney disease trigger a fitness review before "fit" can be signed.
8. **Structured diagnostics**: audiometry thresholds stored as numbers with a standard threshold shift alert against baseline; spirometry trended; ECG as native files.
9. **Sick leave linked to the visit**: real-time entry; validated eGov number; alerts for absence over 14 days, repeated episodes and notifiable diseases (automatic sanitary-service notification task); return-to-work clearance step.
10. **Closed-loop referrals**: outcome required before a dependent fitness decision; overdue referral list.
11. **Automatic imaging**: DICOM Modality Worklist sends the patient's IIN to the device; studies attach automatically.
12. **MAC workflow**: mandatory diagnosis, conclusion and recommendation; members' electronic signatures; printed number and date always match the record; official templates validated in Kazakh and Russian with local date format.
13. **Incomplete-documents dashboard**: unposted, unsigned or overdue documents per clinician and site.
14. **Access and audit**: named users only, role-based access administration, electronic signatures, full audit trail, no accounting menus for clinicians.
15. **Language**: full English, Russian, Kazakh and Kyrgyz versions, one language per user.
16. **Dashboards**: dispositions, evacuations, response times, stock discrepancies and expiries, contractor KPIs.

## For each process collected, capture

Name and trigger; roles involved; steps in order including workarounds; documents and forms (Excel, paper, state forms, emails); decision points; outputs and recipients; pain points; applicable orders, standards and KPIs.

## Build roadmap

1. Process map of every workflow, plus current-system gaps.
2. Core design: data model, roles, structure.
3. Clinical modules: visits, occupational health, emergencies and medevac, pharmacy and stock, contractor KPIs.
4. AI features: scribe, summaries, alerts, analytics.
5. Device integration layer tested against simulators.
6. Handover pack: security hardening, multilingual interface, deployment package, documentation for IT.
