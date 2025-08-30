-- USERS & SESSIONS
CREATE TABLE IF NOT EXISTS users (
  id            BIGINT PRIMARY KEY AUTO_INCREMENT,
  email         VARCHAR(255) NOT NULL UNIQUE,
  full_name     VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role          ENUM('doctor','assistant') NOT NULL DEFAULT 'assistant',
  is_active     TINYINT(1) NOT NULL DEFAULT 1,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS sessions (
  id            BIGINT PRIMARY KEY AUTO_INCREMENT,
  session_id    CHAR(36) NOT NULL UNIQUE,            -- UUIDv4
  user_id       BIGINT NOT NULL,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_seen_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at    DATETIME NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- CSV UPLOADS
CREATE TABLE IF NOT EXISTS csv_uploads (
  id            BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id       BIGINT,
  filename      VARCHAR(255) NOT NULL,
  rows_parsed   INT NOT NULL DEFAULT 0,
  rows_loaded   INT NOT NULL DEFAULT 0,
  status        ENUM('queued','processing','completed','failed') NOT NULL DEFAULT 'queued',
  error_msg     TEXT NULL,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- PATIENTS & OBSERVATIONS (Updated for heart disease dataset)
CREATE TABLE IF NOT EXISTS patients (
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT,
  patient_uid           VARCHAR(64) NOT NULL UNIQUE,
  patient_name          VARCHAR(255) NOT NULL,
  phone                 VARCHAR(32) NULL,
  age                   INT NOT NULL,
  sex                   ENUM('M','F','O') NOT NULL DEFAULT 'O',
  created_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_patients_age (age),
  INDEX idx_patients_sex (sex)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS patient_observations (
  id               BIGINT PRIMARY KEY AUTO_INCREMENT,
  patient_id       BIGINT NOT NULL,
  obs_type         VARCHAR(64) NOT NULL,
  value_num        DOUBLE NULL,
  value_text       VARCHAR(255) NULL,
  unit             VARCHAR(32) NULL,
  observed_at      DATETIME NOT NULL,
  source_upload_id BIGINT NULL,
  FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
  FOREIGN KEY (source_upload_id) REFERENCES csv_uploads(id) ON DELETE SET NULL,
  INDEX idx_patient_obs (patient_id, obs_type, observed_at),
  INDEX idx_obs_type (obs_type),
  INDEX idx_observed_at (observed_at)
) ENGINE=InnoDB;

-- HEART DISEASE VITAL SIGNS SUMMARY TABLE (for quick dashboard access)
CREATE TABLE IF NOT EXISTS patient_vitals_summary (
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT,
  patient_id            BIGINT NOT NULL,
  chest_pain_type       INT NULL,                    -- 0-3: typical angina, atypical angina, non-anginal pain, asymptomatic
  resting_bp            INT NULL,                    -- Resting blood pressure (mmHg)
  cholesterol           INT NULL,                    -- Serum cholesterol (mg/dl)
  fasting_bs            INT NULL,                    -- Fasting blood sugar > 120 mg/dl (1=true, 0=false)
  resting_ecg           INT NULL,                    -- Resting ECG results (0-2)
  max_heart_rate        INT NULL,                    -- Maximum heart rate achieved
  exercise_angina       INT NULL,                    -- Exercise induced angina (1=yes, 0=no)
  st_depression         DECIMAL(4,2) NULL,           -- ST depression induced by exercise
  st_slope              INT NULL,                    -- Slope of peak exercise ST segment (0-2)
  num_vessels           INT NULL,                    -- Number of major vessels colored by fluoroscopy
  thalassemia           INT NULL,                    -- Thalassemia (0-3)
  target                INT NULL,                    -- Heart disease (1=yes, 0=no)
  last_updated          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
  UNIQUE KEY unique_patient (patient_id),
  INDEX idx_vitals_target (target),
  INDEX idx_vitals_chest_pain (chest_pain_type),
  INDEX idx_vitals_bp (resting_bp),
  INDEX idx_vitals_cholesterol (cholesterol),
  INDEX idx_vitals_heart_rate (max_heart_rate)
) ENGINE=InnoDB;

-- NEW TABLE: PATIENT OUTCOMES AND RISK ASSESSMENT
CREATE TABLE IF NOT EXISTS patient_outcomes (
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT,
  patient_id            BIGINT NOT NULL,
  readmission           TINYINT(1) NULL,             -- 1=yes, 0=no
  complication          TINYINT(1) NULL,             -- 1=yes, 0=no
  mortality             TINYINT(1) NULL,             -- 1=yes, 0=no
  readmission_risk      ENUM('Low','Medium','High') NULL,
  complication_risk     ENUM('Low','Medium','High') NULL,
  mortality_risk        ENUM('Low','Medium','High') NULL,
  last_updated          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
  UNIQUE KEY unique_patient_outcome (patient_id),
  INDEX idx_outcomes_readmission (readmission),
  INDEX idx_outcomes_complication (complication),
  INDEX idx_outcomes_mortality (mortality),
  INDEX idx_outcomes_readmission_risk (readmission_risk),
  INDEX idx_outcomes_complication_risk (complication_risk),
  INDEX idx_outcomes_mortality_risk (mortality_risk)
) ENGINE=InnoDB;