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

-- PATIENTS & OBSERVATIONS (Updated for comprehensive healthcare data)
CREATE TABLE IF NOT EXISTS patients (
  id            BIGINT PRIMARY KEY AUTO_INCREMENT,
  patient_uid   VARCHAR(64) NOT NULL UNIQUE,
  first_name    VARCHAR(64) NOT NULL,
  last_name     VARCHAR(64) NOT NULL,
  age           INT NOT NULL,
  sex           ENUM('M','F','O') NOT NULL DEFAULT 'O',
  contact_phone VARCHAR(32) NULL,
  height_cm     DECIMAL(5,2) NULL,
  weight_kg     DECIMAL(5,2) NULL,
  bmi           DECIMAL(4,2) NULL,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
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

-- VITAL SIGNS SUMMARY TABLE (for quick dashboard access)
CREATE TABLE IF NOT EXISTS patient_vitals_summary (
  id               BIGINT PRIMARY KEY AUTO_INCREMENT,
  patient_id       BIGINT NOT NULL,
  bp_systolic      INT NULL,
  bp_diastolic     INT NULL,
  heart_rate       INT NULL,
  temperature      DECIMAL(4,1) NULL,
  oxygen_saturation DECIMAL(4,1) NULL,
  respiratory_rate INT NULL,
  cholesterol      DECIMAL(5,2) NULL,
  glucose          DECIMAL(5,2) NULL,
  bmi              DECIMAL(4,2) NULL,
  last_updated     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
  UNIQUE KEY unique_patient (patient_id)
) ENGINE=InnoDB;
