/* ============================================================
   MediCore — Data Layer (localStorage persistence)
   ============================================================ */

const DB = (() => {
  // ---------- helpers ----------
  const uid = prefix => `${prefix}-${Date.now().toString(36).toUpperCase()}-${Math.random().toString(36).slice(2,5).toUpperCase()}`;
  const today = () => new Date().toISOString().split('T')[0];
  const daysAgo = n => { const d = new Date(); d.setDate(d.getDate() - n); return d.toISOString().split('T')[0]; };
  const daysAhead = n => { const d = new Date(); d.setDate(d.getDate() + n); return d.toISOString().split('T')[0]; };

  // ---------- schema keys ----------
  const KEYS = {
    patients: 'mc_patients',
    opdVisits: 'mc_opd',
    ipdAdmissions: 'mc_ipd',
    appointments: 'mc_appointments',
    medications: 'mc_medications',
    medTransactions: 'mc_med_tx',
    chronicCases: 'mc_chronic',
    screenings: 'mc_screenings',
    staff: 'mc_staff',
    sites: 'mc_sites',
    settings: 'mc_settings',
    users: 'mc_users',
  };

  // ---------- read / write ----------
  const read = key => { try { return JSON.parse(localStorage.getItem(key) || 'null'); } catch { return null; } };
  const write = (key, val) => localStorage.setItem(key, JSON.stringify(val));

  // ---------- sample data ----------
  const SEED_PATIENTS = [
    { id:'PAT-001', registrationDate: daysAgo(120), firstName:'Amara', lastName:'Nkosi', dob:'1978-06-15', gender:'Female', bloodType:'O+', phone:'+260971234001', email:'amara.nkosi@email.com', address:'12 Independence Ave', city:'Lusaka', country:'Zambia', emergencyName:'James Nkosi', emergencyPhone:'+260971234002', emergencyRelation:'Spouse', allergies:['Penicillin'], chronicConditions:['Hypertension','Type 2 Diabetes'], insurance:'NHIMA-7823', site:'site-1', status:'active', notes:'' },
    { id:'PAT-002', registrationDate: daysAgo(90), firstName:'David', lastName:'Okonkwo', dob:'1990-03-22', gender:'Male', bloodType:'A+', phone:'+260971234003', email:'', address:'45 Cairo Rd', city:'Lusaka', country:'Zambia', emergencyName:'Grace Okonkwo', emergencyPhone:'+260971234004', emergencyRelation:'Mother', allergies:[], chronicConditions:[], insurance:'', site:'site-1', status:'active', notes:'' },
    { id:'PAT-003', registrationDate: daysAgo(200), firstName:'Fatima', lastName:'Al-Rashid', dob:'1965-11-08', gender:'Female', bloodType:'B+', phone:'+260971234005', email:'fatima.r@email.com', address:'7 Kafue Rd', city:'Kafue', country:'Zambia', emergencyName:'Hassan Al-Rashid', emergencyPhone:'+260971234006', emergencyRelation:'Son', allergies:['Aspirin','Sulfa'], chronicConditions:['COPD','Hypertension'], insurance:'NHIMA-3391', site:'site-1', status:'active', notes:'Hard of hearing — speak slowly' },
    { id:'PAT-004', registrationDate: daysAgo(60), firstName:'Michael', lastName:'Banda', dob:'2005-07-30', gender:'Male', bloodType:'AB-', phone:'+260971234007', email:'', address:'23 Longacres', city:'Lusaka', country:'Zambia', emergencyName:'Patricia Banda', emergencyPhone:'+260971234008', emergencyRelation:'Mother', allergies:[], chronicConditions:[], insurance:'', site:'site-1', status:'active', notes:'Paediatric patient' },
    { id:'PAT-005', registrationDate: daysAgo(45), firstName:'Grace', lastName:'Mwanza', dob:'1955-02-14', gender:'Female', bloodType:'O-', phone:'+260971234009', email:'grace.mwanza@email.com', address:'88 Olympia', city:'Lusaka', country:'Zambia', emergencyName:'Peter Mwanza', emergencyPhone:'+260971234010', emergencyRelation:'Spouse', allergies:['NSAIDs'], chronicConditions:['Osteoarthritis','Hypertension','Hypothyroidism'], insurance:'NHIMA-5512', site:'site-1', status:'active', notes:'' },
    { id:'PAT-006', registrationDate: daysAgo(15), firstName:'Emmanuel', lastName:'Chanda', dob:'1995-09-18', gender:'Male', bloodType:'A-', phone:'+260971234011', email:'emmanuel.c@email.com', address:'3 Northmead', city:'Lusaka', country:'Zambia', emergencyName:'', emergencyPhone:'', emergencyRelation:'', allergies:[], chronicConditions:[], insurance:'', site:'site-2', status:'active', notes:'' },
    { id:'PAT-007', registrationDate: daysAgo(300), firstName:'Precious', lastName:'Sakala', dob:'1982-04-01', gender:'Female', bloodType:'B-', phone:'+260971234012', email:'', address:'55 Chilenje', city:'Lusaka', country:'Zambia', emergencyName:'Moses Sakala', emergencyPhone:'+260971234013', emergencyRelation:'Spouse', allergies:['Metronidazole'], chronicConditions:['Type 2 Diabetes','Chronic Kidney Disease'], insurance:'NHIMA-9900', site:'site-1', status:'active', notes:'CKD stage 3 — caution with NSAIDs' },
    { id:'PAT-008', registrationDate: daysAgo(10), firstName:'Joseph', lastName:'Tembo', dob:'1972-12-25', gender:'Male', bloodType:'O+', phone:'+260971234014', email:'', address:'1 Foxdale', city:'Lusaka', country:'Zambia', emergencyName:'', emergencyPhone:'', emergencyRelation:'', allergies:[], chronicConditions:[], insurance:'NHIMA-2211', site:'site-1', status:'active', notes:'' },
    { id:'PAT-009', registrationDate: daysAgo(5), firstName:'Charity', lastName:'Phiri', dob:'2018-08-12', gender:'Female', bloodType:'A+', phone:'+260971234015', email:'', address:'19 Kabulonga', city:'Lusaka', country:'Zambia', emergencyName:'Miriam Phiri', emergencyPhone:'+260971234016', emergencyRelation:'Mother', allergies:[], chronicConditions:[], insurance:'', site:'site-1', status:'active', notes:'Paediatric patient — use weight-based dosing' },
    { id:'PAT-010', registrationDate: daysAgo(180), firstName:'Samuel', lastName:'Lungu', dob:'1948-01-30', gender:'Male', bloodType:'B+', phone:'+260971234017', email:'samuel.l@email.com', address:'77 Fairview', city:'Lusaka', country:'Zambia', emergencyName:'Ruth Lungu', emergencyPhone:'+260971234018', emergencyRelation:'Daughter', allergies:['Penicillin','Codeine'], chronicConditions:['Hypertension','Type 2 Diabetes','Ischaemic Heart Disease'], insurance:'NHIMA-4456', site:'site-1', status:'active', notes:'High risk cardiac patient' },
  ];

  const SEED_STAFF = [
    { id:'DOC-001', name:'Dr. Sarah Mulenga', role:'doctor', specialty:'General Medicine', phone:'+260977001001', email:'sarah@medicore.zm', site:'site-1' },
    { id:'DOC-002', name:'Dr. Peter Zulu', role:'doctor', specialty:'Internal Medicine', phone:'+260977001002', email:'peter@medicore.zm', site:'site-1' },
    { id:'DOC-003', name:'Dr. Anna Ngoma', role:'doctor', specialty:'Paediatrics', phone:'+260977001003', email:'anna@medicore.zm', site:'site-2' },
    { id:'NRS-001', name:'Nurse Janet Banda', role:'nurse', specialty:'', phone:'+260977001004', email:'janet@medicore.zm', site:'site-1' },
    { id:'NRS-002', name:'Nurse Charles Phiri', role:'nurse', specialty:'', phone:'+260977001005', email:'charles@medicore.zm', site:'site-1' },
    { id:'PHM-001', name:'Pharmacist Ruth Mwale', role:'pharmacist', specialty:'', phone:'+260977001006', email:'ruth@medicore.zm', site:'site-1' },
    { id:'ADM-001', name:'Admin User', role:'admin', specialty:'', phone:'+260977001007', email:'admin@medicore.zm', site:'site-1' },
  ];

  const SEED_MEDS = [
    { id:'MED-001', name:'Amoxicillin 500mg', category:'Antibiotics', type:'medicine', unit:'Capsule', stock:2400, minStock:300, expiryDate:'2026-12-01', batchNo:'BCH-2024-001', supplier:'MedSupply Ltd', costPerUnit:0.80, siteId:'site-1' },
    { id:'MED-002', name:'Paracetamol 500mg', category:'Analgesics', type:'medicine', unit:'Tablet', stock:8000, minStock:1000, expiryDate:'2027-06-01', batchNo:'BCH-2024-002', supplier:'PharmaZam', costPerUnit:0.10, siteId:'site-1' },
    { id:'MED-003', name:'Metformin 500mg', category:'Antidiabetics', type:'medicine', unit:'Tablet', stock:3600, minStock:500, expiryDate:'2026-09-01', batchNo:'BCH-2024-003', supplier:'MedSupply Ltd', costPerUnit:0.25, siteId:'site-1' },
    { id:'MED-004', name:'Amlodipine 5mg', category:'Antihypertensives', type:'medicine', unit:'Tablet', stock:180, minStock:200, expiryDate:'2026-11-01', batchNo:'BCH-2024-004', supplier:'PharmaZam', costPerUnit:0.30, siteId:'site-1' },
    { id:'MED-005', name:'Atorvastatin 20mg', category:'Lipid Lowering', type:'medicine', unit:'Tablet', stock:1200, minStock:300, expiryDate:'2026-08-01', batchNo:'BCH-2024-005', supplier:'MedSupply Ltd', costPerUnit:0.60, siteId:'site-1' },
    { id:'MED-006', name:'Salbutamol Inhaler 100mcg', category:'Bronchodilators', type:'medicine', unit:'Inhaler', stock:45, minStock:50, expiryDate:'2026-03-01', batchNo:'BCH-2024-006', supplier:'RespiCare', costPerUnit:8.50, siteId:'site-1' },
    { id:'MED-007', name:'ORS Sachets', category:'Rehydration', type:'medicine', unit:'Sachet', stock:600, minStock:200, expiryDate:'2027-01-01', batchNo:'BCH-2024-007', supplier:'PharmaZam', costPerUnit:0.20, siteId:'site-1' },
    { id:'MED-008', name:'Surgical Gloves (L)', category:'Supplies', type:'supply', unit:'Pair', stock:400, minStock:100, expiryDate:'2028-01-01', batchNo:'BCH-2024-008', supplier:'MedSupply Ltd', costPerUnit:0.50, siteId:'site-1' },
    { id:'MED-009', name:'IV Cannula 20G', category:'Supplies', type:'supply', unit:'Piece', stock:90, minStock:100, expiryDate:'2027-06-01', batchNo:'BCH-2024-009', supplier:'SurgicalSupply', costPerUnit:0.70, siteId:'site-1' },
    { id:'MED-010', name:'Artemether/Lumefantrine 20/120mg', category:'Antimalarials', type:'medicine', unit:'Tablet', stock:1800, minStock:400, expiryDate:'2026-10-01', batchNo:'BCH-2024-010', supplier:'MedSupply Ltd', costPerUnit:0.90, siteId:'site-1' },
    { id:'MED-011', name:'Cotrimoxazole 480mg', category:'Antibiotics', type:'medicine', unit:'Tablet', stock:2200, minStock:400, expiryDate:'2026-07-01', batchNo:'BCH-2024-011', supplier:'PharmaZam', costPerUnit:0.15, siteId:'site-1' },
    { id:'MED-012', name:'Losartan 50mg', category:'Antihypertensives', type:'medicine', unit:'Tablet', stock:1500, minStock:300, expiryDate:'2026-10-15', batchNo:'BCH-2024-012', supplier:'MedSupply Ltd', costPerUnit:0.40, siteId:'site-1' },
    { id:'MED-013', name:'Insulin Glargine 100U/ml (vial)', category:'Antidiabetics', type:'medicine', unit:'Vial', stock:30, minStock:20, expiryDate:'2025-12-01', batchNo:'BCH-2024-013', supplier:'DiabeCare', costPerUnit:18.00, siteId:'site-1' },
    { id:'MED-014', name:'Levothyroxine 50mcg', category:'Thyroid', type:'medicine', unit:'Tablet', stock:900, minStock:200, expiryDate:'2026-04-01', batchNo:'BCH-2024-014', supplier:'PharmaZam', costPerUnit:0.20, siteId:'site-1' },
    { id:'MED-015', name:'Ibuprofen 400mg', category:'Analgesics/NSAIDs', type:'medicine', unit:'Tablet', stock:3000, minStock:500, expiryDate:'2026-12-01', batchNo:'BCH-2024-015', supplier:'PharmaZam', costPerUnit:0.12, siteId:'site-1' },
  ];

  const SEED_CHRONIC = [
    { id:'CHR-001', patientId:'PAT-001', condition:'Hypertension', icdCode:'I10', severity:'Moderate', enrollDate: daysAgo(400), medications:['Amlodipine 5mg','Losartan 50mg'], target:'BP < 130/80 mmHg', lastVisit: daysAgo(14), nextFollowup: daysAhead(16), status:'active', notes:'BP well controlled on dual therapy' },
    { id:'CHR-002', patientId:'PAT-001', condition:'Type 2 Diabetes', icdCode:'E11', severity:'Moderate', enrollDate: daysAgo(400), medications:['Metformin 1g BD','Glibenclamide 5mg OD'], target:'HbA1c < 7%', lastVisit: daysAgo(14), nextFollowup: daysAhead(16), status:'active', notes:'Last HbA1c 7.2%' },
    { id:'CHR-003', patientId:'PAT-003', condition:'COPD', icdCode:'J44.1', severity:'Severe', enrollDate: daysAgo(600), medications:['Salbutamol inhaler PRN','Tiotropium 18mcg OD'], target:'FEV1 stable, no exacerbations', lastVisit: daysAgo(30), nextFollowup: daysAhead(30), status:'active', notes:'2 exacerbations last year' },
    { id:'CHR-004', patientId:'PAT-005', condition:'Hypertension', icdCode:'I10', severity:'Mild', enrollDate: daysAgo(180), medications:['Amlodipine 5mg OD'], target:'BP < 140/90 mmHg', lastVisit: daysAgo(7), nextFollowup: daysAhead(23), status:'active', notes:'' },
    { id:'CHR-005', patientId:'PAT-007', condition:'Type 2 Diabetes', icdCode:'E11', severity:'Severe', enrollDate: daysAgo(700), medications:['Insulin Glargine 20U nocte','Metformin 500mg BD'], target:'HbA1c < 8%', lastVisit: daysAgo(21), nextFollowup: daysAhead(9), status:'active', notes:'On insulin — monitor closely' },
    { id:'CHR-006', patientId:'PAT-007', condition:'Chronic Kidney Disease', icdCode:'N18.3', severity:'Moderate', enrollDate: daysAgo(500), medications:['Losartan 50mg OD'], target:'eGFR stable, UP:Cr < 0.3', lastVisit: daysAgo(21), nextFollowup: daysAhead(9), status:'active', notes:'CKD Stage 3 — avoid nephrotoxic drugs' },
    { id:'CHR-007', patientId:'PAT-010', condition:'Ischaemic Heart Disease', icdCode:'I25.1', severity:'Severe', enrollDate: daysAgo(800), medications:['Aspirin 75mg OD','Atorvastatin 40mg nocte','Bisoprolol 5mg OD'], target:'LDL < 1.8 mmol/L, BP controlled', lastVisit: daysAgo(10), nextFollowup: daysAhead(20), status:'active', notes:'Previous MI 2021' },
  ];

  const SEED_SCREENINGS = [
    { id:'SCR-001', patientId:'PAT-001', type:'Blood Pressure', date: daysAgo(14), result:'138/88 mmHg', status:'abnormal', referredTo:'CHR-001', notes:'Above target, reviewed medication', conductedBy:'NRS-001', site:'site-1' },
    { id:'SCR-002', patientId:'PAT-002', type:'Blood Glucose (Random)', date: daysAgo(2), result:'5.6 mmol/L', status:'normal', referredTo:'', notes:'', conductedBy:'NRS-001', site:'site-1' },
    { id:'SCR-003', patientId:'PAT-004', type:'BMI Assessment', date: daysAgo(5), result:'BMI 22.4', status:'normal', referredTo:'', notes:'', conductedBy:'NRS-002', site:'site-1' },
    { id:'SCR-004', patientId:'PAT-005', type:'Thyroid Function (TSH)', date: daysAgo(20), result:'TSH 0.9 mIU/L', status:'normal', referredTo:'', notes:'On levothyroxine — stable', conductedBy:'DOC-001', site:'site-1' },
    { id:'SCR-005', patientId:'PAT-003', type:'Oxygen Saturation', date: daysAgo(30), result:'SpO2 91%', status:'abnormal', referredTo:'CHR-003', notes:'Low due to COPD — on home O2', conductedBy:'NRS-001', site:'site-1' },
    { id:'SCR-006', patientId:'PAT-006', type:'Blood Pressure', date: today(), result:'122/76 mmHg', status:'normal', referredTo:'', notes:'', conductedBy:'NRS-002', site:'site-2' },
  ];

  const SEED_APPOINTMENTS = [
    { id:'APT-001', patientId:'PAT-001', date: today(), time:'09:00', duration:30, doctorId:'DOC-001', type:'Follow-up', reason:'Hypertension & Diabetes review', status:'scheduled', site:'site-1' },
    { id:'APT-002', patientId:'PAT-002', date: today(), time:'09:30', duration:20, doctorId:'DOC-001', type:'New', reason:'Acute cough and fever', status:'completed', site:'site-1' },
    { id:'APT-003', patientId:'PAT-005', date: today(), time:'10:00', duration:30, doctorId:'DOC-002', type:'Follow-up', reason:'Joint pain review', status:'scheduled', site:'site-1' },
    { id:'APT-004', patientId:'PAT-010', date: today(), time:'11:00', duration:45, doctorId:'DOC-002', type:'Follow-up', reason:'Cardiac review + ECG', status:'scheduled', site:'site-1' },
    { id:'APT-005', patientId:'PAT-009', date: today(), time:'11:30', duration:20, doctorId:'DOC-003', type:'New', reason:'Fever and ear pain', status:'scheduled', site:'site-1' },
    { id:'APT-006', patientId:'PAT-007', date: daysAhead(1), time:'09:00', duration:30, doctorId:'DOC-001', type:'Follow-up', reason:'Diabetes + CKD review', status:'scheduled', site:'site-1' },
    { id:'APT-007', patientId:'PAT-003', date: daysAhead(2), time:'14:00', duration:30, doctorId:'DOC-002', type:'Follow-up', reason:'COPD review + spirometry', status:'scheduled', site:'site-1' },
    { id:'APT-008', patientId:'PAT-004', date: daysAhead(3), time:'10:30', duration:20, doctorId:'DOC-003', type:'Follow-up', reason:'Teenage health check', status:'scheduled', site:'site-1' },
    { id:'APT-009', patientId:'PAT-008', date: daysAgo(1), time:'10:00', duration:20, doctorId:'DOC-001', type:'New', reason:'Skin rash', status:'completed', site:'site-1' },
    { id:'APT-010', patientId:'PAT-006', date: daysAgo(2), time:'14:00', duration:30, doctorId:'DOC-003', type:'New', reason:'Chest pain — reviewed', status:'completed', site:'site-2' },
  ];

  const SEED_OPD = [
    { id:'OPD-001', patientId:'PAT-002', date: today(), time:'09:30', doctorId:'DOC-001', site:'site-1', chiefComplaint:'Acute cough and fever for 3 days', diagnosis:'Upper Respiratory Tract Infection', icdCode:'J06.9', vitals:{ bp:'122/78', pulse:88, temp:38.1, weight:74, height:172, spo2:97, rr:18 }, prescription:[{ medId:'MED-002', name:'Paracetamol 500mg', dosage:'500mg', freq:'TDS', duration:'5 days', instructions:'After meals' },{ medId:'MED-001', name:'Amoxicillin 500mg', dosage:'500mg', freq:'TDS', duration:'7 days', instructions:'After meals' }], notes:'Throat erythema. No tonsillar exudate. Review if no improvement in 5 days.', followUpDate:'', status:'completed' },
    { id:'OPD-002', patientId:'PAT-008', date: daysAgo(1), time:'10:00', doctorId:'DOC-001', site:'site-1', chiefComplaint:'Itchy skin rash on both arms', diagnosis:'Allergic Dermatitis', icdCode:'L23.9', vitals:{ bp:'130/84', pulse:76, temp:36.8, weight:82, height:175, spo2:99, rr:16 }, prescription:[{ medId:'MED-015', name:'Ibuprofen 400mg', dosage:'400mg', freq:'BD', duration:'5 days', instructions:'After meals with food' }], notes:'Papular erythematous rash — likely contact allergy. Advised to avoid soaps.', followUpDate: daysAhead(7), status:'completed' },
    { id:'OPD-003', patientId:'PAT-009', date: daysAgo(3), time:'09:00', doctorId:'DOC-003', site:'site-1', chiefComplaint:'Fever and right ear pain for 2 days', diagnosis:'Acute Otitis Media', icdCode:'H66.0', vitals:{ bp:'—', pulse:110, temp:38.6, weight:18, height:110, spo2:98, rr:24 }, prescription:[{ medId:'MED-001', name:'Amoxicillin 500mg', dosage:'250mg', freq:'BD', duration:'7 days', instructions:'With food' },{ medId:'MED-002', name:'Paracetamol 500mg', dosage:'250mg', freq:'TDS', duration:'3 days', instructions:'For fever/pain' }], notes:'Weight 18kg. Tympanic membrane red and bulging right side. Review in 2 weeks.', followUpDate: daysAhead(11), status:'completed' },
    { id:'OPD-004', patientId:'PAT-001', date: daysAgo(14), time:'10:30', doctorId:'DOC-001', site:'site-1', chiefComplaint:'Routine review — HTN and DM', diagnosis:'Hypertension (controlled) + Type 2 DM', icdCode:'I10; E11', vitals:{ bp:'138/88', pulse:72, temp:36.6, weight:78, height:160, spo2:99, rr:16 }, prescription:[{ medId:'MED-004', name:'Amlodipine 5mg', dosage:'5mg', freq:'OD', duration:'30 days', instructions:'Morning' },{ medId:'MED-012', name:'Losartan 50mg', dosage:'50mg', freq:'OD', duration:'30 days', instructions:'Morning' },{ medId:'MED-003', name:'Metformin 500mg', dosage:'500mg', freq:'BD', duration:'30 days', instructions:'After meals' }], notes:'BP slightly above target. Reinforced low-salt diet. Check HbA1c next visit.', followUpDate: daysAhead(16), status:'completed' },
  ];

  const SEED_IPD = [
    { id:'IPD-001', patientId:'PAT-003', admitDate: daysAgo(3), dischargeDate:'', ward:'Medical', bed:'M-04', doctorId:'DOC-002', admitDiagnosis:'COPD exacerbation with type 2 respiratory failure', finalDiagnosis:'', treatment:'IV hydrocortisone 200mg BD, Nebulised salbutamol 4-hrly, O2 via Venturi mask 28%', vitalsAdmission:{ bp:'148/92', pulse:108, temp:37.2, spo2:88, rr:28 }, notes:'Admitted from OPD. Improving on treatment.', status:'admitted', site:'site-1' },
    { id:'IPD-002', patientId:'PAT-010', admitDate: daysAgo(1), dischargeDate:'', ward:'Medical', bed:'M-07', doctorId:'DOC-002', admitDiagnosis:'Unstable angina', finalDiagnosis:'', treatment:'IV heparin infusion, Aspirin 300mg loading, GTN PRN, Bisoprolol 2.5mg', vitalsAdmission:{ bp:'162/98', pulse:94, temp:36.4, spo2:96, rr:18 }, notes:'Troponin mildly elevated. ECG: ST depression V4-V6. Cardiology referral pending.', status:'admitted', site:'site-1' },
  ];

  const SEED_SITES = [
    { id:'site-1', name:'Main Clinic', shortName:'Main', address:'25 Independence Ave, Lusaka', phone:'+260211200001', email:'main@medicore.zm', wards:['Medical','Surgical','Paediatric','Maternity'], beds:{ 'Medical':12, 'Surgical':8, 'Paediatric':6, 'Maternity':8 } },
    { id:'site-2', name:'North Branch Clinic', shortName:'North', address:'88 Great North Rd, Lusaka', phone:'+260211200002', email:'north@medicore.zm', wards:['General'], beds:{ 'General':8 } },
    { id:'site-3', name:'Mobile Health Unit', shortName:'Mobile', address:'Various locations', phone:'+260977009999', email:'mobile@medicore.zm', wards:[], beds:{} },
  ];

  const SEED_USERS = [
    { id:'USR-001', username:'admin', password:'admin123', name:'Admin User', role:'admin', staffId:'ADM-001', site:'site-1' },
    { id:'USR-002', username:'dr.sarah', password:'doc123', name:'Dr. Sarah Mulenga', role:'doctor', staffId:'DOC-001', site:'site-1' },
    { id:'USR-003', username:'dr.peter', password:'doc123', name:'Dr. Peter Zulu', role:'doctor', staffId:'DOC-002', site:'site-1' },
  ];

  const SEED_SETTINGS = {
    clinicName: 'MediCore Medical Centre',
    currency: 'ZMW',
    timezone: 'Africa/Lusaka',
    consultationFee: 150,
    aiApiKey: '',
    defaultSite: 'site-1',
  };

  // ---------- bootstrap ----------
  function bootstrap() {
    if (!read(KEYS.patients)) write(KEYS.patients, SEED_PATIENTS);
    if (!read(KEYS.staff)) write(KEYS.staff, SEED_STAFF);
    if (!read(KEYS.medications)) write(KEYS.medications, SEED_MEDS);
    if (!read(KEYS.chronicCases)) write(KEYS.chronicCases, SEED_CHRONIC);
    if (!read(KEYS.screenings)) write(KEYS.screenings, SEED_SCREENINGS);
    if (!read(KEYS.appointments)) write(KEYS.appointments, SEED_APPOINTMENTS);
    if (!read(KEYS.opdVisits)) write(KEYS.opdVisits, SEED_OPD);
    if (!read(KEYS.ipdAdmissions)) write(KEYS.ipdAdmissions, SEED_IPD);
    if (!read(KEYS.sites)) write(KEYS.sites, SEED_SITES);
    if (!read(KEYS.users)) write(KEYS.users, SEED_USERS);
    if (!read(KEYS.settings)) write(KEYS.settings, SEED_SETTINGS);
    if (!read(KEYS.medTransactions)) write(KEYS.medTransactions, []);
  }

  // ============ PATIENTS ============
  function getPatients() { return read(KEYS.patients) || []; }
  function getPatient(id) { return getPatients().find(p => p.id === id) || null; }
  function savePatient(patient) {
    const list = getPatients();
    if (!patient.id) {
      const next = list.length + 1;
      patient.id = `PAT-${String(next).padStart(3,'0')}`;
      patient.registrationDate = today();
      list.push(patient);
    } else {
      const idx = list.findIndex(p => p.id === patient.id);
      if (idx > -1) list[idx] = patient;
      else list.push(patient);
    }
    write(KEYS.patients, list);
    return patient;
  }
  function deletePatient(id) {
    write(KEYS.patients, getPatients().filter(p => p.id !== id));
  }
  function searchPatients(q) {
    if (!q) return [];
    const lq = q.toLowerCase();
    return getPatients().filter(p =>
      `${p.firstName} ${p.lastName}`.toLowerCase().includes(lq) ||
      p.id.toLowerCase().includes(lq) ||
      (p.phone || '').includes(q)
    ).slice(0, 8);
  }

  // ============ OPD ============
  function getOpdVisits(filters = {}) {
    let list = read(KEYS.opdVisits) || [];
    if (filters.patientId) list = list.filter(v => v.patientId === filters.patientId);
    if (filters.date) list = list.filter(v => v.date === filters.date);
    if (filters.site) list = list.filter(v => v.site === filters.site);
    if (filters.status) list = list.filter(v => v.status === filters.status);
    return list.sort((a,b) => b.date.localeCompare(a.date) || b.time.localeCompare(a.time));
  }
  function getOpdVisit(id) { return (read(KEYS.opdVisits) || []).find(v => v.id === id) || null; }
  function saveOpdVisit(visit) {
    const list = read(KEYS.opdVisits) || [];
    if (!visit.id) {
      visit.id = uid('OPD');
      list.push(visit);
    } else {
      const idx = list.findIndex(v => v.id === visit.id);
      if (idx > -1) list[idx] = visit; else list.push(visit);
    }
    write(KEYS.opdVisits, list);
    // deduct stock for prescriptions
    if (visit.prescription && visit.status === 'completed') {
      visit.prescription.forEach(rx => {
        if (rx.medId) adjustStock(rx.medId, -1, `Dispensed for ${visit.id}`);
      });
    }
    return visit;
  }

  // ============ IPD ============
  function getIpdAdmissions(filters = {}) {
    let list = read(KEYS.ipdAdmissions) || [];
    if (filters.patientId) list = list.filter(a => a.patientId === filters.patientId);
    if (filters.status) list = list.filter(a => a.status === filters.status);
    if (filters.site) list = list.filter(a => a.site === filters.site);
    return list.sort((a,b) => b.admitDate.localeCompare(a.admitDate));
  }
  function getIpdAdmission(id) { return (read(KEYS.ipdAdmissions) || []).find(a => a.id === id) || null; }
  function saveIpdAdmission(admission) {
    const list = read(KEYS.ipdAdmissions) || [];
    if (!admission.id) { admission.id = uid('IPD'); list.push(admission); }
    else { const idx = list.findIndex(a => a.id === admission.id); if (idx > -1) list[idx] = admission; else list.push(admission); }
    write(KEYS.ipdAdmissions, list);
    return admission;
  }

  // ============ APPOINTMENTS ============
  function getAppointments(filters = {}) {
    let list = read(KEYS.appointments) || [];
    if (filters.date) list = list.filter(a => a.date === filters.date);
    if (filters.patientId) list = list.filter(a => a.patientId === filters.patientId);
    if (filters.doctorId) list = list.filter(a => a.doctorId === filters.doctorId);
    if (filters.status) list = list.filter(a => a.status === filters.status);
    if (filters.site) list = list.filter(a => a.site === filters.site);
    return list.sort((a,b) => a.date.localeCompare(b.date) || a.time.localeCompare(b.time));
  }
  function saveAppointment(apt) {
    const list = read(KEYS.appointments) || [];
    if (!apt.id) { apt.id = uid('APT'); list.push(apt); }
    else { const idx = list.findIndex(a => a.id === apt.id); if (idx > -1) list[idx] = apt; else list.push(apt); }
    write(KEYS.appointments, list);
    return apt;
  }

  // ============ MEDICATIONS ============
  function getMedications(filters = {}) {
    let list = read(KEYS.medications) || [];
    if (filters.type) list = list.filter(m => m.type === filters.type);
    if (filters.siteId) list = list.filter(m => m.siteId === filters.siteId);
    return list.sort((a,b) => a.name.localeCompare(b.name));
  }
  function getMedication(id) { return getMedications().find(m => m.id === id) || null; }
  function saveMedication(med) {
    const list = read(KEYS.medications) || [];
    if (!med.id) { med.id = uid('MED'); list.push(med); }
    else { const idx = list.findIndex(m => m.id === med.id); if (idx > -1) list[idx] = med; else list.push(med); }
    write(KEYS.medications, list);
    return med;
  }
  function deleteMedication(id) { write(KEYS.medications, getMedications().filter(m => m.id !== id)); }
  function adjustStock(medId, qty, reason) {
    const meds = read(KEYS.medications) || [];
    const idx = meds.findIndex(m => m.id === medId);
    if (idx > -1) {
      meds[idx].stock = Math.max(0, (meds[idx].stock || 0) + qty);
      write(KEYS.medications, meds);
    }
    const tx = read(KEYS.medTransactions) || [];
    tx.push({ id: uid('TX'), medId, qty, reason, date: today(), time: new Date().toTimeString().slice(0,5) });
    write(KEYS.medTransactions, tx);
  }
  function getLowStockMeds() { return getMedications().filter(m => m.stock <= m.minStock); }

  // ============ CHRONIC ============
  function getChronicCases(filters = {}) {
    let list = read(KEYS.chronicCases) || [];
    if (filters.patientId) list = list.filter(c => c.patientId === filters.patientId);
    if (filters.condition) list = list.filter(c => c.condition === filters.condition);
    if (filters.status) list = list.filter(c => c.status === filters.status);
    return list.sort((a,b) => a.condition.localeCompare(b.condition));
  }
  function saveChronicCase(c) {
    const list = read(KEYS.chronicCases) || [];
    if (!c.id) { c.id = uid('CHR'); list.push(c); }
    else { const idx = list.findIndex(x => x.id === c.id); if (idx > -1) list[idx] = c; else list.push(c); }
    write(KEYS.chronicCases, list);
    return c;
  }

  // ============ SCREENINGS ============
  function getScreenings(filters = {}) {
    let list = read(KEYS.screenings) || [];
    if (filters.patientId) list = list.filter(s => s.patientId === filters.patientId);
    if (filters.site) list = list.filter(s => s.site === filters.site);
    return list.sort((a,b) => b.date.localeCompare(a.date));
  }
  function saveScreening(s) {
    const list = read(KEYS.screenings) || [];
    if (!s.id) { s.id = uid('SCR'); list.push(s); }
    else { const idx = list.findIndex(x => x.id === s.id); if (idx > -1) list[idx] = s; else list.push(s); }
    write(KEYS.screenings, list);
    return s;
  }

  // ============ STAFF ============
  function getStaff(role) {
    const list = read(KEYS.staff) || [];
    return role ? list.filter(s => s.role === role) : list;
  }
  function getStaffMember(id) { return getStaff().find(s => s.id === id) || null; }
  function saveStaff(member) {
    const list = read(KEYS.staff) || [];
    if (!member.id) { member.id = uid(member.role === 'doctor' ? 'DOC' : member.role === 'nurse' ? 'NRS' : 'STF'); list.push(member); }
    else { const idx = list.findIndex(s => s.id === member.id); if (idx > -1) list[idx] = member; else list.push(member); }
    write(KEYS.staff, list);
    return member;
  }

  // ============ SITES ============
  function getSites() { return read(KEYS.sites) || []; }
  function getSite(id) { return getSites().find(s => s.id === id) || null; }

  // ============ SETTINGS ============
  function getSettings() { return { ...SEED_SETTINGS, ...(read(KEYS.settings) || {}) }; }
  function saveSettings(s) { write(KEYS.settings, s); }

  // ============ AUTH ============
  function getUsers() { return read(KEYS.users) || []; }
  function authenticate(username, password) {
    return getUsers().find(u => u.username === username && u.password === password) || null;
  }

  // ============ STATS ============
  function getStats() {
    const t = today();
    return {
      totalPatients: getPatients().length,
      todayOPD: getOpdVisits({ date: t }).length,
      todayAppointments: getAppointments({ date: t }).length,
      activeIPD: getIpdAdmissions({ status: 'admitted' }).length,
      activeChronic: getChronicCases({ status: 'active' }).length,
      lowStock: getLowStockMeds().length,
      pendingScreenings: getScreenings().filter(s => s.status === 'abnormal' && !s.referredTo).length,
    };
  }

  // ---------- init ----------
  bootstrap();

  return {
    // patients
    getPatients, getPatient, savePatient, deletePatient, searchPatients,
    // opd
    getOpdVisits, getOpdVisit, saveOpdVisit,
    // ipd
    getIpdAdmissions, getIpdAdmission, saveIpdAdmission,
    // appointments
    getAppointments, saveAppointment,
    // medications
    getMedications, getMedication, saveMedication, deleteMedication, adjustStock, getLowStockMeds,
    // chronic
    getChronicCases, saveChronicCase,
    // screenings
    getScreenings, saveScreening,
    // staff
    getStaff, getStaffMember, saveStaff,
    // sites
    getSites, getSite,
    // settings
    getSettings, saveSettings,
    // auth
    authenticate,
    // stats
    getStats,
    // utils
    uid, today, daysAgo, daysAhead,
  };
})();
