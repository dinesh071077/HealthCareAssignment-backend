-- ============================================================
-- AI-First CRM Healthcare Professional Module
-- Sample SQL for MySQL / PostgreSQL
-- (SQLite is used by default — see backend/.env)
-- ============================================================

-- Doctors table
CREATE TABLE IF NOT EXISTS doctors (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            VARCHAR(255) NOT NULL,
    specialization  VARCHAR(255),
    hospital        VARCHAR(255)
);

-- Interactions table
CREATE TABLE IF NOT EXISTS interactions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id       INTEGER REFERENCES doctors(id),
    visit_date      DATE NOT NULL,
    visit_time      TIME,
    visit_type      VARCHAR(50) NOT NULL,
    purpose         TEXT,
    summary         TEXT NOT NULL,
    sentiment       VARCHAR(20) NOT NULL,
    products        JSON,
    follow_up_date  DATE,
    outcome         VARCHAR(100),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ── Sample Data ──────────────────────────────────────────────

INSERT INTO doctors (name, specialization, hospital) VALUES
  ('Dr. Rajesh Sharma', 'Cardiologist',     'Apollo Hospital Chennai'),
  ('Dr. Priya Patel',   'Neurologist',      'Fortis Hospital Bangalore'),
  ('Dr. Anil Rao',      'General Physician','Columbia Asia Hyderabad'),
  ('Dr. Meera Nair',    'Endocrinologist',  'Manipal Hospital Kochi'),
  ('Dr. Suresh Kumar',  'Pulmonologist',    'Max Hospital Delhi');

INSERT INTO interactions
  (doctor_id, visit_date, visit_type, purpose, summary, sentiment, products, follow_up_date, outcome)
VALUES
  (1, '2026-07-10', 'In-person', 'CardioPlus product launch',
   'Discussed benefits of CardioPlus for atrial fibrillation. Doctor showed strong interest and requested samples.',
   'Positive', '["CardioPlus","NeuroMax"]', '2026-07-24', 'Sample Requested'),

  (2, '2026-07-11', 'Phone', 'NeuroMax follow-up',
   'Doctor asked for clinical trial data. Neutral response, wants to review literature first.',
   'Neutral', '["NeuroMax"]', '2026-07-28', 'Follow-up Needed'),

  (3, '2026-07-12', 'In-person', 'DiabetiCare introduction',
   'Doctor currently using a competitor product. Not interested in switching.',
   'Negative', '["DiabetiCare"]', NULL, 'No Action'),

  (4, '2026-07-13', 'Video', 'OncoPrime awareness',
   'Detailed demo of OncoPrime. Doctor will discuss with department head.',
   'Positive', '["OncoPrime","ImmunBoost"]', '2026-07-27', 'Prescription Interest');
