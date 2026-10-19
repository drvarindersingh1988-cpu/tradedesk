# MediCore KZ — Medical Information System

Electronic medical record (EMR) for KAZ Minerals site clinics, built independently by the Group Chief Medical Officer (clinical lead) with Claude writing the code. It will replace the current 1C:Medicine system (CiToDesk-PM, customised by contractor SMT). When finished it is handed to KAZ Minerals IT ready to install on approved servers in Kazakhstan.

Full requirements and gap analysis: `docs/project-brief.md`. Read it before designing or building any module.

## Where the project stands

- Phase: requirements gathering. Process documentation is being collected from site staff, one workflow at a time.
- Agreed next step: design the core data model (person registry, medicine catalogue, warehouses and stock, encounters, roles and sites) before building more UI.
- Existing code is an early prototype only: `index.html` (app shell), `css/styles.css`, `js/data.js` (localStorage sample data with placeholder names that are not Kazakh). `index.html` references JS modules (`app.js`, `dashboard.js`, `opd.js` etc.) that do not exist yet. Expect the prototype to be reworked once the data model is agreed.
- Do not build a module until the user has sent the process documentation for it and says to proceed.

## Sites and ownership

- Kazakhstan sites: Aktogay, Bozshakol, VCM. Kyrgyzstan site: Bozymchak (separate deployment on Kyrgyz hosting).
- KAZ Minerals owns the system. Medical services are delivered by contractor companies (currently Mediker). Each site is linked to its contractor, and every document prints with the contractor's name, logo and contact details.
- Contractor staff see only their own site. The CMO sees all sites, including a combined KZ + KY dashboard.
- Medical staff are contractors who use shared position mailboxes, so accounts are per position (for example `aktogay.nurse1`), but every signature and audit entry must still identify the person on duty.

## Non-negotiable rules

- No real patient or employee data in this repository, ever: invented test data only. Screenshots must be anonymised.
- Patient data stays on servers in Kazakhstan (personal data localisation law). No Azure or other foreign cloud for identifiable data.
- AI drafts and the clinician decides: nothing AI-generated enters the record without a clinician's signature, and every AI suggestion is logged together with what was accepted or changed (AI Law No. 230-VIII). Identifiable data goes only to models hosted in Kazakhstan (for example Ollama with Llama, Qwen or Mistral, and Whisper for speech).
- The system prevents errors instead of relying on user discipline: mandatory fields, fixed lists, duplicate checks, validation.
- Zero paper, Excel or Word: every report, certificate and state form comes out of the system.
- Official forms must match Ministry of Health templates exactly (for example 026/у under order ҚР ДСМ-175/2020), in Kazakh and Russian with local date format.

## Target architecture

- Web app for phone, tablet and desktop. Offline-first progressive web app (PWA), because remote sites have poor connectivity.
- React frontend, Node.js backend, PostgreSQL. Packaged in containers so IT can run it on any approved server.
- Data structured to FHIR. Integrations: HL7/ASTM for lab analysers, DICOM with Modality Worklist for X-ray, ECG as native files, HR feed for employees, smsc.kz for SMS alerts.
- Languages: English, Russian, Kazakh, Kyrgyz. One language per user. Interface text translated by people, medical terms from ICD-10, free text by local AI.
- Reference content: ICD-10 and ICD-11, Kazakhstan clinical protocols (rcrz.kz), Kyrgyz protocols for the KY deployment, WHO/ICMM/ICOH guidance.
- Hosting candidates: PS.kz or Beeline KZ (Kazakhstan), Elcat.kg (Kyrgyzstan).

## Process collection order

1. Walk-in clinic visit and treatment
2. Emergency response and medevac
3. Pharmacy: receipt, issue, write-off, stock count, handover
4. Pre-employment and periodic medical examinations
5. Sick leave and return to work
6. Contractor KPIs and monthly reporting
7. Vaccinations, alcohol and drug testing, expatriate and family care, training

Later: HR module for medical staff (schedules, documents, certificates), HR system integration, role-based education module with periodic tests, protocol library, device integration (pre-shift exam devices, X-ray, PACS).

## Module specification format

Each module is specified in the format contractor SMT requires, so the same spec can also be sent to SMT for interim fixes to the current system: task name, goal, current state, required state, user scenario, input fields (type, mandatory, source, validation), outputs, business logic, roles and rights, reports (columns, filters, grouping, calculations, export), print forms, integrations, acceptance criteria.

## Working style

- The user is a physician, not a software engineer. Explain technical steps plainly and step by step, and give exact commands for Windows PowerShell.
- Development branch: `claude/medical-information-system-0b9ihz`.
